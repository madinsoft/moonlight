<template>
  <div class="relative h-80">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js'
import { getChartConfig } from '@/services/chartConfig'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  }
})

const chartData = computed(() => ({
  labels: props.data.map(d => d.time),
  datasets: [
    {
      label: 'État de charge (%)',
      data: props.data.map(d => d.value),
      borderColor: '#A78BFA', // A lighter purple
      backgroundColor: 'rgba(167, 139, 250, 0.2)',
      borderWidth: 2,
      pointRadius: 0,
      tension: 0.3,
      fill: true,
    }
  ]
}))

const chartOptions = computed(() => {
    const config = getChartConfig('batterySoc'); // Using a new config type
    
    config.scales.y.min = 0;
    config.scales.y.max = 100;
    config.scales.y.ticks.callback = function(value) {
        return value.toFixed(0) + ' %';
    };

    config.plugins.tooltip.callbacks.label = function(context) {
        return `Charge: ${context.parsed.y.toFixed(1)} %`;
    };

    return config;
})
</script>
