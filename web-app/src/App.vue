<template>
  <div class="min-h-screen bg-dark-bg pb-12">
    <!-- Header -->
    <header class="bg-dark-card border-b border-dark-border sticky top-0 z-50 backdrop-blur-sm bg-opacity-95">
      <div class="container mx-auto px-4 py-6">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <div class="w-10 h-10 bg-gradient-to-br from-blue-primary to-blue-secondary rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
            <div>
              <h1 class="text-2xl font-bold text-white">Dashboard Solaire</h1>
              <p class="text-sm text-gray-light">Quartier Résidentiel - Sud de la France</p>
            </div>
          </div>
          
          <div v-if="metadata" class="hidden md:flex items-center space-x-6 text-sm">
            <div class="text-center">
              <div class="text-gray-light">Production moy.</div>
              <div class="text-blue-accent font-semibold">{{ metadata.avg_daily_production_kwh?.toFixed(0) }} kWh/j</div>
            </div>
            <div class="text-center">
              <div class="text-gray-light">Consommation moy.</div>
              <div class="text-yellow-primary font-semibold">{{ metadata.avg_daily_consumption_kwh?.toFixed(0) }} kWh/j</div>
            </div>
          </div>

          <!-- Player and Battery Controls -->
          <div class="flex items-center space-x-6">
            <ChartPlayerControls 
              v-if="chartData.production.length"
              :time-labels="chartData.production.map(d => d.time)"
              class="hidden md:flex"
            />
            <!-- Battery Slider -->
            <div class="flex items-center space-x-4">
              <svg class="w-6 h-6 text-purple-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7h16M4 12h16M4 17h16"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 5v14M18 5v14"></path></svg>
              <div class="w-48 text-sm">
                <div class="flex justify-between text-gray-light">
                  <span>Batterie</span>
                  <span class="font-bold text-white">{{ batteryCapacityKwh }} kWh</span>
                </div>
                <input 
                  type="range" 
                  min="50" 
                  max="1500" 
                  step="50"
                  v-model.number="batteryCapacityKwh"
                  class="w-full h-1.5 bg-gray-700 rounded-lg appearance-none cursor-pointer range-sm">
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center min-h-[400px]">
        <div class="text-center">
          <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-primary mx-auto mb-4"></div>
          <p class="text-gray-light">Chargement des données...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="card p-8 text-center">
        <svg class="w-16 h-16 text-red-primary mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h2 class="text-xl font-semibold text-white mb-2">Erreur de chargement</h2>
        <p class="text-gray-light mb-4">{{ error }}</p>
        <button @click="loadData" class="btn-primary">
          Réessayer
        </button>
      </div>

      <!-- Data Display -->
      <div v-else class="space-y-6">
        <!-- Controls -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <DatePicker 
            v-model="selectedDate"
            :available-dates="availableDates"
            @update:modelValue="onDateChange"
            class="lg:col-span-1"
          />
        </div>

        <!-- Statistics Panel -->
        <StatisticsPanel 
          v-if="dailyStats"
          :stats="dailyStats"
        />

        <!-- Charts -->
        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
          <!-- Production Chart -->
          <GraphCard 
            title="Production Solaire"
            icon="sun"
            color="blue"
            :subtitle="` ${dailyStats?.production.total.toFixed(1)} kWh produits`"
          >
            <ChartProduction :data="chartData.production" />
          </GraphCard>

          <!-- Consumption Chart -->
          <GraphCard 
            title="Consommation du Quartier"
            icon="home"
            color="yellow"
            :subtitle="` ${dailyStats?.consumption.total.toFixed(1)} kWh consommés`"
          >
            <ChartConsumption :data="chartData.consumption" />
          </GraphCard>

          <!-- Network Chart -->
          <GraphCard 
            title="Flux Energétiques (Réseau & Batterie)"
            icon="activity"
            :color="dailyStats?.network.balance >= 0 ? 'green' : 'red'"
            :subtitle="getNetworkSubtitle()"
          >
            <ChartNetwork :networkData="chartData.network" :batteryData="chartData.battery" />
          </GraphCard>

          <!-- Battery SoC Chart -->
          <GraphCard 
            title="État de Charge de la Batterie"
            icon="battery"
            color="purple"
            subtitle="Évolution de l'énergie stockée"
          >
            <ChartBatterySoc :data="chartData.batterySoc" />
          </GraphCard>
        </div>

        <!-- Energy Flow Diagram -->
        <EnergyFlowDiagram 
          v-if="dailyStats && chartData"
          :stats="dailyStats"
          :chartData="chartData"
        />
      </div>
    </main>

    <!-- Footer -->
    <footer class="mt-12 text-center text-gray-medium text-sm">
      <p>Dashboard Solaire - Visualisation de production et consommation énergétique</p>
      <p class="mt-1">Données {{ metadata?.year }} - Sud de la France</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import DatePicker from './components/DatePicker.vue'
