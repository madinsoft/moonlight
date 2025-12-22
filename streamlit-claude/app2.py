import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime, timedelta
import numpy as np

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Moonlight Energy Dashboard",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS PERSONNALISÉ ---
st.markdown("""
<style>
    .main {
        background-color: #0f1419;
        color: #f3f4f6;
    }
    .stApp {
        background-color: #0f1419;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #ffffff;
    }
    div[data-testid="stMetricLabel"] {
        color: #9ca3af;
    }
    .card {
        background-color: #1a1f2e;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #2d3748;
        height: 100%;
    }
    h1, h2, h3 {
        color: #ffffff;
    }
    .stSelectbox label, .stSlider label {
        color: #9ca3af !important;
    }
    /* Correction pour l'affichage des graphiques */
    .js-plotly-plot .plotly .modebar {
        orientation: v;
        right: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. FONCTIONS UTILITAIRES ---
@st.cache_data
def load_csv_data(file_path):
    """Charge les données CSV avec gestion d'erreurs."""
    try:
        df = pd.read_csv(file_path)
        # On s'assure que les colonnes existent
        if 'timestamp' not in df.columns or 'value' not in df.columns:
            st.error(f"Le fichier {file_path} doit contenir les colonnes 'timestamp' et 'value'.")
            return None
            
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        df['time'] = df['timestamp'].dt.strftime('%H:%M')
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement de {file_path}: {e}")
        return None

def simulate_battery(production, consumption, battery_capacity_kwh):
    """Simule le comportement de la batterie et les flux réseau."""
    time_step_hours = 0.25 # Données supposées en pas de 15 min
    min_soc = 0.10
    max_soc = 0.80 # On ne charge pas au delà de 80% pour la simulation
    
    # État initial de la batterie (50%)
    battery_soc_kwh = battery_capacity_kwh * 0.50
    
    battery_power = []
    battery_soc = []
    network_power = []
    
    for prod, cons in zip(production, consumption):
        net_power = prod - cons # Surplus (+) ou Besoin (-)
        
        if net_power > 0:
            # Surplus: charger la batterie
            available_capacity = (max_soc * battery_capacity_kwh) - battery_soc_kwh
            # Puissance max acceptée par la batterie pour ce pas de temps
            max_charge_power = available_capacity / time_step_hours
            
            charge_power = min(net_power, max_charge_power)
            
            battery_soc_kwh += charge_power * time_step_hours
            battery_power.append(charge_power) # Positif = Charge
            
            network_surplus = net_power - charge_power
            network_power.append(network_surplus) # Positif = Injection
        else:
            # Déficit: décharger la batterie
            deficit = abs(net_power)
            available_discharge = battery_soc_kwh - (min_soc * battery_capacity_kwh)
            
            if available_discharge < 0: available_discharge = 0
            
            max_discharge_power = available_discharge / time_step_hours
            discharge_power = min(deficit, max_discharge_power)
            
            battery_soc_kwh -= discharge_power * time_step_hours
            battery_power.append(-discharge_power) # Négatif = Décharge
            
            network_deficit = deficit - discharge_power
            network_power.append(-network_deficit) # Négatif = Soutirage
        
        battery_soc.append((battery_soc_kwh / battery_capacity_kwh) * 100)
    
    return battery_power, battery_soc, network_power

def calculate_daily_stats(production, consumption, network, time_step=0.25):
    """Calcule les statistiques globales pour la journée."""
    production_total = sum(production) * time_step
    consumption_total = sum(consumption) * time_step
    
    production_max = max(production) if production else 0
    consumption_max = max(consumption) if consumption else 0
    
    network_balance = sum(network) * time_step
    
    # Autoconsommation : (Prod Total - Injection Réseau) / Consommation Totale
    total_injected = sum([n for n in network if n > 0]) * time_step
    self_consumed = production_total - total_injected
    
    if consumption_total > 0:
        self_consumption_pct = (self_consumed / consumption_total * 100)
    else:
        self_consumption_pct = 0
    
    return {
        'production_total': production_total,
        'production_max': production_max,
        'consumption_total': consumption_total,
        'consumption_max': consumption_max,
        'network_balance': network_balance,
        'self_consumption': max(0, min(100, self_consumption_pct))
    }

# --- 4. INTERFACE PRINCIPALE ---
def main():
    # Header
    st.markdown("""
        <div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); 
                    padding: 2rem; border-radius: 12px; margin-bottom: 2rem;'>
            <h1 style='margin: 0; display: flex; align-items: center; color: white;'>
                🌙 Moonlight Energy Dashboard
            </h1>
            <p style='color: #94a3b8; margin-top: 0.5rem;'>
                Visualisation et simulation de production solaire et consommation énergétique
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # --- Vérification et Création des Dossiers ---
    # Utilisation de chemins relatifs pour la compatibilité locale
    data_dir = 'data'
    production_path = os.path.join(data_dir, 'production.csv')
    consumption_path = os.path.join(data_dir, 'consumption.csv')
    
    if not os.path.exists(production_path) or not os.path.exists(consumption_path):
        st.error(f"""
        ⚠️ **Fichiers de données manquants**
        
        Le programme cherche les fichiers ici :
        - `{os.path.abspath(production_path)}`
        - `{os.path.abspath(consumption_path)}`
        
        Veuillez créer un dossier nommé `data` à côté de ce script et y placer vos fichiers CSV.
        """)
        
        # Tentative de création du dossier
        try:
            os.makedirs(data_dir, exist_ok=True)
            st.info(f"✅ Le dossier '{data_dir}' a été créé. Copiez vos fichiers CSV dedans et rafraîchissez la page.")
        except Exception as e:
            st.error(f"Impossible de créer le dossier automatiquement : {e}")
        return
    
    # --- Chargement ---
    with st.spinner('Chargement des données...'):
        production_df = load_csv_data(production_path)
        consumption_df = load_csv_data(consumption_path)
    
    if production_df is None or consumption_df is None:
        return
    
    # --- Sidebar ---
    with st.sidebar:
        st.markdown("### ⚙️ Paramètres")
        
        available_dates = sorted(production_df['date'].unique())
        selected_date = st.selectbox(
            "📅 Date",
            available_dates,
            index=len(available_dates)-1 if available_dates else 0
        )
        
        battery_capacity = st.slider(
            "🔋 Capacité batterie (kWh)",
            min_value=10,
            max_value=1000,
            value=100,
            step=10
        )
        
        st.markdown("---")
        st.caption("Données sources : data/*.csv")
    
    # --- Filtrage ---
    prod_day = production_df[production_df['date'] == selected_date].copy()
    cons_day = consumption_df[consumption_df['date'] == selected_date].copy()
    
    if prod_day.empty or cons_day.empty:
        st.warning(f"Aucune donnée disponible pour le {selected_date}")
        return
    
    # Préparation des listes
    production_values = prod_day['value'].tolist()
    consumption_values = cons_day['value'].tolist()
    time_labels = prod_day['time'].tolist()
    
    # --- Simulation ---
    battery_power, battery_soc, network_power = simulate_battery(
        production_values, consumption_values, battery_capacity
    )
    
    stats = calculate_daily_stats(production_values, consumption_values, network_power)
    
    # --- Affichage des KPIs (Cartes) ---
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='card'>
            <div style='color: #fbbf24; font-size: 2.5rem; margin-bottom: 0.5rem;'>☀️</div>
            <div style='font-size: 1.8rem; font-weight: bold; color: white;'>
                {stats['production_total']:.1f} <span style='font-size: 1rem;'>kWh</span>
            </div>
            <div style='color: #9ca3af; margin-top: 0.5rem;'>Production Solaire</div>
            <div style='color: #6b7280; font-size: 0.85rem; margin-top: 0.25rem;'>
                Max: {stats['production_max']:.1f} kW
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='card'>
            <div style='color: #8b5cf6; font-size: 2.5rem; margin-bottom: 0.5rem;'>🏠</div>
            <div style='font-size: 1.8rem; font-weight: bold; color: white;'>
                {stats['consumption_total']:.1f} <span style='font-size: 1rem;'>kWh</span>
            </div>
            <div style='color: #9ca3af; margin-top: 0.5rem;'>Consommation</div>
            <div style='color: #6b7280; font-size: 0.85rem; margin-top: 0.25rem;'>
                Max: {stats['consumption_max']:.1f} kW
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        net_bal = stats['network_balance']
        network_color = "#ef4444" if net_bal < 0 else "#10b981"
        network_icon = "⚡" if net_bal < 0 else "↗️"
        network_text = "soutiré" if net_bal < 0 else "injecté"
        
        st.markdown(f"""
        <div class='card'>
            <div style='color: {network_color}; font-size: 2.5rem; margin-bottom: 0.5rem;'>{network_icon}</div>
            <div style='font-size: 1.8rem; font-weight: bold; color: white;'>
                {abs(net_bal):.1f} <span style='font-size: 1rem;'>kWh</span>
            </div>
            <div style='color: #9ca3af; margin-top: 0.5rem;'>Réseau</div>
            <div style='color: #6b7280; font-size: 0.85rem; margin-top: 0.25rem;'>
                {network_text} du réseau
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='card'>
            <div style='color: #3b82f6; font-size: 2.5rem; margin-bottom: 0.5rem;'>📊</div>
            <div style='font-size: 1.8rem; font-weight: bold; color: white;'>
                {stats['self_consumption']:.0f} <span style='font-size: 1rem;'>%</span>
            </div>
            <div style='color: #9ca3af; margin-top: 0.5rem;'>Autoconsommation</div>
            <div style='color: #6b7280; font-size: 0.85rem; margin-top: 0.25rem;'>
                Ratio Prod/Conso
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- Graphiques (Tabs) ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Production", 
        "🏠 Consommation", 
        "⚡ Réseau", 
        "🔋 Batterie"
    ])
    
    # Configuration commune pour les graphiques
    common_layout = dict(
        paper_bgcolor='#1a1f2e',
        plot_bgcolor='#1a1f2e',
        font=dict(color='#9ca3af'),
        xaxis=dict(gridcolor='rgba(45, 55, 72, 0.5)', showgrid=True),
        yaxis=dict(gridcolor='rgba(45, 55, 72, 0.5)', showgrid=True),
        hovermode='x unified',
        margin=dict(l=60, r=20, t=40, b=40)
    )

    with tab1:
        fig_prod = go.Figure()
        fig_prod.add_trace(go.Scatter(
            x=time_labels, y=production_values,
            fill='tozeroy', name='Production',
            line=dict(color='#fbbf24', width=2),
            fillcolor='rgba(251, 191, 36, 0.2)'
        ))
        fig_prod.update_layout(title="Production Solaire (kW)", **common_layout)
        st.plotly_chart(fig_prod, use_container_width=True)
    
    with tab2:
        fig_cons = go.Figure()
        fig_cons.add_trace(go.Scatter(
            x=time_labels, y=consumption_values,
            fill='tozeroy', name='Consommation',
            line=dict(color='#8b5cf6', width=2),
            fillcolor='rgba(139, 92, 246, 0.2)'
        ))
        fig_cons.update_layout(title="Consommation Maison (kW)", **common_layout)
        st.plotly_chart(fig_cons, use_container_width=True)
    
    with tab3:
        colors = ['#10b981' if v > 0 else '#ef4444' for v in network_power]
        fig_net = go.Figure()
        fig_net.add_trace(go.Bar(
            x=time_labels, y=network_power,
            name='Réseau', marker=dict(color=colors)
        ))
        fig_net.update_layout(title="Flux Réseau (kW) - Positif = Injection", **common_layout)
        st.plotly_chart(fig_net, use_container_width=True)
    
    with tab4:
        # Subplots pour la batterie
        fig_bat = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Puissance Batterie (kW)', 'État de Charge (%)'),
            vertical_spacing=0.2,
            row_heights=[0.5, 0.5]
        )
        
        # Puissance
        bat_colors = ['#10b981' if v > 0 else '#ef4444' for v in battery_power]
        fig_bat.add_trace(
            go.Bar(x=time_labels, y=battery_power, name='Puissance', marker=dict(color=bat_colors)),
            row=1, col=1
        )
        
        # SOC
        fig_bat.add_trace(
            go.Scatter(x=time_labels, y=battery_soc, name='SOC', 
                      fill='tozeroy', line=dict(color='#3b82f6', width=2),
                      fillcolor='rgba(59, 130, 246, 0.2)'),
            row=2, col=1
        )
        
        # Layout spécifique pour subplots
        fig_bat.update_layout(height=600, **common_layout)
        fig_bat.update_xaxes(gridcolor='rgba(45, 55, 72, 0.5)', row=1, col=1)
        fig_bat.update_xaxes(gridcolor='rgba(45, 55, 72, 0.5)', row=2, col=1)
        fig_bat.update_yaxes(gridcolor='rgba(45, 55, 72, 0.5)', row=1, col=1)
        fig_bat.update_yaxes(gridcolor='rgba(45, 55, 72, 0.5)', range=[0, 100], row=2, col=1)
        
        st.plotly_chart(fig_bat, use_container_width=True)
    
    # --- Flux instantanés (Snapshot à midi) ---
    st.markdown("### 🔄 Flux d'Énergie (Aperçu à midi)")
    
    mid_idx = len(production_values)//2
    if mid_idx < len(production_values):
        c_prod = production_values[mid_idx]
        c_cons = consumption_values[mid_idx]
        c_bat = battery_power[mid_idx]
        c_net = network_power[mid_idx]
        
        fc1, fc2, fc3, fc4 = st.columns(4)
        
        with fc1:
            st.markdown(f"""<div class='card' style='text-align:center'>
                <div style='font-size:2rem'>☀️</div>
                <h3 style='color:#fbbf24'>{c_prod:.2f} kW</h3>
            </div>""", unsafe_allow_html=True)
        with fc2:
            st.markdown(f"""<div class='card' style='text-align:center'>
                <div style='font-size:2rem'>🔋</div>
                <h3 style='color:#3b82f6'>{c_bat:.2f} kW</h3>
            </div>""", unsafe_allow_html=True)
        with fc3:
            st.markdown(f"""<div class='card' style='text-align:center'>
                <div style='font-size:2rem'>🏠</div>
                <h3 style='color:#8b5cf6'>{c_cons:.2f} kW</h3>
            </div>""", unsafe_allow_html=True)
        with fc4:
             st.markdown(f"""<div class='card' style='text-align:center'>
                <div style='font-size:2rem'>⚡</div>
                <h3 style='color:{"#10b981" if c_net > 0 else "#ef4444"}'>{c_net:.2f} kW</h3>
            </div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()