"""
Module de mise à l'échelle de la production solaire
pour correspondre à la consommation du quartier
"""
import pandas as pd
import numpy as np

def scale_production_to_consumption(solar_file, consumption_file, output_file):
    """
    Met à l'échelle la production solaire pour que le cumul journalier moyen
    corresponde au cumul journalier moyen de consommation
    
    Args:
        solar_file: Fichier CSV de production solaire
        consumption_file: Fichier CSV de consommation
        output_file: Fichier CSV de sortie (production mise à l'échelle)
    
    Returns:
        dict: Métadonnées (facteur d'échelle, statistiques)
    """
    print("📊 Chargement des données...")
    
    # Charger les données
    df_solar = pd.read_csv(solar_file)
    df_consumption = pd.read_csv(consumption_file)
    
    # Convertir timestamps
    df_solar['timestamp'] = pd.to_datetime(df_solar['timestamp'])
    df_consumption['timestamp'] = pd.to_datetime(df_consumption['timestamp'])
    
    # Extraire date (sans heure)
    df_solar['date'] = df_solar['timestamp'].dt.date
    df_consumption['date'] = df_consumption['timestamp'].dt.date
    
    # Calculer cumuls journaliers (kWh = kW * 0.25h pour pas de 15 min)
    solar_daily = df_solar.groupby('date')['production_kw'].sum() * 0.25
    consumption_daily = df_consumption.groupby('date')['consumption_kw'].sum() * 0.25
    
    # Moyennes
    avg_solar_daily = solar_daily.mean()
    avg_consumption_daily = consumption_daily.mean()
    
    print(f"   Production journalière moyenne: {avg_solar_daily:.2f} kWh")
    print(f"   Consommation journalière moyenne: {avg_consumption_daily:.2f} kWh")
    
    # Calculer facteur d'échelle
    scale_factor = avg_consumption_daily / avg_solar_daily
    
    print(f"\n🔧 Application du facteur d'échelle: {scale_factor:.2f}")
    
    # Appliquer l'échelle
    df_solar['production_kw_scaled'] = df_solar['production_kw'] * scale_factor
    
    # Sauvegarder
    df_output = df_solar[['timestamp', 'production_kw_scaled']].copy()
    df_output.columns = ['timestamp', 'production_kw']
    df_output.to_csv(output_file, index=False)
    
    # Préparer métadonnées
    metadata = {
        'scale_factor': float(scale_factor),
        'avg_daily_production_kwh': float(avg_solar_daily * scale_factor),
        'avg_daily_consumption_kwh': float(avg_consumption_daily),
        'total_records_solar': int(len(df_solar)),
        'total_records_consumption': int(len(df_consumption)),
        'date_start': str(df_solar['timestamp'].min()),
        'date_end': str(df_solar['timestamp'].max())
    }
    
    print(f"✅ Production mise à l'échelle sauvegardée")
    print(f"   Nouvelle production journalière moyenne: {metadata['avg_daily_production_kwh']:.2f} kWh")
    
    return metadata
