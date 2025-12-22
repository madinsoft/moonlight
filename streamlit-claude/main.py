from nicegui import ui, app
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import numpy as np

# ========================================
# 1. LOGIQUE METIER & DONNEES
# ========================================

def load_data():
    data_dir = Path("data")
    try:
        prod = pd.read_csv(data_dir / "production.csv", parse_dates=['timestamp'])
        cons = pd.read_csv(data_dir / "consumption.csv", parse_dates=['timestamp'])
        
        for df in [prod, cons]:
            if 'value' not in df.columns:
                col = [c for c in df.columns if 'kw' in c.lower() or 'value' in c.lower()][0]
                df['value'] = df[col]
            df['date'] = df['timestamp'].dt.date
            df['time'] = df['timestamp'].dt.strftime('%H:%M')
        return prod, cons
    except Exception as e:
        ui.notify(f"Erreur chargement: {e}", type='negative')
        return None, None

def simulate_battery_logic(production, consumption, capacity_kwh, time_step_hours=1/12):
    soc = capacity_kwh * 0.5
    max_soc = 0.95
    min_soc = 0.05
    battery_power = []
    battery_soc = []
    network_power = []
    
    for prod, cons in zip(production, consumption):
        net_power = prod - cons
        battery_soc.append((soc / capacity_kwh) * 100)
        
        if net_power > 0:
            max_charge = (capacity_kwh * max_soc - soc) / time_step_hours
            charge_power = min(net_power, max_charge)
            soc += charge_power * time_step_hours
            battery_power.append(-charge_power) 
            network_power.append(net_power - charge_power)
        else:
            max_discharge = (soc - capacity_kwh * min_soc) / time_step_hours
            discharge_power = min(-net_power, max_discharge)
            soc -= discharge_power * time_step_hours
            battery_power.append(discharge_power) 
            network_power.append(net_power + discharge_power)
        
        soc = max(capacity_kwh * min_soc, min(capacity_kwh * max_soc, soc))
    
    return battery_power, battery_soc, network_power

def calculate_stats(production, consumption, network):
    time_step = 1/12
    prod_total = sum(production) * time_step
    cons_total = sum(consumption) * time_step
    self_consumed = prod_total - sum(max(0, n) for n in network) * time_step
    self_consumption = (self_consumed / cons_total * 100) if cons_total > 0 else 0
    
    return {
        'prod': prod_total, 'cons': cons_total,
        'net': sum(network) * time_step, 'self': max(0, min(100, self_consumption))
    }

# ========================================
# 2. GENERATION SVG
# ========================================

def get_svg_diagram(prod, cons, bat, net):
    # Couleurs
    active, charge, inject, draw, inactive = "#3b82f6", "#8b5cf6", "#10b981", "#ef4444", "#4b5563"
    
    # États booléens
    is_solar = prod > 0.1
    is_char = bat < -0.1
    is_dis = bat > 0.1
    is_inj = net > 0.1
    is_draw = net < -0.1
    
    # Classes CSS pour animation
    c_sol = "flow-active" if is_solar else "flow-inactive"
    c_bat = "flow-charge" if is_char else ("flow-active" if is_dis else "flow-inactive")
    c_grd = "flow-inject" if is_inj else ("flow-draw" if is_draw else "flow-inactive")
    
    # --- COORDINATES ---
    # Solaire (Haut Gauche) : x=100
    # Réseau (Haut Droite)  : x=400
    # Batterie (Bas Gauche) : x=100 (Aligné sous solaire)
    # Maison (Bas Droite)   : x=350 (Décalé pour laisser de l'espace)
    
    svg = f"""
    <svg viewBox="0 0 600 350" xmlns="http://www.w3.org/2000/svg" style="width: 100%; height: 100%; background-color: #1e293b; border-radius: 0.5rem;">
        <defs>
            <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#94a3b8" /></marker>
        </defs>

        <path d="M 150 80 L 150 150 L 400 150 L 400 220" class="flow-line {c_sol}" stroke="{active if is_solar else inactive}" />
        
        <path d="M 150 80 L 150 220" class="flow-line {c_bat if is_char else 'flow-inactive'}" stroke="{charge if is_char else inactive}" />
        
        <path d="M 190 250 L 350 250" class="flow-line {c_bat if is_dis else 'flow-inactive'}" stroke="{charge if is_dis else inactive}" />
        
        <path d="M 450 80 L 450 150 L 400 150 L 400 220" class="flow-line {c_grd if is_inj else 'flow-inactive'}" stroke="{inject if is_inj else inactive}" />
        <path d="M 450 80 L 450 150 L 400 150 L 400 220" class="flow-line {c_grd if is_draw else 'flow-inactive'}" stroke="{draw if is_draw else inactive}" />


        <rect x="100" y="20" width="100" height="60" rx="8" fill="#0f172a" stroke="#334155" stroke-width="2"/>
        <text x="150" y="45" text-anchor="middle" fill="#3b82f6" font-size="24">☀️</text>
        <text x="150" y="70" text-anchor="middle" fill="#3b82f6" font-weight="bold">{prod:.1f} kW</text>
        
        <rect x="400" y="20" width="100" height="60" rx="8" fill="#0f172a" stroke="#334155" stroke-width="2"/>
        <text x="450" y="45" text-anchor="middle" fill="{inject if is_inj else (draw if is_draw else '#94a3b8')}" font-size="24">⚡</text>
        <text x="450" y="70" text-anchor="middle" fill="{inject if is_inj else (draw if is_draw else '#94a3b8')}" font-weight="bold">{abs(net):.1f} kW</text>

        <rect x="110" y="220" width="80" height="60" rx="8" fill="#0f172a" stroke="#334155" stroke-width="2"/>
        <text x="150" y="245" text-anchor="middle" fill="#8b5cf6" font-size="24">🔋</text>
        <text x="150" y="270" text-anchor="middle" fill="#8b5cf6" font-weight="bold">{abs(bat):.1f} kW</text>
        
        <rect x="350" y="220" width="100" height="80" rx="8" fill="#0f172a" stroke="#334155" stroke-width="2"/>
        <text x="400" y="255" text-anchor="middle" fill="#10b981" font-size="24">🏠</text>
        <text x="400" y="285" text-anchor="middle" fill="#10b981" font-weight="bold">{cons:.1f} kW</text>
        
    </svg>
    """
    return svg
