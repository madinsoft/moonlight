
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import numpy as np
import base64

# ========================================
# CONFIGURATION
# ========================================

st.set_page_config(
    page_title="Dashboard Solaire",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personnalisé
st.markdown("""
<style>
    .main { background-color: #0f172a; }
    .stMetric { background-color: #1e293b; padding: 1rem; border-radius: 0.5rem; }
    .stMetric label { color: #94a3b8 !important; }
    .stMetric [data-testid="stMetricValue"] { color: #ffffff !important; }
    h1, h2, h3 { color: #ffffff !important; }
    .stSelectbox label, .stSlider label { color: #94a3b8 !important; }
    
    .energy-flow-container {
        background-color: #1e293b;
        border-radius: 0.5rem;
        padding: 2rem;
        margin: 2rem 0;
    }
    
    .flow-arrow {
        stroke-width: 3;
        fill: none;
        marker-end: url(#arrowhead);
    }
    
    .flow-active {
        stroke: #3b82f6;
        filter: drop-shadow(0 0 4px #3b82f6);
        animation: flow 2s linear infinite;
    }
    
    .flow-charge {
        stroke: #8b5cf6;
        filter: drop-shadow(0 0 4px #8b5cf6);
    }
    
    .flow-discharge {
        stroke: #c084fc;
        filter: drop-shadow(0 0 4px #c084fc);
    }
    
    .flow-inject {
        stroke: #10b981;
        filter: drop-shadow(0 0 4px #10b981);
    }
    
    .flow-draw {
        stroke: #ef4444;
        filter: drop-shadow(0 0 4px #ef4444);
    }
    
    .flow-inactive {
        stroke: #4b5563;
        stroke-dasharray: 5,5;
    }
    
    @keyframes flow {
        from { stroke-dashoffset: 20; }
        to { stroke-dashoffset: 0; }
    }
    
    .energy-node {
        text-align: center;
    }
    
    .energy-value {
        color: #ffffff;
        font-size: 1.2rem;
        font-weight: bold;
        margin-top: 0.5rem;
    }
    
    .energy-label {
        color: #94a3b8;
        font-size: 0.875rem;
    }
</style>
""", unsafe_allow_html=True)

# ========================================
# FONCTIONS UTILITAIRES
# ========================================

def get_svg_icon(icon_name):
    """Charge une icône SVG et la convertit en base64"""
    icon_path = Path("assets/icons") / f"{icon_name}.svg"
    
    if icon_path.exists():
        with open(icon_path, "r", encoding="utf-8") as f:
            svg_content = f.read()
        return svg_content
    else:
        # Retourne une icône par défaut si le fichier n'existe pas
        default_icons = {
            "solar-panel": """
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                    <line x1="3" y1="9" x2="21" y2="9"/>
                    <line x1="3" y1="15" x2="21" y2="15"/>
                    <line x1="9" y1="3" x2="9" y2="21"/>
                    <line x1="15" y1="3" x2="15" y2="21"/>
                </svg>
            """,
            "battery": """
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="1" y="6" width="18" height="12" rx="2" ry="2"/>
                    <line x1="23" y1="10" x2="23" y2="14"/>
                    <line x1="5" y1="10" x2="13" y2="10"/>
                </svg>
            """,
            "house": """
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
                </svg>
            """,
            "grid": """
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                </svg>
            """
        }
        return default_icons.get(icon_name, "<svg></svg>")


def create_energy_flow_diagram(production_current, consumption_current, battery_power_current, network_current):
    """Crée un diagramme de flux d'énergie en SVG"""
    
    # Déterminer les flux actifs
    solar_to_house = production_current > 0 and consumption_current > 0
    solar_to_battery = battery_power_current < 0  # Charge
    battery_to_house = battery_power_current > 0  # Décharge
    house_to_grid = network_current > 0  # Injection
    grid_to_house = network_current < 0  # Soutirage
    
    svg_content = f"""
    <svg viewBox="0 0 600 400" xmlns="http://www.w3.org/2000/svg" style="width: 100%; height: 400px;">
        <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                <polygon points="0 0, 10 3, 0 6" fill="currentColor" />
            </marker>
        </defs>
        
        <!-- Background -->
        <rect width="600" height="400" fill="#1e293b" rx="8"/>
        
        <!-- Connections (fils) -->
        <!-- Solaire -> Maison -->
        <path d="M 150 80 L 150 120 L 300 120 L 300 180" 
              class="flow-arrow {'flow-active' if solar_to_house else 'flow-inactive'}"
              stroke-dasharray="10,5"/>
        
        <!-- Solaire -> Batterie -->
        <path d="M 150 80 L 150 200 L 200 200" 
              class="flow-arrow {'flow-charge' if solar_to_battery else 'flow-inactive'}"
              stroke-dasharray="10,5"/>
        
        <!-- Batterie -> Maison -->
        <path d="M 280 200 L 300 200" 
              class="flow-arrow {'flow-discharge' if battery_to_house else 'flow-inactive'}"
              stroke-dasharray="10,5"/>
        
        <!-- Maison -> Réseau (injection) -->
        <path d="M 350 200 L 450 200 L 450 140" 
              class="flow-arrow {'flow-inject' if house_to_grid else 'flow-inactive'}"
              stroke-dasharray="10,5"/>
        
        <!-- Réseau -> Maison (soutirage) -->
        <path d="M 450 100 L 450 60 L 300 60 L 300 180" 
              class="flow-arrow {'flow-draw' if grid_to_house else 'flow-inactive'}"
              stroke-dasharray="10,5"/>
        
        <!-- Icônes et valeurs -->
        
        <!-- Panneau Solaire (en haut à gauche) -->
        <g transform="translate(100, 20)">
            <rect width="100" height="60" fill="#0f172a" rx="8" stroke="#334155" stroke-width="2"/>
            <foreignObject x="20" y="5" width="60" height="50">
                <div xmlns="http://www.w3.org/1999/xhtml" style="color: #3b82f6; width: 60px; height: 50px;">
                    {get_svg_icon('solar-panel')}
                </div>
            </foreignObject>
        </g>
        <text x="150" y="100" text-anchor="middle" fill="#3b82f6" font-size="18" font-weight="bold">
            {production_current:.1f} kW
        </text>
        <text x="150" y="115" text-anchor="middle" fill="#94a3b8" font-size="12">Production</text>
        
        <!-- Batterie (à gauche au milieu) -->
        <g transform="translate(200, 170)">
            <rect width="80" height="60" fill="#0f172a" rx="8" stroke="#334155" stroke-width="2"/>
            <foreignObject x="10" y="5" width="60" height="50">
                <div xmlns="http://www.w3.org/1999/xhtml" style="color: #8b5cf6; width: 60px; height: 50px;">
                    {get_svg_icon('battery')}
                </div>
            </foreignObject>
        </g>
        <text x="240" y="250" text-anchor="middle" fill="#8b5cf6" font-size="18" font-weight="bold">
            {abs(battery_power_current):.1f} kW
        </text>
        <text x="240" y="265" text-anchor="middle" fill="#94a3b8" font-size="12">
            {'Charge' if battery_power_current < 0 else 'Décharge' if battery_power_current > 0 else 'Repos'}
        </text>
        
        <!-- Maison (au centre) -->
        <g transform="translate(250, 180)">
            <rect width="100" height="80" fill="#0f172a" rx="8" stroke="#334155" stroke-width="2"/>
            <foreignObject x="20" y="10" width="60" height="60">
                <div xmlns="http://www.w3.org/1999/xhtml" style="color: #10b981; width: 60px; height: 60px;">
                    {get_svg_icon('house')}
                </div>
            </foreignObject>
        </g>
        <text x="300" y="280" text-anchor="middle" fill="#10b981" font-size="18" font-weight="bold">
            {consumption_current:.1f} kW
        </text>
        <text x="300" y="295" text-anchor="middle" fill="#94a3b8" font-size="12">Consommation</text>
        
        <!-- Réseau (à droite) -->
        <g transform="translate(400, 80)">
            <rect width="100" height="60" fill="#0f172a" rx="8" stroke="#334155" stroke-width="2"/>
            <foreignObject x="20" y="5" width="60" height="50">
                <div xmlns="http://www.w3.org/1999/xhtml" 
                     style="color: {'#10b981' if network_current > 0 else '#ef4444' if network_current < 0 else '#94a3b8'}; width: 60px; height: 50px;">
                    {get_svg_icon('grid')}
                </div>
            </foreignObject>
        </g>
        <text x="450" y="160" text-anchor="middle" 
              fill="{'#10b981' if network_current > 0 else '#ef4444' if network_current < 0 else '#94a3b8'}" 
              font-size="18" font-weight="bold">
            {abs(network_current):.1f} kW
        </text>
        <text x="450" y="175" text-anchor="middle" fill="#94a3b8" font-size="12">
            {'Injection' if network_current > 0 else 'Soutirage' if network_current < 0 else 'Équilibre'}
        </text>
    </svg>
    """
    
    return svg_content


@st.cache_data
def load_csv_data():
    """Charge et prépare les données CSV"""
    data_path = Path("data")
    
    production_df = pd.read_csv(data_path / "production.csv")
    consumption_df = pd.read_csv(data_path / "consumption.csv")
    
    production_df['timestamp'] = pd.to_datetime(production_df['timestamp'])
    consumption_df['timestamp'] = pd.to_datetime(consumption_df['timestamp'])
    
    for df in [production_df, consumption_df]:
        df['date'] = df['timestamp'].dt.date
        df['time'] = df['timestamp'].dt.strftime('%H:%M')
    
    return production_df, consumption_df


def get_date_data(df, selected_date, value_col):
    """Filtre les données pour une date spécifique"""
    filtered = df[df['date'] == selected_date].copy()
    filtered = filtered.sort_values('timestamp')
    return filtered['time'].tolist(), filtered[value_col].tolist()


def simulate_battery(production, consumption, capacity_kwh, time_step_hours=1/12):
    """Simule le comportement d'une batterie"""
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
    """Calcule les statistiques agrégées"""
    time_step = 1/12
    
    prod_total = sum(production) * time_step
    cons_total = sum(consumption) * time_step
    
    network_balance = sum(network) * time_step
    
    injected = sum(max(0, n) for n in network) * time_step
    self_consumed = prod_total - injected
    self_consumption = (self_consumed / cons_total * 100) if cons_total > 0 else 0
    
    return {
        'production_total': prod_total,
        'consumption_total': cons_total,
        'network_balance': network_balance,
        'self_consumption': max(0, min(100, self_consumption))
    }


def create_chart(times, data, title, color, fill=False, yaxis_range=None, yaxis_title="Puissance (kW)"):
    """Crée un graphique Plotly standardisé"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=times,
        y=data,
        mode='lines',
        name=title,
        line=dict(color=color, width=2),
        fill='tozeroy' if fill else None,
        fillcolor=f'rgba{tuple(list(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.2])}' if fill else None
    ))
    
    yaxis_config = dict(
        gridcolor='#334155',
        title=yaxis_title
    )
    if yaxis_range:
        yaxis_config['range'] = yaxis_range
    
    fig.update_layout(
        title=dict(text=title, font=dict(color='#ffffff', size=16)),
        paper_bgcolor='#1e293b',
        plot_bgcolor='#0f172a',
        font=dict(color='#94a3b8'),
        xaxis=dict(
            gridcolor='#334155',
            title="Heure",
            tickformat='%H:%M'
        ),
        yaxis=yaxis_config,
        height=300,
        margin=dict(l=50, r=20, t=40, b=40),
        hovermode='x unified'
    )
    
    return fig


def create_network_chart(times, network, battery_power):
    """Crée un graphique pour les flux réseau et batterie"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=times,
        y=network,
        mode='lines',
        name='Réseau',
        line=dict(color='#10b981', width=2),
        fill='tozeroy'
    ))
    
    if any(bp != 0 for bp in battery_power):
        fig.add_trace(go.Scatter(
            x=times,
            y=battery_power,
            mode='lines',
            name='Batterie',
            line=dict(color='#8b5cf6', width=2, dash='dash')
        ))
    
    fig.update_layout(
        title=dict(text="Flux Réseau et Batterie", font=dict(color='#ffffff', size=16)),
        paper_bgcolor='#1e293b',
        plot_bgcolor='#0f172a',
        font=dict(color='#94a3b8'),
        xaxis=dict(gridcolor='#334155', title="Heure"),
        yaxis=dict(gridcolor='#334155', title="Puissance (kW)", zeroline=True, zerolinecolor='#64748b'),
        height=300,
        margin=dict(l=50, r=20, t=40, b=40),
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def render_metrics(stats):
    """Affiche les 4 métriques principales"""
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = [
        (col1, "☀️ Production Solaire", f"{stats['production_total']:.1f} kWh", "blue"),
        (col2, "🏠 Consommation", f"{stats['consumption_total']:.1f} kWh", "green"),
        (col3, "⚡ Réseau", 
         f"{'↑' if stats['network_balance'] > 0 else '↓'} {abs(stats['network_balance']):.1f} kWh",
         "green" if stats['network_balance'] > 0 else "red"),
        (col4, "🔄 Autoconsommation", f"{stats['self_consumption']:.1f} %", "purple")
    ]
    
    for col, label, value, _ in metrics:
        with col:
            st.metric(label=label, value=value)


# ========================================
# APPLICATION PRINCIPALE
# ========================================

def main():
    st.title("☀️ Dashboard Solaire")
    st.markdown("Visualisation de production et consommation énergétique")
    
    # Chargement des données
    production_df, consumption_df = load_csv_data()
    
    # Obtenir les dates disponibles
    available_dates = sorted(production_df['date'].unique())
    
    # Contrôles dans la sidebar
    with st.sidebar:
        st.header("⚙️ Paramètres")
        
        selected_date = st.selectbox(
            "📅 Date",
            options=available_dates,
            format_func=lambda d: d.strftime('%d/%m/%Y')
        )
        
        battery_capacity = st.slider(
            "🔋 Capacité Batterie (kWh)",
            min_value=0,
            max_value=1500,
            value=500,
            step=50
        )
        
        st.markdown("---")
        st.markdown("### 📊 Légende des flux")
        st.markdown("🔵 **Bleu** : Production solaire")
        st.markdown("🟣 **Violet** : Batterie (charge/décharge)")
        st.markdown("🟢 **Vert** : Injection réseau")
        st.markdown("🔴 **Rouge** : Soutirage réseau")
    
    # Récupération des données
    times_prod, production = get_date_data(production_df, selected_date, 'production_kw')
    times_cons, consumption = get_date_data(consumption_df, selected_date, 'consumption_kw')
    
    # Simulation batterie
    battery_power, battery_soc, network = simulate_battery(
        production, consumption, battery_capacity
    )
    
    # Calcul des statistiques
    stats = calculate_stats(production, consumption, network)
    
    # Affichage des métriques
    render_metrics(stats)
    
    st.markdown("---")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        fig_prod = create_chart(times_prod, production, "Production Solaire", "#3b82f6", fill=True)
        st.plotly_chart(fig_prod, use_container_width=True)
        
        fig_network = create_network_chart(times_prod, network, battery_power)
        st.plotly_chart(fig_network, use_container_width=True)
    
    with col2:
        fig_cons = create_chart(times_cons, consumption, "Consommation Quartier", "#10b981", fill=True)
        st.plotly_chart(fig_cons, use_container_width=True)
        
        if battery_capacity > 0:
            fig_soc = create_chart(
                times_prod, 
                battery_soc, 
                "État de Charge Batterie (%)", 
                "#8b5cf6", 
                fill=True,
                yaxis_range=[0, 100],
                yaxis_title="État de charge (%)"
            )
            st.plotly_chart(fig_soc, use_container_width=True)
    
    # Diagramme de flux d'énergie
    st.markdown("---")
    st.markdown("### 🔄 Diagramme de Flux d'Énergie")
    
    # Obtenir les valeurs moyennes pour le diagramme
    if len(production) > 0:
        mid_index = len(production) // 2
        prod_current = production[mid_index]
        cons_current = consumption[mid_index]
        bat_current = battery_power[mid_index]
        net_current = network[mid_index]
        
        # Afficher le diagramme SVG
        energy_diagram = create_energy_flow_diagram(
            prod_current, cons_current, bat_current, net_current
        )
        st.markdown(energy_diagram, unsafe_allow_html=True)
        
        # Slider pour naviguer dans le temps
        st.markdown("---")
        time_index = st.slider(
            "⏰ Sélectionner l'heure",
            min_value=0,
            max_value=len(times_prod) - 1,
            value=mid_index,
            format=times_prod[mid_index] if mid_index < len(times_prod) else "00:00"
        )
        
        # Mettre à jour le diagramme avec l'heure sélectionnée
        energy_diagram_current = create_energy_flow_diagram(
            production[time_index],
            consumption[time_index],
            battery_power[time_index],
            network[time_index]
        )
        st.markdown(f"**Flux à {times_prod[time_index]}**")
        st.markdown(energy_diagram_current, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"<p style='text-align: center; color: #64748b;'>Date sélectionnée: {selected_date.strftime('%d/%m/%Y')} | "
        f"Capacité batterie: {battery_capacity} kWh</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