import StatisticsPanel from './components/StatisticsPanel.vue'
import GraphCard from './components/GraphCard.vue'
import ChartProduction from './components/ChartProduction.vue'
import ChartConsumption from './components/ChartConsumption.vue'
import ChartNetwork from './components/ChartNetwork.vue'
import ChartBatterySoc from './components/ChartBatterySoc.vue'
import EnergyFlowDiagram from './components/EnergyFlowDiagram.vue'
import ChartPlayerControls from './components/ChartPlayerControls.vue'
import { loadCSVData } from './services/dataLoader'
import { processDataForDate, calculateDailyStats } from './services/dataProcessor'

// State
const loading = ref(true)
const error = ref(null)
const selectedDate = ref(null)
const productionData = ref([])
const consumptionData = ref([])
const metadata = ref(null)
const batteryCapacityKwh = ref(500)

const chartData = ref({ production: [], consumption: [], network: [], battery: [], batterySoc: [] });
const dailyStats = ref(null);


// Computed
const availableDates = computed(() => {
  if (!productionData.value.length) return []
  
  const dates = new Set()
  productionData.value.forEach(row => {
    // console.log(row)
    if (row && row.timestamp && typeof row.timestamp === 'string') {
      const date = row.timestamp.split(' ')[0]
      if (date) {
        dates.add(date)
      }
    }
  })
  
  return Array.from(dates).sort()
})

// Methods
const processAllData = () => {
  if (!selectedDate.value) return;

  const processed = processDataForDate(
    productionData.value,
    consumptionData.value,
    selectedDate.value,
    batteryCapacityKwh.value
  );
  chartData.value = processed;

  dailyStats.value = calculateDailyStats(
    processed.production,
    processed.consumption,
    processed.network,
  );
};

const loadData = async () => {
  loading.value = true
  error.value = null
  
  try {
    const data = await loadCSVData()
    productionData.value = data.production
    consumptionData.value = data.consumption
    metadata.value = data.metadata
    
    // Sélectionner une date par défaut (21 juin - solstice d'été)
    if (availableDates.value.length > 0) {
      const summerDate = availableDates.value.find(d => d.includes('-06-21'))
      selectedDate.value = summerDate || availableDates.value[Math.floor(availableDates.value.length / 2)]
    }
  } catch (e) {
    error.value = e.message
    console.error('Erreur chargement:', e)
  } finally {
    loading.value = false
  }
}

const onDateChange = (newDate) => {
  selectedDate.value = newDate
}

const getNetworkSubtitle = () => {
  if (!dailyStats.value) return ''
  
  const balance = dailyStats.value.network.balance
  if (balance > 0) {
    return ` ${balance.toFixed(1)} kWh injectés sur le réseau`
  } else {
    return ` ${Math.abs(balance).toFixed(1)} kWh soutirés du réseau`
  }
}

// Watchers
watch(selectedDate, (newDate) => {
  if (newDate) {
    processAllData();
  }
});

watch(batteryCapacityKwh, (newCapacity) => {
  if (selectedDate.value) {
    processAllData();
  }
});


// Lifecycle
onMounted(async () => {
  await loadData();
  if (selectedDate.value) {
    processAllData();
  }
})
</script>
