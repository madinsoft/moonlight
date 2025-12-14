#!/usr/bin/env python3
"""
Script principal de récupération et mise à l'échelle des données
"""
import os
import sys
from pathlib import Path
import json
from datetime import datetime

from solar_data import fetch_solar_data
from consumption_data import fetch_consumption_data
from scaler import scale_production_to_consumption

# Chemins
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"

def main():
    """Point d'entrée principal"""
    print("=" * 60)
    print("RÉCUPÉRATION DES DONNÉES - DASHBOARD SOLAIRE")
    print("=" * 60)
    
    # Créer le répertoire data s'il n'existe pas
    DATA_DIR.mkdir(exist_ok=True)
    
    # Paramètres
    year = 2024
    latitude = 43.6  # Sud de la France (Marseille)
    longitude = 3.9
    
    print(f"\n📍 Localisation: {latitude}°N, {longitude}°E")
    print(f"📅 Année: {year}\n")
    
    # Étape 1: Récupération production solaire
    print("=" * 60)
    print("ÉTAPE 1/3: Récupération données production solaire")
    print("=" * 60)
    solar_file = DATA_DIR / "solar_production.csv"
    try:
        fetch_solar_data(
            latitude=latitude,
            longitude=longitude,
            year=year,
            output_file=solar_file
        )
        print(f"✅ Production solaire sauvegardée: {solar_file}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)
    
    # Étape 2: Récupération consommation
    print("\n" + "=" * 60)
    print("ÉTAPE 2/3: Récupération données consommation")
    print("=" * 60)
    consumption_file = DATA_DIR / "consumption.csv"
    try:
        fetch_consumption_data(
            year=year,
            output_file=consumption_file
        )
        print(f"✅ Consommation sauvegardée: {consumption_file}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)
    
    # Étape 3: Mise à l'échelle
    print("\n" + "=" * 60)
    print("ÉTAPE 3/3: Mise à l'échelle production/consommation")
    print("=" * 60)
    scaled_file = DATA_DIR / "solar_production_scaled.csv"
    metadata_file = DATA_DIR / "metadata.json"
    
    try:
        metadata = scale_production_to_consumption(
            solar_file=solar_file,
            consumption_file=consumption_file,
            output_file=scaled_file
        )
        
        # Sauvegarder métadonnées
        metadata['generation_date'] = datetime.now().isoformat()
        metadata['latitude'] = latitude
        metadata['longitude'] = longitude
        metadata['year'] = year
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Production mise à l'échelle: {scaled_file}")
        print(f"✅ Métadonnées: {metadata_file}")
        print(f"\n📊 Facteur d'échelle appliqué: {metadata['scale_factor']:.2f}")
        print(f"📊 Cumul journalier moyen production: {metadata['avg_daily_production_kwh']:.2f} kWh")
        print(f"📊 Cumul journalier moyen consommation: {metadata['avg_daily_consumption_kwh']:.2f} kWh")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ RÉCUPÉRATION TERMINÉE AVEC SUCCÈS")
    print("=" * 60)
    print(f"\n📁 Fichiers générés dans: {DATA_DIR}")
    print("   - solar_production.csv")
    print("   - consumption.csv")
    print("   - solar_production_scaled.csv")
    print("   - metadata.json")
    print("\n🚀 Vous pouvez maintenant lancer l'application web!\n")

if __name__ == "__main__":
    main()
