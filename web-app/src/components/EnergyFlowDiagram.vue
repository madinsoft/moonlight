<template>
  <div class="card p-4">
    <h3 class="text-lg font-semibold text-white mb-4 text-center">Schéma des Flux Énergétiques</h3>
    <svg viewBox="0 0 400 300" class="w-full h-auto">
      <!-- Icons -->
      <image href="../assets/icons/solar-panel.svg" x="160" y="10" width="80" height="80" />
      <image href="../assets/icons/house.svg" x="30" y="110" width="80" height="80" />
      <image href="../assets/icons/battery.svg" x="290" y="110" width="80" height="80" />
      <image href="../assets/icons/grid.svg" x="160" y="210" width="80" height="80" />

      <!-- Center Junction -->
      <circle cx="200" cy="150" r="5" fill="#4b5563" />

      <!-- Static Wires -->
      <path d="M200 90 V 145" stroke="#4b5563" stroke-width="2" /> <!-- Solar to Center -->
      <path d="M110 150 H 195" stroke="#4b5563" stroke-width="2" /> <!-- House to Center -->
      <path d="M205 150 H 290" stroke="#4b5563" stroke-width="2" /> <!-- Center to Battery -->
      <path d="M200 155 V 210" stroke="#4b5563" stroke-width="2" /> <!-- Center to Grid -->
      
      <!-- Dynamic Flows -->
      <!-- Solar to Center -->
      <path v-if="flows.solarToCenter" d="M200 90 V 145" class="flow-line solar" />
      
      <!-- Center to House -->
      <path v-if="flows.centerToHouse" d="M195 150 H 110" class="flow-line consumption" />

      <!-- Center to Battery (Charging) -->
      <path v-if="flows.centerToBattery" d="M205 150 H 290" class="flow-line battery-charge" />
      
      <!-- Battery to Center (Discharging) -->
      <path v-if="flows.batteryToCenter" d="M290 150 H 205" class="flow-line battery-discharge" />

      <!-- Center to Grid (Injection) -->
      <path v-if="flows.centerToGrid" d="M200 155 V 210" class="flow-line grid-inject" />

      <!-- Grid to Center (Drawing) -->
      <path v-if="flows.gridToCenter" d="M200 210 V 155" class="flow-line grid-draw" />
    </svg>
  </div>
</template>

<script setup>
import { computed } from 'vue';

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
  if (!props.stats || !props.chartData) {
    return {};
  }

  const { production, consumption, network } = props.stats;
  const batteryFlows = props.chartData.battery || [];
  
  const batteryChargeTotal = batteryFlows.filter(d => d.value < 0).reduce((sum, d) => sum + Math.abs(d.value), 0);
  const batteryDischargeTotal = batteryFlows.filter(d => d.value > 0).reduce((sum, d) => sum + d.value, 0);

  return {
    solarToCenter: production.total > 0,
    centerToHouse: consumption.total > 0,
    centerToBattery: batteryChargeTotal > batteryDischargeTotal,
    batteryToCenter: batteryDischargeTotal > batteryChargeTotal,
    centerToGrid: network.balance > 0,
    gridToCenter: network.balance < 0,
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
