<template>
  <div class="card p-4 relative">
    <h3 class="text-lg font-semibold text-white mb-4 text-center">Schéma des Flux Énergétiques</h3>
    <svg viewBox="0 0 500 350" class="w-full h-auto">
      
      <!-- Gauges (réduites et à gauche) -->
      <foreignObject x="10" y="30" width="40" height="80">
        <Gauge label="Solaire" :value="displayData.solar" :unit="displayData.unit" :max="displayData.maxSolar" positive-color="#3b82f6"/>
      </foreignObject>
      
      <foreignObject x="10" y="130" width="40" height="80">
        <Gauge label="Batterie" :value="displayData.battery" :unit="displayData.unit" :max="displayData.maxBattery" is-bidirectional positive-color="#c084fc" negative-color="#8B5CF6"/>
      </foreignObject>
      
      <foreignObject x="10" y="230" width="40" height="80">
         <Gauge label="Charge" :value="displayData.batterySoc" unit="%" :max="100" positive-color="#A78BFA" />
      </foreignObject>
      
      <foreignObject x="210" y="130" width="40" height="80">
        <Gauge label="Quartier" :value="displayData.house" :unit="displayData.unit" :max="displayData.maxHouse" positive-color="#f59e0b"/>
      </foreignObject>
      
      <foreignObject x="410" y="130" width="40" height="80">
        <Gauge label="Réseau" :value="displayData.grid" :unit="displayData.unit" :max="displayData.maxGrid" is-bidirectional/>
      </foreignObject>

      <!-- Icons (déplacés à droite des jauges) -->
      <image href="../assets/icons/solar-panel.svg" x="70" y="40" width="60" height="60" />
      <image href="../assets/icons/battery.svg" x="70" y="140" width="60" height="60" />
      <image href="../assets/icons/house.svg" x="270" y="140" width="60" height="60" />
      <image href="../assets/icons/grid.svg" x="470" y="140" width="60" height="60" />

      <!-- Static Wires (sens inversé: droite vers gauche) -->
      <!-- Solaire -> Quartier -->
      <path d="M 270 170 H 200 L 200 70 H 130" stroke="#4b5563" stroke-width="2" fill="none" />
      
      <!-- Solaire -> Batterie -->
      <path d="M 130 70 V 170" stroke="#4b5563" stroke-width="2" />
      
      <!-- Batterie -> Quartier -->
      <path d="M 130 170 H 270" stroke="#4b5563" stroke-width="2" fill="none" />
      
      <!-- Quartier -> Réseau -->
      <path d="M 330 170 H 470" stroke="#4b5563" stroke-width="2" />

      <!-- Dynamic Flows (sens inversé) -->
      <template v-if="animationStore.isPlaying">
        <!-- Solaire -> Quartier -->
        <path v-if="flows.solarToHouse" d="M 270 170 H 200 L 200 70 H 130" class="flow-line solar-to-house" />
        
        <!-- Solaire -> Batterie (charge) -->
        <path v-if="flows.solarToBattery" d="M 130 70 V 170" class="flow-line solar-to-battery" />
        
        <!-- Batterie -> Quartier (décharge) -->
        <path v-if="flows.batteryToHouse" d="M 130 170 H 270" class="flow-line battery-discharge" />
        
        <!-- Quartier -> Batterie (rare) -->
        <path v-if="flows.houseToBattery" d="M 270 170 H 130" class="flow-line battery-charge" />
        
        <!-- Réseau -> Quartier (soutirage) -->
        <path v-if="flows.gridToHouse" d="M 470 170 H 330" class="flow-line grid-draw" />
        
        <!-- Quartier -> Réseau (injection) -->
        <path v-if="flows.houseToGrid" d="M 330 170 H 470" class="flow-line grid-inject" />
      </template>

    </svg>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { animationStore } from '@/services/animationStore';
import Gauge from './Gauge.vue';

const props = defineProps({
  stats: {
    type: Object,
    required: true
  },
  chartData: {
    type: Object,
    required: true
  }
});

const flows = computed(() => {
  if (!animationStore.isPlaying || animationStore.currentIndex === null) {
    return {};
  }
  const i = animationStore.currentIndex;
  const prod = props.chartData.production[i]?.value || 0;
  const cons = props.chartData.consumption[i]?.value || 0;
  const batt = props.chartData.battery[i]?.value || 0;
  const net = props.chartData.network[i]?.value || 0;

  // Logique des flux (sens physique: production -> consommation)
  const solarToHouse = prod > 0 && cons > 0;
  const solarToBattery = prod > 0 && batt < 0; // Charge batterie
  const batteryToHouse = batt > 0 && cons > 0; // Décharge batterie
  const houseToBattery = cons < 0 && batt < 0; // Rare: surplus va en batterie
  const gridToHouse = net < 0; // Soutirage réseau
  const houseToGrid = net > 0; // Injection réseau

  return { solarToHouse, solarToBattery, batteryToHouse, houseToBattery, gridToHouse, houseToGrid };
});

