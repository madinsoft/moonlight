/**
 * Processes raw production and consumption data for a specific date to generate chart-ready series,
 * including a battery simulation.
 * @param {Array} productionData - Raw production data.
 * @param {Array} consumptionData - Raw consumption data.
 * @param {string} dateString - The date to process data for (e.g., '2023-06-21').
 * @param {number} batteryCapacityKwh - The total capacity of the battery in kWh.
 * @returns {Object} - Contains arrays for production, consumption, network, and battery series.
 */
export function processDataForDate(productionData, consumptionData, dateString, batteryCapacityKwh = 0) {
  // Filter data for the selected date
  const productionFiltered = productionData.filter(row => row.timestamp.startsWith(dateString));
  const consumptionFiltered = consumptionData.filter(row => row.timestamp.startsWith(dateString));

  // --- Initialize Battery Simulation ---
  const timeStepHours = 0.25; // Data is in 15-minute intervals
  const minSoc = 0.10; // Minimum state of charge
  const maxSoc = 0.80; // Maximum state of charge
  let batteryStateOfChargeKwh = batteryCapacityKwh * 0.50; // Start the day at 50% charge

  const processed = {
    production: [],
    consumption: [],
    network: [],
    battery: [],
    batterySoc: []
  };

  // Map and process data point by point
  for (let i = 0; i < productionFiltered.length; i++) {
    const prodRow = productionFiltered[i];
    const consRow = consumptionFiltered.find(c => c.timestamp === prodRow.timestamp) || { consumption_kw: 0 };

    const time = prodRow.timestamp.split(' ')[1].substring(0, 5);
    const productionKw = prodRow.production_kw || 0;
    const consumptionKw = consRow.consumption_kw || 0;
    
    // Net power before battery interaction
    const netPowerKw = productionKw - consumptionKw;

    let batteryPowerKw = 0;
    let finalNetworkKw = 0;

    if (batteryCapacityKwh > 0) {
      // Record SoC *before* this interval's action
      const socPercentage = (batteryStateOfChargeKwh / batteryCapacityKwh) * 100;
      processed.batterySoc.push({ time, value: socPercentage, timestamp: prodRow.timestamp });

      if (netPowerKw > 0) { // Excess production -> Charge battery
        const maxChargePowerKw = (batteryCapacityKwh * maxSoc - batteryStateOfChargeKwh) / timeStepHours;
        const chargePowerKw = Math.min(netPowerKw, maxChargePowerKw);
        
        batteryPowerKw = -chargePowerKw; // Negative for charging
        batteryStateOfChargeKwh += chargePowerKw * timeStepHours;
        finalNetworkKw = netPowerKw - chargePowerKw; // Remaining goes to grid

      } else { // Deficit -> Discharge battery
        const maxDischargePowerKw = (batteryStateOfChargeKwh - batteryCapacityKwh * minSoc) / timeStepHours;
        const dischargePowerKw = Math.min(Math.abs(netPowerKw), maxDischargePowerKw);

        batteryPowerKw = dischargePowerKw; // Positive for discharging
        batteryStateOfChargeKwh -= dischargePowerKw * timeStepHours;
        finalNetworkKw = netPowerKw + dischargePowerKw; // Remaining is drawn from grid
      }
    } else {
        processed.batterySoc.push({ time, value: 0, timestamp: prodRow.timestamp });
        finalNetworkKw = netPowerKw;
    }


    processed.production.push({ time, value: productionKw, timestamp: prodRow.timestamp });
    processed.consumption.push({ time, value: consumptionKw, timestamp: prodRow.timestamp });
    processed.battery.push({ time, value: batteryPowerKw, timestamp: prodRow.timestamp });
    processed.network.push({ time, value: finalNetworkKw, timestamp: prodRow.timestamp });
  }

  return processed;
}


/**
 * Calculates summary statistics for the day based on processed data.
 * @param {Array} production - Processed production series.
 * @param {Array} consumption - Processed consumption series.
 * @param {Array} network - Processed network series (after battery).
 * @returns {Object} - An object with daily statistics.
 */
export function calculateDailyStats(production, consumption, network) {
  if (!production || !production.length) return null;
  // Cumul énergétique (kWh) - pas de 15 min = 0.25h
  const timeStep = 0.25

  const productionTotal = production.reduce((sum, d) => sum + d.value, 0) * timeStep
  const consumptionTotal = consumption.reduce((sum, d) => sum + d.value, 0) * timeStep
  
  // Le bilan réseau est maintenant la somme des valeurs du réseau final
  const networkBalance = network.reduce((sum, d) => sum + d.value, 0) * timeStep;


  // Valeurs max et leur timing
  const productionMax = Math.max(...production.map(d => d.value))
  const productionMaxTime = production.find(d => d.value === productionMax)?.time || ''

  const consumptionMax = Math.max(...consumption.map(d => d.value))
  const consumptionMaxTime = consumption.find(d => d.value === consumptionMax)?.time || ''

  // Taux d'autoconsommation: (Production Solaire - Injection Réseau) / Consommation Totale
  const totalInjected = network.filter(d => d.value > 0).reduce((sum, d) => sum + d.value, 0) * timeStep;
  const selfConsumedFromProd = productionTotal - totalInjected;
  const selfConsumption = consumptionTotal > 0 ? (selfConsumedFromProd / consumptionTotal) * 100 : 0;


  return {
    production: {
      total: productionTotal,
      max: productionMax,
      maxTime: productionMaxTime
    },
    consumption: {
      total: consumptionTotal,
      max: consumptionMax,
      maxTime: consumptionMaxTime
    },
    network: {
      balance: networkBalance
    },
    selfConsumption: Math.max(0, Math.min(100, selfConsumption)) // Clamp between 0 and 100
  }
}
