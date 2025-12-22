import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import numpy as np

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
</style>
""", unsafe_allow_html=True)

# ========================================
# FONCTIONS UTILITAIRES
# ========================================

@st.cache_data
def load_csv_data():
    """Charge et prépare les données CSV"""
    data_path = Path("data")
    
    # Chargement des fichiers
    production_df = pd.read_csv(data_path / "production.csv")
    consumption_df = pd.read_csv(data_path / "consumption.csv")
    
    # Conversion des timestamps
    production_df['timestamp'] = pd.to_datetime(production_df['timestamp'])
    consumption_df['timestamp'] = pd.to_datetime(consumption_df['timestamp'])
    
    # Extraction de la date et l'heure
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
    """
    Simule le comportement d'une batterie
    Returns: battery_power, battery_soc, network_power
    """
    soc = capacity_kwh * 0.5  # Commence à 50%
    max_soc = 0.95
    min_soc = 0.05
    
    battery_power = []
    battery_soc = []
    network_power = []
    
    for prod, cons in zip(production, consumption):
        net_power = prod - cons
        
        # Enregistrer le SoC avant l'action
        soc_pct = (soc / capacity_kwh) * 100
        battery_soc.append(soc_pct)
        
        if capacity_kwh == 0:
            battery_power.append(0)
            network_power.append(net_power)
            continue
        
        if net_power > 0:  # Excédent -> Charger
            max_charge = (capacity_kwh * max_soc - soc) / time_step_hours
            charge = min(net_power, max_charge)
            battery_power.append(-charge)  # Négatif = charge
            soc += charge * time_step_hours
            network_power.append(net_power - charge)
            
        else:  # Déficit -> Décharger
            max_discharge = (soc - capacity_kwh * min_soc) / time_step_hours
            discharge = min(abs(net_power), max_discharge)
            battery_power.append(discharge)  # Positif = décharge
            soc -= discharge * time_step_hours
            network_power.append(net_power + discharge)
    
    return battery_power, battery_soc, network_power


def calculate_stats(production, consumption, network):
    """Calcule les statistiques journalières"""
    time_step = 1/12  # 5 minutes en heures
    
    prod_total = sum(production) * time_step
    cons_total = sum(consumption) * time_step
    net_balance = sum(network) * time_step
    
    # Autoconsommation
    total_injected = sum(max(0, n) for n in network) * time_step
    self_consumed = prod_total - total_injected
    self_consumption_pct = (self_consumed / cons_total * 100) if cons_total > 0 else 0
    
    return {
        'production': {'total': prod_total, 'max': max(production)},
        'consumption': {'total': cons_total, 'max': max(consumption)},
        'network': {'balance': net_balance},
        'self_consumption': max(0, min(100, self_consumption_pct))
    }


def create_chart(times, data, title, color, fill=False):
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
        yaxis=dict(
            gridcolor='#334155',
            title="Puissance (kW)"
        ),
        height=300,
        margin=dict(l=50, r=20, t=40, b=40),
        hovermode='x unified'
    )
    
    return fig


def create_network_chart(times, network_data, battery_data):
    """Crée le graphique réseau + batterie"""
    fig = go.Figure()
    
    # Batterie
    fig.add_trace(go.Scatter(
        x=times,
        y=battery_data,
        mode='lines',
        name='Batterie',
        line=dict(color='#8b5cf6', width=2),
        fill='tozeroy',
        fillcolor='rgba(139, 92, 246, 0.2)'
    ))
    
    # Réseau avec couleurs conditionnelles
    colors = ['#10b981' if n >= 0 else '#ef4444' for n in network_data]
    
    fig.add_trace(go.Scatter(
        x=times,
        y=network_data,
        mode='lines',
        name='Réseau',
        line=dict(color='#4ade80', width=2),
        marker=dict(color=colors)
    ))
    
    fig.update_layout(
        title=dict(text="Réseau & Batterie", font=dict(color='#ffffff', size=16)),
        paper_bgcolor='#1e293b',
        plot_bgcolor='#0f172a',
        font=dict(color='#94a3b8'),
        xaxis=dict(gridcolor='#334155', title="Heure"),
        yaxis=dict(gridcolor='#334155', title="Puissance (kW)"),
        height=300,
        margin=dict(l=50, r=20, t=40, b=40),
        hovermode='x unified',
        showlegend=True
    )
    
    return fig


def render_metrics(stats):
    """Affiche les métriques dans 4 colonnes"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "☀️ Production Totale",
            f"{stats['production']['total']:.1f} kWh",
            f"Max: {stats['production']['max']:.1f} kW"
        )
    
    with col2:
        st.metric(
            "🏠 Consommation Totale",
            f"{stats['consumption']['total']:.1f} kWh",
            f"Max: {stats['consumption']['max']:.1f} kW"
        )
    
    with col3:
        balance = stats['network']['balance']
        delta_label = f"{abs(balance):.1f} kWh {'injectés' if balance > 0 else 'soutirés'}"
        st.metric(
            "⚡ Bilan Réseau",
            f"{balance:.1f} kWh",
            delta_label,
            delta_color="normal" if balance > 0 else "inverse"
        )
    
    with col4:
        st.metric(
            "📊 Autoconsommation",
            f"{stats['self_consumption']:.0f}%",
            "Part produite consommée"
        )


# ========================================
# APPLICATION PRINCIPALE
# ========================================

def main():
    # Header
    st.markdown("### ☀️ Dashboard Solaire - Quartier Résidentiel")
    
    # Chargement des données
    with st.spinner("Chargement des données..."):
        production_df, consumption_df = load_csv_data()
    
    # Dates disponibles
    available_dates = sorted(production_df['date'].unique())
    
    # Interface de contrôle
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_date = st.selectbox(
            "📅 Sélectionner une date",
            options=available_dates,
            index=len(available_dates) // 2,
            format_func=lambda x: x.strftime('%d/%m/%Y')
        )
    
    with col2:
        battery_capacity = st.slider(
            "🔋 Capacité batterie (kWh)",
            min_value=0,
            max_value=1500,
            value=500,
            step=50
        )
    
    st.markdown("---")
    
    # Traitement des données
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
            fig_soc = create_chart(times_prod, battery_soc, "État de Charge Batterie (%)", "#8b5cf6", fill=True)
            fig_soc.update_layout(yaxis=dict(title="État de charge (%)", range=[0, 100]))
            st.plotly_chart(fig_soc, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"<p style='text-align: center; color: #64748b;'>Date sélectionnée: {selected_date.strftime('%d/%m/%Y')} | "
        f"Capacité batterie: {battery_capacity} kWh</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()