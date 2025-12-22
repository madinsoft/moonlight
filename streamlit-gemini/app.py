import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import timedelta
import numpy as np

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Dashboard Solaire",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- THEME & COULEURS (Inspiré de votre CSS) ---
THEME = {
    'bg': '#0f1419',
    'card': '#1a1f2e',
    'blue': '#3b82f6',
    'yellow': '#f59e0b',
    'purple': '#8B5CF6',
    'green': '#10b981',
    'red': '#ef4444',
    'text': '#f3f4f6'
}

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data
def load_data():
    try:
        # Adaptation des noms de colonnes si nécessaire
        prod_df = pd.read_csv('data/production.csv', parse_dates=['timestamp'])
        cons_df = pd.read_csv('data/consumption.csv', parse_dates=['timestamp'])
        
        # Renommage standard
        prod_df.rename(columns={'value': 'production'}, inplace=True)
        cons_df.rename(columns={'value': 'consumption'}, inplace=True)
        
        # Fusion sur le timestamp
        df = pd.merge(prod_df, cons_df, on='timestamp', how='inner')
        df.set_index('timestamp', inplace=True)
        return df
    except FileNotFoundError:
        st.error("⚠️ Fichiers CSV introuvables. Veuillez les placer dans le dossier 'data/'.")
        return pd.DataFrame()

# --- LOGIQUE DE SIMULATION BATTERIE ---
def process_energy_flow(df_day, battery_capacity_kwh):
    """
    Simule le comportement de la batterie et du réseau.
    Logique portée depuis le projet Vue.js.
    """
    # Conversion index temporel en heures pour le calcul de l'énergie (si données en kW)
    # On suppose un pas de temps constant
    if len(df_day) > 1:
        time_diff = (df_day.index[1] - df_day.index[0]).seconds / 3600.0
    else:
        time_diff = 0.25 # Defaut 15 min
        
    battery_energy = [] # kWh stockés
    grid_power = []     # kW (Positif = Injection, Négatif = Soutirage)
    soc = []            # % de charge
    
    current_battery_kwh = battery_capacity_kwh * 0.5 # On commence à 50%
    
    for _, row in df_day.iterrows():
        prod = row['production']
        cons = row['consumption']
        net_load = prod - cons # Surplus si positif, Besoin si négatif
        
        # Calcul de l'énergie disponible/requise pour ce pas de temps
        energy_step = net_load * time_diff
        
        if energy_step > 0:
            # Surplus -> Charge batterie
            space_available = battery_capacity_kwh - current_battery_kwh
            to_battery = min(energy_step, space_available)
            current_battery_kwh += to_battery
            to_grid_energy = energy_step - to_battery
        else:
            # Déficit -> Décharge batterie
            energy_needed = abs(energy_step)
            from_battery = min(energy_needed, current_battery_kwh)
            current_battery_kwh -= from_battery
            to_grid_energy = -(energy_needed - from_battery) # Négatif = soutirage
            
        battery_energy.append(current_battery_kwh)
        soc.append((current_battery_kwh / battery_capacity_kwh) * 100)
        
        # Puissance réseau (kW) = Energie réseau / temps
        grid_power.append(to_grid_energy / time_diff)

    df_res = df_day.copy()
    df_res['battery_soc'] = soc
    df_res['grid_power'] = grid_power
    df_res['battery_kwh'] = battery_energy
    
    # Séparation batterie charge/décharge pour le graph
    df_res['battery_power'] = df_res['production'] - df_res['consumption'] - df_res['grid_power']
    
    return df_res

# --- VISUALISATION PLOTLY ---
def create_chart(df, y_col, title, color, fill=True, y_axis_title="Puissance (kW)"):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df[y_col], 
        mode='lines',
        name=title,
        line=dict(color=color, width=2),
        fill='tozeroy' if fill else None,
        fillcolor=f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.2)" if fill else None
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(color='white')),
        paper_bgcolor=THEME['card'],
        plot_bgcolor=THEME['card'],
        font=dict(color='#9ca3af'),
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#2d3748', title=y_axis_title),
        hovermode="x unified"
    )
    return fig

