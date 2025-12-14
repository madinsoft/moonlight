<template>
  <div class="chart-container">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler
} from 'chart.js'
import { getChartConfig } from '../services/chartConfig'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler
)

const props = defineProps({
  data: {
    type: Array,
    required: true,
    default: () => []
  }
})

const chartData = computed(() => ({
  labels: props.data.map(d => d.time),
  datasets: [
    {
      label: 'Production',
      data: props.data.map(d => d.value),
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      borderWidth: 2,
      fill: true,
      tension: 0.4,
      pointRadius: 0,
      pointHoverRadius: 4,
      pointHoverBackgroundColor: '#3b82f6',
      pointHoverBorderColor: '#fff',
      pointHoverBorderWidth: 2
    }
  ]
}))

const chartOptions = computed(() => getChartConfig('production'))
</script>

<style scoped>
.chart-container {
  position: relative;
  height: 100%;
  min-height: 300px;
}
</style>