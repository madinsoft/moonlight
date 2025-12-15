<template>
  <div class="card p-4 relative">
    <h3 class="text-lg font-semibold text-white mb-4 text-center">Schéma des Flux Énergétiques</h3>
    <svg viewBox="0 0 400 300" class="w-full h-auto">
      
      <!-- Gauges -->
      <foreignObject x="10" y="20" width="50" height="120">
        <Gauge label="Solaire" :value="displayData.solar" :unit="displayData.unit" :max="displayData.maxSolar" positive-color="#3b82f6"/>
      </foreignObject>
      <foreignObject x="340" y="20" width="50" height="120">
        <Gauge label="Batterie" :value="displayData.battery" :unit="displayData.unit" :max="displayData.maxBattery" is-bidirectional positive-color="#c084fc" negative-color="#8B5CF6"/>
      </foreignObject>
      <foreignObject x="270" y="20" width="50" height="120">
         <Gauge label="Charge" :value="displayData.batterySoc" unit="%" :max="100" positive-color="#A78BFA" />
      </foreignObject>
      <foreignObject x="10" y="150" width="50" height="120">
        <Gauge label="Quartier" :value="displayData.house" :unit="displayData.unit" :max="displayData.maxHouse" positive-color="#f59e0b"/>
      </foreignObject>
      <foreignObject x="10" y="250" width="50" height="120">
        <Gauge label="Réseau" :value="displayData.grid" :unit="displayData.unit" :max="displayData.maxGrid" is-bidirectional/>
      </foreignObject>

      <!-- Icons -->
      <image href="../assets/icons/solar-panel.svg" x="70" y="50" width="50" height="50" />
      <image href="../assets/icons/battery.svg" x="280" y="50" width="50" height="50" />
      <image href="../assets/icons/house.svg" x="175" y="125" width="50" height="50" />
      <image href="../assets/icons/grid.svg" x="175" y="225" width="50" height="50" />

      <!-- Static Wires -->
      <path d="M120 75 H 180 L 180 125 H 200" stroke="#4b5563" stroke-width="2" fill="none" /> <!-- Solar to House -->
      <path d="M120 75 H 280" stroke="#4b5563" stroke-width="2" /> <!-- Solar to Battery -->
      <path d="M280 75 H 220 L 220 125 H 200" stroke="#4b5563" stroke-width="2" fill="none" /> <!-- Battery to House -->
      <path d="M200 175 V 225" stroke="#4b5563" stroke-width="2" /> <!-- House to Grid -->

      <!-- Dynamic Flows -->
      <template v-if="animationStore.isPlaying">
        <!-- Solar -> House -->
        <path v-if="flows.solarToHouse" d="M120 75 H 180 L 180 125 H 200" class="flow-line solar" />
        <!-- Solar -> Battery -->
        <path v-if="flows.solarToBattery" d="M120 75 H 280" class="flow-line solar" />
        <!-- Battery -> House -->
        <path v-if="flows.batteryToHouse" d="M280 75 H 220 L 220 125 H 200" class="flow-line battery-discharge" />
        <!-- House -> Battery -->
        <path v-if="flows.houseToBattery" d="M200 125 H 220 L 220 75 H 280" class="flow-line battery-charge" />
        <!-- Grid -> House -->
        <path v-if="flows.gridToHouse" d="M200 225 V 175" class="flow-line grid-draw" />
        <!-- House -> Grid -->
        <path v-if="flows.houseToGrid" d="M200 175 V 225" class="flow-line grid-inject" />
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

  // Simplified flow logic based on new connections
  const solarToHouse = prod > 0 && cons > 0;
  const solarToBattery = prod > 0 && batt < 0;
  const batteryToHouse = batt > 0 && cons > 0;
  const houseToBattery = cons < 0 && batt < 0; // Less common, but possible
  const gridToHouse = net < 0;
  const houseToGrid = net > 0;

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
.flow-line {
  fill: none;
  stroke-width: 4;
  stroke-dasharray: 8 4;
  animation: flow 1s linear infinite;
}
.solar { stroke: #3b82f6; }
.consumption { stroke: #f59e0b; }
.battery-charge { stroke: #8B5CF6; }
.battery-discharge { stroke: #c084fc; }
.grid-inject { stroke: #10b981; }
.grid-draw { stroke: #ef4444; }

@keyframes flow {
  from {
    stroke-dashoffset: 0;
  }
  to {
    stroke-dashoffset: 12;
  }
}
</style>
