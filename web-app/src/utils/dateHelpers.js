/**
 * Formate une date au format YYYY-MM-DD
 */
export function formatDate(date) {
  if (typeof date === 'string') {
    return date.split(' ')[0]
  }
  
  if (date instanceof Date) {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }
  
  return ''
}

/**
 * Extrait la date d'un timestamp
 */
export function extractDate(timestamp) {
  return timestamp.split(' ')[0]
}

/**
 * Extrait l'heure d'un timestamp (format HH:MM)
 */
export function extractTime(timestamp) {
  return timestamp.split(' ')[1]?.substring(0, 5) || ''
}

/**
 * Vérifie si une date est valide
 */
export function isValidDate(dateString) {
  const date = new Date(dateString)
  return date instanceof Date && !isNaN(date)
}

/**
 * Retourne la liste des dates entre deux dates
 */
export function getDateRange(startDate, endDate) {
  const dates = []
  const current = new Date(startDate)
  const end = new Date(endDate)

  while (current <= end) {
    dates.push(formatDate(current))
    current.setDate(current.getDate() + 1)
  }

  return dates
}

/**
 * Formate une date en français
 */
export function formatDateFR(dateString) {
  const date = new Date(dateString)
  const options = { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  }
  return date.toLocaleDateString('fr-FR', options)
}
