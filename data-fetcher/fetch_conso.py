import requests
import pandas as pd
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning 

# Désactiver l'avertissement d'insécurité lié à verify=False
warnings.simplefilter('ignore', InsecureRequestWarning)

# --- Configuration de l'API ---
BASE_URL = "https://data.enedis.fr/api/explore/v2.1/catalog/datasets/bilan-electrique-demi-heure/records"
# Le nombre de lignes par requête est maintenant le nombre max par mois.
ROWS_PER_REQUEST = 31 * 48 * 2  # Environ 3000, 10000 est sûr.
TARGET_YEAR = 2024
CSV_FILENAME = f'bilan_electrique_{TARGET_YEAR}_mensuel_fix.csv'

# Liste pour stocker les DataFrames de chaque mois
all_data = []

print(f"Démarrage de la récupération des données pour l'année {TARGET_YEAR} par itération mensuelle...")

# Itération sur les 12 mois de l'année
for month in range(1, 13):
    # Formatage de la date pour la requête (ex: 2024/01)
    refine_date = f"{TARGET_YEAR}/{month:02d}"
    
    # Construction des paramètres de la requête
    params = {
        # Filtre sur le mois et l'année
        "refine": f"horodate:{refine_date}",
        "limit": ROWS_PER_REQUEST,
        "order_by": "horodate",
        "select": "horodate, injection_rte, soutirage_rte",
    }
    
    try:
        # Envoi de la requête avec vérification SSL désactivée
        response = requests.get(BASE_URL, params=params, verify=False)
        response.raise_for_status() # Lève l'exception si le statut est un échec
        
        data = response.json()
        records = data.get('results', [])
        
        if records:
            df_month = pd.DataFrame(records)
            all_data.append(df_month)
            print(f"✅ Mois {month:02d} : {len(df_month)} enregistrements récupérés.")
        else:
            print(f"⚠️ Mois {month:02d} : Aucune donnée trouvée.")

    except requests.exceptions.HTTPError as e:
        print(f"❌ Erreur HTTP ({e.response.status_code}) lors du mois {month:02d} : {e}")
        # Arrêter si une erreur 400 ou 404 est rencontrée
        break 
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion lors du mois {month:02d} : {e}")
        break

# --- Traitement Final ---

if all_data:
    df_final = pd.concat(all_data, ignore_index=True)
    
    # Nettoyage et Préparation des Données
    df_final['horodate'] = pd.to_datetime(df_final['horodate'])
    df_final = df_final.set_index('horodate').sort_index()
    df_final = df_final.rename(columns={
        'injection_rte': 'Puissance_Injectee_MWh', 
        'soutirage_rte': 'Puissance_Soutiree_MWh' 
    })
    
    # Sauvegarde en CSV
    df_final.to_csv(CSV_FILENAME, index=True, encoding='utf-8')
    
    print("\n--- Opération Terminée ---")
    print(f"Nombre total d'enregistrements (demi-heures) pour {TARGET_YEAR} : {len(df_final)}")
    print(f"✅ Données sauvegardées dans : **{CSV_FILENAME}**")
    print("Aperçu des cinq premières lignes du fichier :")
    print(df_final.head())
    
else:
    print("\nAucune donnée n'a pu être récupérée au total.")