const displayData = computed(() => {
  if (!props.stats) return {};

  const maxValues = {
    maxSolar: props.stats.production.max || 1,
    maxHouse: props.stats.consumption.max || 1,
    maxBattery: Math.max(...(props.chartData.battery || []).map(d => Math.abs(d.value))) || 1,
    maxGrid: Math.max(...(props.chartData.network || []).map(d => Math.abs(d.value))) || 1,
  };

  if (animationStore.isPlaying && animationStore.currentIndex !== null) {
    const i = animationStore.currentIndex;
    return {
      ...maxValues,
      unit: 'kW',
      solar: props.chartData.production[i]?.value || 0,
      house: props.chartData.consumption[i]?.value || 0,
      battery: props.chartData.battery[i]?.value || 0,
      grid: props.chartData.network[i]?.value || 0,
      batterySoc: props.chartData.batterySoc[i]?.value || 0,
    };
  }

  const batteryNetKwh = (props.chartData.battery || []).reduce((sum, d) => sum + d.value, 0) * 0.25;

  return {
    ...maxValues,
    unit: 'kW Avg',
    solar: props.stats.production.total / 24,
    house: props.stats.consumption.total / 24,
    battery: batteryNetKwh / 24,
    grid: props.stats.network.balance / 24,
    batterySoc: 50,
  };
});
</script>