# ========================================
# 3. INTERFACE NICEGUI
# ========================================

@ui.page('/')
def main_page():
    ui.add_head_html("""
    <style>
        body { background-color: #0f172a; color: #f3f4f6; }
        .card-dark { background-color: #1e293b; border: 1px solid #334155; border-radius: 0.5rem; padding: 1rem; }
        .metric-label { color: #94a3b8; font-size: 0.875rem; }
        .metric-value { color: white; font-size: 1.5rem; font-weight: bold; }
        .flow-line { fill: none; stroke-width: 3; stroke-dasharray: 10, 5; }
        @keyframes flow { to { stroke-dashoffset: -15; } }
        .flow-active { animation: flow 1s linear infinite; }
        .flow-inactive { stroke-dasharray: 5, 5; opacity: 0.3; }
        .flow-charge { stroke: #8b5cf6; animation: flow 1s linear infinite; }
        .flow-inject { stroke: #10b981; animation: flow 1s linear infinite; }
        .flow-draw { stroke: #ef4444; animation: flow 1s linear infinite; }
    </style>
    """)

    prod_df, cons_df = load_data()
    if prod_df is None: return

    dates = sorted(prod_df['date'].unique())
    date_options = {d: d.strftime('%d/%m/%Y') for d in dates}
    
    state = {'date': dates[-1], 'capacity': 500, 'time_idx': 0, 'data_len': 0}

    with ui.header().classes('bg-slate-900 border-b border-slate-700'):
        ui.label('☀️ Dashboard Solaire').classes('text-2xl font-bold text-white')

    with ui.left_drawer(value=True).classes('bg-slate-900 border-r border-slate-700 p-4'):
        ui.label('Paramètres').classes('text-xl font-bold mb-4 text-white')
        ui.label('Date').classes('text-gray-400 text-sm')
        date_select = ui.select(options=date_options, value=state['date']).classes('w-full mb-6').props('dark filled')
        ui.label('Capacité Batterie (kWh)').classes('text-gray-400 text-sm')
        cap_slider = ui.slider(min=0, max=1500, step=50, value=state['capacity']).classes('w-full mb-2')
        ui.label().bind_text_from(cap_slider, 'value', backward=lambda x: f"{x} kWh")
        
    with ui.column().classes('w-full p-4 gap-4'):
        # --- CARTES KPI ---
        with ui.grid(columns=4).classes('w-full gap-4'):
            with ui.column().classes('card-dark'):
                ui.label('Production').classes('metric-label')
                m_prod = ui.label('0 kWh').classes('metric-value text-blue-500')
            with ui.column().classes('card-dark'):
                ui.label('Consommation').classes('metric-label')
                m_cons = ui.label('0 kWh').classes('metric-value text-green-500')
            with ui.column().classes('card-dark'):
                ui.label('Réseau').classes('metric-label')
                m_net = ui.label('0 kWh').classes('metric-value')
            with ui.column().classes('card-dark'):
                ui.label('Autoconsommation').classes('metric-label')
                m_self = ui.label('0 %').classes('metric-value text-purple-500')

        # --- 4 GRAPHIQUES DISTINCTS ---
        with ui.grid(columns=2).classes('w-full gap-4'):
            # Production
            with ui.column().classes('card-dark'):
                ui.label('Production Solaire (kW)').classes('text-sm text-gray-400 mb-2')
                chart_solar = ui.plotly({}).classes('w-full h-60')
            
            # Consommation
            with ui.column().classes('card-dark'):
                ui.label('Consommation (kW)').classes('text-sm text-gray-400 mb-2')
                chart_cons = ui.plotly({}).classes('w-full h-60')
                
            # Réseau
            with ui.column().classes('card-dark'):
                ui.label('Réseau (kW) - (+ Injection / - Soutirage)').classes('text-sm text-gray-400 mb-2')
                chart_net = ui.plotly({}).classes('w-full h-60')
                
            # Batterie
            with ui.column().classes('card-dark'):
                ui.label('État Batterie (SOC %)').classes('text-sm text-gray-400 mb-2')
                chart_batt = ui.plotly({}).classes('w-full h-60')

        # --- DIAGRAMME FLUX ---
        with ui.column().classes('w-full card-dark mt-4'):
            ui.label("Flux Instantané").classes('text-lg font-bold mb-4')
            svg_container = ui.html('', sanitize=False).classes('w-full')
            with ui.row().classes('w-full items-center gap-4 mt-4'):
                ui.label('Heure:').classes('text-gray-400')
                time_slider = ui.slider(min=0, max=96, step=1, value=0).classes('flex-grow')
                time_label = ui.label('00:00').classes('w-16 font-mono text-white')

    # --- CONFIGURATION STYLE GRAPHIQUE ---
    def get_common_layout():
        return dict(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#9ca3af',
            margin=dict(l=30,r=10,t=10,b=30),
            xaxis=dict(
                showgrid=True, 
                gridwidth=1, 
                gridcolor='rgba(255, 255, 255, 0.2)', # Transparente à 20%
                griddash='dot' # Pointillée
            ),
            yaxis=dict(
                showgrid=True, 
                gridwidth=1, 
                gridcolor='rgba(255, 255, 255, 0.2)', 
                griddash='dot'
            )
        )

    def update_flow_diagram():
        idx = int(time_slider.value)
        if idx >= state['data_len']: idx = state['data_len'] - 1
        current_t = state['current_time'][idx]
        time_label.text = current_t
        p, c = state['current_prod'][idx], state['current_cons'][idx]
        b, n = state['current_bat'][idx], state['current_net'][idx]
        svg_container.content = get_svg_diagram(p, c, b, n)

    def update_dashboard():
        sel_date, sel_cap = date_select.value, cap_slider.value
        day_prod = prod_df[prod_df['date'] == sel_date].sort_values('timestamp')
        day_cons = cons_df[cons_df['date'] == sel_date].sort_values('timestamp')
        
        if len(day_prod) == 0: return

        vals_prod, vals_cons = day_prod['value'].tolist(), day_cons['value'].tolist()
        vals_time = day_prod['time'].tolist()
        
        state.update({'data_len': len(vals_prod), 'current_prod': vals_prod, 
                      'current_cons': vals_cons, 'current_time': vals_time})
        time_slider.props(f'max={len(vals_prod)-1}')
        
        bat_pow, bat_soc, net_pow = simulate_battery_logic(vals_prod, vals_cons, sel_cap)
        state.update({'current_bat': bat_pow, 'current_net': net_pow})
        
        # Stats
        stats = calculate_stats(vals_prod, vals_cons, net_pow)
        m_prod.text = f"{stats['prod']:.1f} kWh"
        m_cons.text = f"{stats['cons']:.1f} kWh"
        m_net.text = f"{abs(stats['net']):.1f} kWh"
        m_net.classes('text-green-500' if stats['net'] > 0 else 'text-red-500', remove='text-green-500 text-red-500')
        m_self.text = f"{stats['self']:.1f} %"
        
        layout = get_common_layout()
        
        # 1. Chart Solar
        fig_s = go.Figure(go.Scatter(x=vals_time, y=vals_prod, fill='tozeroy', line_color='#3b82f6'))
        fig_s.update_layout(**layout)
        chart_solar.update_figure(fig_s)
        
        # 2. Chart Cons
        fig_c = go.Figure(go.Scatter(x=vals_time, y=vals_cons, fill='tozeroy', line_color='#10b981'))
        fig_c.update_layout(**layout)
        chart_cons.update_figure(fig_c)
        
        # 3. Chart Net
        fig_n = go.Figure(go.Scatter(x=vals_time, y=net_pow, fill='tozeroy', line_color='#06b6d4')) # Cyan
        fig_n.update_layout(**layout)
        chart_net.update_figure(fig_n)
        
        # 4. Chart Battery SOC
        fig_b = go.Figure(go.Scatter(x=vals_time, y=bat_soc, fill='tozeroy', line_color='#8b5cf6')) # Violet
        fig_b.update_layout(**layout)
        fig_b.update_yaxes(range=[0, 100])
        chart_batt.update_figure(fig_b)
        
        update_flow_diagram()

    date_select.on_value_change(update_dashboard)
    cap_slider.on_value_change(update_dashboard)
    cap_slider.on('change', update_dashboard)
    time_slider.on_value_change(update_flow_diagram)

    update_dashboard()

ui.run(title='Dashboard Solaire', dark=True)