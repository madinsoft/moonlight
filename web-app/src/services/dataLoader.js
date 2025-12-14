import Papa from 'papaparse'

export async function loadCSVData() {
  try {
    // Charger les 3 fichiers CSV
    const [production, consumption, metadata] = await Promise.all([
      loadCSV('/data/solar_production_2.csv'),
      loadCSV('/data/consumption.csv'),
      loadJSON('/data/metadata.json')
    ])

    return {
      production,
      consumption,
      metadata
    }
  } catch (error) {
    throw new Error(`Erreur de chargement des données:  $ {error.message}`)
  }
}

async function loadCSV(path) {
  const response = await fetch(path)
  
  if (!response.ok) {
    throw new Error(`Fichier non trouvé:  $ {path}`)
  }
  
  const csvText = await response.text()
  
  return new Promise((resolve, reject) => {
    Papa.parse(csvText, {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      delimiter: ',',
      complete: (results) => {
        if (results.errors.length > 0) {
          console.warn('Erreurs de parsing CSV:', results.errors)
        }
        resolve(results.data)
      },
      error: (error) => {
        reject(error)
      }
    })
  })
}

async function loadJSON(path) {
  const response = await fetch(path)
  
  if (!response.ok) {
    throw new Error(`Fichier non trouvé: ${path}`)
  }
  
  return response.json()
}