def create_network_chart(df):
    fig = go.Figure()
    
    # Batterie (Zone violette)
    fig.add_trace(go.Scatter(
        x=df.index, y=df['battery_power'],
        name="Batterie",
        line=dict(color=THEME['purple'], width=2),
        fill='tozeroy',
        fillcolor="rgba(139, 92, 246, 0.2)"
    ))
    
    # Réseau (Ligne Verte/Rouge) - Astuce: on trace deux lignes ou on utilise un dégradé, 
    # mais Plotly simple préfère une couleur. On va utiliser vert pour le tout et indiquer via le signe.
    fig.add_trace(go.Scatter(
        x=df.index, y=df['grid_power'],
        name="Réseau",
        line=dict(color=THEME['green'], width=2),
    ))

    fig.update_layout(
        title=dict(text="Flux Énergétiques (Réseau & Batterie)", font=dict(color='white')),
        paper_bgcolor=THEME['card'],
        plot_bgcolor=THEME['card'],
        font=dict(color='#9ca3af'),
        yaxis=dict(gridcolor='#2d3748', title="Puissance (kW)"),
        xaxis=dict(showgrid=False)
    )
    return fig

# --- MAIN APP ---
def main():
    # CSS Hack pour le look "Dashboard"
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {THEME['bg']}; }}
        .stMetric {{ background-color: {THEME['card']}; padding: 15px; border-radius: 10px; border: 1px solid #2d3748; }}
        [data-testid="stHeader"] {{ background-color: {THEME['bg']}; }}
        </style>
    """, unsafe_allow_html=True)

    # Sidebar
    st.sidebar.title("Configuration")
    
    df = load_data()
    if df.empty:
        return

    # Sélecteurs
    min_date = df.index.min().date()
    max_date = df.index.max().date()
    
    selected_date = st.sidebar.date_input(
        "Date", 
        value=min_date + timedelta(days=180), # Date d'été par défaut
        min_value=min_date, 
        max_value=max_date
    )
    
    battery_cap = st.sidebar.slider(
        "Capacité Batterie (kWh)", 
        min_value=50, 
        max_value=1500, 
        value=500, 
        step=50
    )

    # Filtrage et Calculs
    day_df = df[df.index.date == selected_date].copy()
    
    if day_df.empty:
        st.warning("Pas de données pour cette date.")
        return
        
    final_df = process_energy_flow(day_df, battery_cap)
    
    # KPI Totaux
    total_prod = final_df['production'].sum() / 4 # approx si données 15min
    total_cons = final_df['consumption'].sum() / 4
    net_grid = final_df['grid_power'].sum() / 4
    
    # En-tête Dashboard
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.title("Dashboard Solaire")
        st.caption(f"Données pour le {selected_date}")
    
    # Métriques
    m1, m2, m3 = st.columns(3)
    m1.metric("Production Solaire", f"{total_prod:.1f} kWh", delta_color="normal")
    m2.metric("Consommation", f"{total_cons:.1f} kWh", delta="-")
    m3.metric("Bilan Réseau", f"{abs(net_grid):.1f} kWh", 
              delta="Injecté" if net_grid > 0 else "Soutiré",
              delta_color="normal" if net_grid > 0 else "inverse")

    st.markdown("---")

    # Graphiques Ligne 1
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(create_chart(final_df, 'production', "Production Solaire", THEME['blue']), use_container_width=True)
    with c2:
        st.plotly_chart(create_chart(final_df, 'consumption', "Consommation du Quartier", THEME['yellow']), use_container_width=True)

    # Graphiques Ligne 2
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(create_network_chart(final_df), use_container_width=True)
    with c4:
        st.plotly_chart(create_chart(final_df, 'battery_soc', "État de Charge Batterie (%)", THEME['purple'], y_axis_title="%"), use_container_width=True)

if __name__ == "__main__":
    main()