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
  datasets: [{
    label: 'Production (kW)',
    data: props.data.map(d => d.value),
    borderColor: '#60a5fa',
    backgroundColor: 'rgba(96, 165, 250, 0.1)',
    fill: true,
    tension: 0.4,
    pointRadius: 0,
    pointHoverRadius: 5,
    borderWidth: 2
  }]
}))

const chartOptions = computed(() => getChartConfig('production'))
</script>
