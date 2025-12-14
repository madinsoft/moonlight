/**
 * Parse un fichier CSV et filtre les données pour une date spécifique
 * @param {string} csvText - Contenu du fichier CSV
 * @param {string} targetDate - Date à filtrer (format YYYY-MM-DD)
 * @returns {Array} Tableau d'objets avec timestamp, time et value
 */
export function parseCSV(csvText, targetDate) {
  const lines = csvText.trim().split('\n')
  
  if (lines.length < 2) {
    console.warn('⚠️ CSV vide ou invalide')
    return []
  }
  
  const data = []
  
  // Ignorer la première ligne (en-têtes)
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim()
    
    // Ignorer les lignes vides
    if (!line) continue
    
    const parts = line.split(',')
    
    // Vérifier que la ligne a au moins 2 colonnes
    if (parts.length < 2) {
      console.warn(`⚠️ Ligne ignorée (format invalide): ${line}`)
      continue
    }
    
    const timestamp = parts[0]?.trim()
    const valueStr = parts[1]?.trim()
    
    // Vérifier que le timestamp et la valeur existent
    if (!timestamp || !valueStr) {
      console.warn(`⚠️ Ligne ignorée (données manquantes): ${line}`)
      continue
    }
    
    // Extraire la date du timestamp
    const dateFromTimestamp = timestamp.split(' ')[0]
    
    // Filtrer par date si spécifiée
    if (targetDate && dateFromTimestamp !== targetDate) {
      continue
    }
    
    // Parser la valeur
    const value = parseFloat(valueStr)
    
    // Vérifier que la valeur est un nombre valide
    if (isNaN(value)) {
      console.warn(`⚠️ Ligne ignorée (valeur invalide): ${line}`)
      continue
    }
    
    // Extraire l'heure (format HH:MM)
    const timePart = timestamp.split(' ')[1]
    const time = timePart ? timePart.substring(0, 5) : '00:00'
    
    data.push({
      timestamp,
      time,
      value
    })
  }
  
  console.log(`✅ ${data.length} lignes valides parsées`)
  
  return data
}
