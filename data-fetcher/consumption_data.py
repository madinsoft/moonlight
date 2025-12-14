"""
Module de génération des données de consommation d'un quartier résidentiel
Basé sur des profils types de consommation française
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def fetch_consumption_data(year, output_file, num_homes=50):
    """
    Génère des données de consommation pour un quartier résidentiel
    
    Args:
        year: Année de simulation
        output_file: Chemin du fichier CSV de sortie
        num_homes: Nombre de foyers dans le quartier
    """
    print(f"🏘️  Génération consommation pour {num_homes} foyers...")
    
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
    df['weekday'] = df['timestamp'].dt.weekday  # 0=lundi, 6=dimanche
    df['is_weekend'] = df['weekday'] >= 5
    df['month'] = df['timestamp'].dt.month
    
    # Consommation de base par foyer (kW)
    base_consumption_per_home = 0.5  # 500W de base
    
    # Profil horaire (pic matin et soir)
    morning_peak = np.exp(-((df['hour'] - 8) ** 2) / 4)
    evening_peak = np.exp(-((df['hour'] - 19) ** 2) / 6) * 1.5
    night_reduction = 0.3 + 0.2 * np.exp(-((df['hour'] - 3) ** 2) / 8)
    
    hourly_profile = np.maximum.reduce([morning_peak, evening_peak, night_reduction])
    
    # Variation saisonnière (chauffage en hiver)
    winter_heating = np.zeros(len(df))
    winter_months = [1, 2, 3, 11, 12]
    for month in winter_months:
        mask = df['month'] == month
        winter_heating[mask] = 1.5
    
    summer_cooling = np.zeros(len(df))
    summer_months = [6, 7, 8]
    for month in summer_months:
        mask = df['month'] == month
        summer_cooling[mask] = 0.8
    
    seasonal_factor = 1 + winter_heating + summer_cooling
    
    # Réduction weekend (moins de consommation professionnelle)
    weekend_factor = np.where(df['is_weekend'], 0.85, 1.0)
    
    # Calcul consommation
    df['consumption_kw'] = (
        base_consumption_per_home * 
        num_homes * 
        hourly_profile * 
        seasonal_factor * 
        weekend_factor
    )
    
    # Ajouter variabilité réaliste
    np.random.seed(42)
    noise = np.random.normal(1, 0.1, len(df))
    noise = np.clip(noise, 0.7, 1.3)
    df['consumption_kw'] = df['consumption_kw'] * noise
    
    # Pics aléatoires (appareils électroménagers)
    random_peaks = np.random.random(len(df)) < 0.05
    df.loc[random_peaks, 'consumption_kw'] *= 1.5
    
    # Assurer valeurs positives
    df['consumption_kw'] = df['consumption_kw'].clip(lower=5)
    
    # Formater
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df[['timestamp', 'consumption_kw']].to_csv(output_file, index=False)
    
    print(f"✅ {len(df)} enregistrements générés")
    print(f"   Consommation max: {df['consumption_kw'].max():.2f} kW")
    print(f"   Consommation moy: {df['consumption_kw'].mean():.2f} kW")
    print(f"   Consommation min: {df['consumption_kw'].min():.2f} kW")
