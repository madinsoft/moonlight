"""
Module de récupération des données de production solaire
Utilise PVGIS (Photovoltaic Geographical Information System)
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from pathlib import Path

def fetch_solar_data(latitude, longitude, year, output_file):
    """
    Récupère les données de production solaire via PVGIS
    
    Args:
        latitude: Latitude du lieu
        longitude: Longitude du lieu
        year: Année de simulation
        output_file: Chemin du fichier CSV de sortie
    """
    print(f"🔍 Tentative de récupération via PVGIS...")
    print(f"   Latitude: {latitude}, Longitude: {longitude}")
    
    # URL de l'API PVGIS
    url = "https://re.jrc.ec.europa.eu/api/v5_2/seriescalc"
    
    params = {
        'lat': latitude,
        'lon': longitude,
        'startyear': year,
        'endyear': year,
        'pvcalculation': 1,
        'peakpower': 100,  # 100 kWc (sera mis à l'échelle plus tard)
        'loss': 14,
        'mountingplace': 'building',
        'angle': 35,
        'aspect': 0,
        'outputformat': 'json'
    }
    
    try:
        print("⏳ Requête en cours (peut prendre 30-60 secondes)...")
        response = requests.get(url, params=params, timeout=120)
        response.raise_for_status()
        
        data = response.json()
        
        if 'outputs' in data and 'hourly' in data['outputs']:
            hourly_data = data['outputs']['hourly']
            
            # Convertir en DataFrame
            df = pd.DataFrame(hourly_data)
            
            # Créer timestamp
            df['timestamp'] = pd.to_datetime(
                df[['year', 'month', 'day', 'hour']].rename(columns={'hour': 'hour'})
            )
            
            # Convertir P (W) en kW
            df['production_kw'] = df['P'] / 1000
            
            # Interpoler pour obtenir des données au quart d'heure
            df = df.set_index('timestamp')
            df_15min = df[['production_kw']].resample('15min').interpolate(method='linear')
            df_15min = df_15min.reset_index()
            
            # Formater timestamp
            df_15min['timestamp'] = df_15min['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Sauvegarder
            df_15min.to_csv(output_file, index=False)
            
            print(f"✅ {len(df_15min)} enregistrements générés")
            print(f"   Production max: {df_15min['production_kw'].max():.2f} kW")
            print(f"   Production moy: {df_15min['production_kw'].mean():.2f} kW")
            
        else:
            raise Exception("Format de réponse PVGIS inattendu")
            
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Échec PVGIS: {e}")
        print("🔄 Génération de données synthétiques...")
        generate_synthetic_solar_data(latitude, year, output_file)

def generate_synthetic_solar_data(latitude, year, output_file):
    """
    Génère des données solaires synthétiques réalistes
    """
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31, 23, 45)
    
    # Générer timestamps toutes les 15 minutes
    timestamps = []
    current = start_date
    while current <= end_date:
        timestamps.append(current)
        current += timedelta(minutes=15)
    
    df = pd.DataFrame({'timestamp': timestamps})
    df['day_of_year'] = df['timestamp'].dt.dayofyear
    df['hour'] = df['timestamp'].dt.hour
    df['minute'] = df['timestamp'].dt.minute
    df['hour_decimal'] = df['hour'] + df['minute'] / 60
    
    # Modèle de production solaire
    # Variation saisonnière
    season_factor = 0.5 + 0.5 * np.cos(2 * np.pi * (df['day_of_year'] - 172) / 365)
    
    # Courbe journalière (gaussienne centrée à midi)
    daily_curve = np.exp(-((df['hour_decimal'] - 12) ** 2) / 18)
    
    # Production de base (kW pour 100 kWc)
    base_production = 80  # kW max
    
    df['production_kw'] = base_production * season_factor * daily_curve
    
    # Ajouter variabilité (nuages)
    np.random.seed(42)
    noise = np.random.normal(1, 0.15, len(df))
    noise = np.clip(noise, 0.3, 1.2)
    df['production_kw'] = df['production_kw'] * noise
    
    # Production nulle la nuit
    df.loc[(df['hour_decimal'] < 6) | (df['hour_decimal'] > 20), 'production_kw'] = 0
    
    # Limiter à 0
    df['production_kw'] = df['production_kw'].clip(lower=0)
    
    # Formater
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df[['timestamp', 'production_kw']].to_csv(output_file, index=False)
    
    print(f"✅ {len(df)} enregistrements synthétiques générés")
    print(f"   Production max: {df['production_kw'].max():.2f} kW")
    print(f"   Production moy: {df['production_kw'].mean():.2f} kW")
