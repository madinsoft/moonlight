import requests
import pandas as pd
from datetime import datetime
import time

def recuperer_donnees_enedis_2024():
    """
    Récupère les données de puissance électrique pour l'année 2024
    depuis l'API Enedis (bilan électrique demi-heure)
    """
    
    # URL de base de l'API
    base_url = "https://data.enedis.fr/api/records/1.0/search/"
    
    # Paramètres de la requête
    params = {
        'dataset': 'bilan-electrique-demi-heure',
        'q': '',
        'rows': 100,  # Nombre de résultats par requête (max 100)
        'start': 0,
        'refine.horodate': '2024',  # Filtre pour l'année 2024
        'sort': 'horodate',
        'facet': 'horodate'
    }
    
    all_records = []
    start = 0
    
    print("Début de la récupération des données pour 2024...")
    
    while True:
        params['start'] = start
        
        try:
            response = requests.get(base_url, params=params, verify=False)
            response.raise_for_status()
            data = response.json()
            
            # Extraire les enregistrements
            records = data.get('records', [])
            
            if not records:
                print("Fin de la récupération des données.")
                break
            
            all_records.extend(records)
            
            # Informations de progression
            total_count = data.get('nhits', 0)
            print(f"Récupéré {len(all_records)} / {total_count} enregistrements...")
            
            # Vérifier s'il reste des données à récupérer
            if len(all_records) >= total_count:
                break
            
            start += len(records)
            
            # Pause pour éviter de surcharger l'API
            time.sleep(0.5)
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la requête : {e}")
            break
    
    return all_records

def traiter_donnees(records):
    """
    Traite les données brutes et crée un DataFrame pandas
    """
    donnees_traitees = []
    
    for record in records:
        fields = record.get('fields', {})
        
        donnee = {
            'horodate': fields.get('horodate'),
            'injection_rte': fields.get('injection_rte'),
            'soutirage_rte': fields.get('soutirage_rte'),
            'consommation_totale': fields.get('consommation_totale'),
            'production_totale': fields.get('production_totale'),
            'production_photovoltaique': fields.get('production_photovoltaique'),
        }
        
        donnees_traitees.append(donnee)
    
    # Créer un DataFrame
    df = pd.DataFrame(donnees_traitees)
    
    # Convertir la colonne horodate en datetime
    df['horodate'] = pd.to_datetime(df['horodate'])
    
    # Trier par date
    df = df.sort_values('horodate')
    
    return df

def sauvegarder_donnees(df, format='csv'):
    """
    Sauvegarde les données dans différents formats
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if format == 'csv':
        filename = f'enedis_puissance_2024_{timestamp}.csv'
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"Données sauvegardées dans {filename}")
    
    elif format == 'excel':
        filename = f'enedis_puissance_2024_{timestamp}.xlsx'
        df.to_excel(filename, index=False)
        print(f"Données sauvegardées dans {filename}")
    
    elif format == 'json':
        filename = f'enedis_puissance_2024_{timestamp}.json'
        df.to_json(filename, orient='records', date_format='iso', indent=2)
        print(f"Données sauvegardées dans {filename}")
    
    return filename

def afficher_statistiques(df):
    """
    Affiche des statistiques sur les données récupérées
    """
    print("\n" + "="*60)
    print("STATISTIQUES DES DONNÉES 2024")
    print("="*60)
    print(f"\nNombre total d'enregistrements : {len(df)}")
    print(f"Période couverte : du {df['horodate'].min()} au {df['horodate'].max()}")
    print(f"\nColonnes disponibles : {', '.join(df.columns)}")
    
    print("\n--- Statistiques de Soutirage RTE (en MW) ---")
    if 'soutirage_rte' in df.columns:
        print(df['soutirage_rte'].describe())
    
    print("\n--- Statistiques d'Injection RTE (en MW) ---")
    if 'injection_rte' in df.columns:
        print(df['injection_rte'].describe())
    
    print("\n--- Aperçu des premières lignes ---")
    print(df.head())

# Programme principal
if __name__ == "__main__":
    # 1. Récupérer les données
    records = recuperer_donnees_enedis_2024()
    
    if records:
        # 2. Traiter les données
        df = traiter_donnees(records)
        
        # 3. Afficher les statistiques
        afficher_statistiques(df)
        
        # 4. Sauvegarder les données (choisir le format)
        sauvegarder_donnees(df, format='csv')
        # sauvegarder_donnees(df, format='excel')  # Décommenter pour Excel
        # sauvegarder_donnees(df, format='json')   # Décommenter pour JSON
        
        print("\n✅ Traitement terminé avec succès !")
    else:
        print("❌ Aucune donnée récupérée.")
