<template>
  <div class="relative h-80">
    <Line :chart-id="'chart-consumption'" ref="chartRef" :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
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
import { timeIndicatorPlugin } from '@/services/timeIndicatorPlugin'
import { animationStore } from '@/services/animationStore'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler,
  timeIndicatorPlugin
)

const props = defineProps({
  data: {
    type: Array,
    required: true,
    default: () => []
  }
})

const chartRef = ref(null);

const chartData = computed(() => ({
  labels: props.data.map(d => d.time),
  datasets: [
    {
      label: 'Consommation (kW)',
      data: props.data.map(d => d.value),
      borderColor: '#f59e0b',
      backgroundColor: 'rgba(245, 158, 11, 0.1)',
      borderWidth: 2,
      fill: true,
      tension: 0.4,
      pointRadius: 0,
      pointHoverRadius: 4,
    }
  ]
}))

const chartOptions = computed(() => getChartConfig('consumption'))

watch(() => animationStore.currentIndex, () => {
  if (chartRef.value) {
    chartRef.value.chart.update('none');
  }
});
</script>