<style scoped>
.card {
  background: rgba(30, 41, 59, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 0.75rem;
}

.flow-line {
  fill: none;
  stroke-width: 4;
  stroke-dasharray: 10 5;
  animation: flow-rtl 1.5s linear infinite;
}

/* Couleurs des flux */
.solar-to-house { 
  stroke: #3b82f6; 
  filter: drop-shadow(0 0 4px #3b82f6);
}

.solar-to-battery { 
  stroke: #8B5CF6; 
  filter: drop-shadow(0 0 4px #8B5CF6);
}

.battery-charge { 
  stroke: #8B5CF6; 
  filter: drop-shadow(0 0 4px #8B5CF6);
}

.battery-discharge { 
  stroke: #c084fc; 
  filter: drop-shadow(0 0 4px #c084fc);
}

.grid-inject { 
  stroke: #10b981; 
  filter: drop-shadow(0 0 4px #10b981);
}

.grid-draw { 
  stroke: #ef4444; 
  filter: drop-shadow(0 0 4px #ef4444);
}

/* Animation de dro# 📄 Fichier `EnergyFlowDiagram.vue` corrigé

```vue
<template>
  <div class="card p-4 relative">
    <h3 class="text-lg font-semibold text-white mb-4 text-center">Schéma des Flux Énergétiques</h3>
    <svg viewBox="0 0 500 350" class="w-full h-auto">
      
      <!-- Gauges (réduites et à gauche) -->
      <foreignObject x="10" y="30" width="40" height="80">
        <Gauge label="Solaire" :value="displayData.solar" :unit="displayData.unit" :max="displayData.maxSolar" positive-color="#3b82f6"/>
      </foreignObject>
      
      <foreignObject x="10" y="130" width="40" height="80">
        <Gauge label="Batterie" :value="displayData.battery" :unit="displayData.unit" :max="displayData.maxBattery" is-bidirectional positive-color="#c084fc" negative-color="#8B5CF6"/>
      </foreignObject>
      
      <foreignObject x="10" y="230" width="40" height="80">
         <Gauge label="Charge" :value="displayData.batterySoc" unit="%" :max="100" positive-color="#A78BFA" />
      </foreignObject>
      
      <foreignObject x="210" y="130" width="40" height="80">
        <Gauge label="Quartier" :value="displayData.house" :unit="displayData.unit" :max="displayData.maxHouse" positive-color="#f59e0b"/>
      </foreignObject>
      
      <foreignObject x="410" y="130" width="40" height="80">
        <Gauge label="Réseau" :value="displayData.grid" :unit="displayData.unit" :max="displayData.maxGrid" is-bidirectional/>
      </foreignObject>

      <!-- Icons (déplacés à droite des jauges) -->
      <image href="../assets/icons/solar-panel.svg" x="70" y="40" width="60" height="60" />
      <image href="../assets/icons/battery.svg" x="70" y="140" width="60" height="60" />
      <image href="../assets/icons/house.svg" x="270" y="140" width="60" height="60" />
      <image href="../assets/icons/grid.svg" x="470" y="140" width="60" height="60" />

      <!-- Static Wires (sens inversé: droite vers gauche) -->
      <!-- Solaire -> Quartier -->
      <path d="M 270 170 H 200 L 200 70 H 130" stroke="#4b5563" stroke-width="2" fill="none" />
      
      <!-- Solaire -> Batterie -->
      <path d="M 130 70 V 170" stroke="#4b5563" stroke-width="2" />
      
      <!-- Batterie -> Quartier -->
      <path d="M 130 170 H 270" stroke="#4b5563" stroke-width="2" fill="none" />
      
      <!-- Quartier -> Réseau -->
      <path d="M 330 170 H 470" stroke="#4b5563" stroke-width="2" />

      <!-- Dynamic Flows (sens inversé) -->
      <template v-if="animationStore.isPlaying">
        <!-- Solaire -> Quartier -->
        <path v-if="flows.solarToHouse" d="M 270 170 H 200 L 200 70 H 130" class="flow-line solar-to-house" />
        
        <!-- Solaire -> Batterie (charge) -->
        <path v-if="flows.solarToBattery" d="M 130 70 V 170" class="flow-line solar-to-battery" />
        
        <!-- Batterie -> Quartier (décharge) -->
        <path v-if="flows.batteryToHouse" d="M 130 170 H 270" class="flow-line battery-discharge" />
        
        <!-- Quartier -> Batterie (rare) -->
        <path v-if="flows.houseToBattery" d="M 270 170 H 130" class="flow-line battery-charge" />
        
        <!-- Réseau -> Quartier (soutirage) -->
        <path v-if="flows.gridToHouse" d="M 470 170 H 330" class="flow-line grid-draw" />
        
        <!-- Quartier -> Réseau (injection) -->
        <path v-if="flows.houseToGrid" d="M 330 170 H 470" class="flow-line grid-inject" />
      </template>

    </svg>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { animationStore } from '@/services/animationStore';
import Gauge from './Gauge.vue';

const props = defineProps({
  stats: {
    type: Object,
    required: true
  },
  chartData: {
    type: Object,
    required: true
  }
});

const flows = computed(() => {
  if (!animationStore.isPlaying || animationStore.currentIndex === null) {
    return {};
  }
  const i = animationStore.currentIndex;
  const prod = props.chartData.production[i]?.value || 0;
  const cons = props.chartData.consumption[i]?.value || 0;
  const batt = props.chartData.battery[i]?.value || 0;
  const net = props.chartData.network[i]?.value || 0;

  // Logique des flux (sens physique: production -> consommation)
  const solarToHouse = prod > 0 && cons > 0;
  const solarToBattery = prod > 0 && batt < 0; // Charge batterie
  const batteryToHouse = batt > 0 && cons > 0; // Décharge batterie
  const houseToBattery = cons < 0 && batt < 0; // Rare: surplus va en batterie
  const gridToHouse = net < 0; // Soutirage réseau
  const houseToGrid = net > 0; // Injection réseau

  return { solarToHouse, solarToBattery, batteryToHouse, houseToBattery, gridToHouse, houseToGrid };
});

const displayData = computed(() => {
  if (!props.stats) return {};

  const maxValues = {
    maxSolar: props.stats.production.max || 1,
    maxHouse: props.stats.consumption.max || 1,
    maxBattery: Math.max(...(props.chartData.battery || []).map(d => Math.abs(d.value))) || 1,
    maxGrid: Math.max(...(props.chartData.network || []).map(d => Math.abs(d.value))) || 1,
  };

  if (animationStore.isPlaying && animationStore.currentIndex !== null) {
    const i = animationStore.currentIndex;
    return {
      ...maxValues,
      unit: 'kW',
      solar: props.chartData.production[i]?.value || 0,
      house: props.chartData.consumption[i]?.value || 0,
      battery: props.chartData.battery[i]?.value || 0,
      grid: props.chartData.network[i]?.value || 0,
      batterySoc: props.chartData.batterySoc[i]?.value || 0,
    };
  }

  const batteryNetKwh = (props.chartData.battery || []).reduce((sum, d) => sum + d.value, 0) * 0.25;

  return {
    ...maxValues,
    unit: 'kW Avg',
    solar: props.stats.production.total / 24,
    house: props.stats.consumption.total / 24,
    battery: batteryNetKwh / 24,
    grid: props.stats.network.balance / 24,
    batterySoc: 50,
  };
});
</script>

<style scoped>
.card {
  background: rgba(30, 41, 59, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 0.75rem;
}

.flow-line {
  fill: none;
  stroke-width: 4;
  stroke-dasharray: 10 5;
  animation: flow-rtl 1.5s linear infinite;
}

/* Couleurs des flux */
.solar-to-house { 
  stroke: #3b82f6; 
  filter: drop-shadow(0 0 4px #3b82f6);
}

.solar-to-battery { 
  stroke: #8B5CF6; 
  filter: drop-shadow(0 0 4px #8B5CF6);
}

.battery-charge { 
  stroke: #8B5CF6; 
  filter: drop-shadow(0 0 4px #8B5CF6);
}

.battery-discharge { 
  stroke: #c084fc; 
  filter: drop-shadow(0 0 4px #c084fc);
}

.grid-inject { 
  stroke: #10b981; 
  filter: drop-shadow(0 0 4px #10b981);
}

.grid-draw { 
  stroke: #ef4444; 
  filter: drop-shadow(0 0 4px #ef4444);
}

/* Animation de droite à gauche (sens physique inversé) */
@keyframes flow-rtl {
  from {
    stroke-dashoffset: 15;
  }
  to {
    stroke-dashoffset: 0;
  }
}

/* Responsive */
@media (max-width: 768px) {
  foreignObject {
    width: 35px !important;
    height: 70px !important;
  }
  
  image {
    width: 50px !important;
    height: 50px !important;
  }
}
</style>
