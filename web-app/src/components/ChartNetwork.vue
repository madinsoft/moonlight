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
  networkData: {
    type: Array,
    default: () => []
  },
  batteryData: {
    type: Array,
    default: () => []
  }
})

const chartData = computed(() => {
  const labels = props.networkData.map(d => d.time);
  
  return {
    labels: labels,
    datasets: [
      {
        label: 'Batterie (kW)',
        data: props.batteryData.map(d => d.value),
        borderColor: '#8B5CF6', // Purple
        backgroundColor: 'rgba(139, 92, 246, 0.2)',
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.3,
        fill: true,
      },
      {
        label: 'Réseau (kW)',
        data: props.networkData.map(d => d.value),
        borderColor: '#4ade80',
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.3,
        segment: {
            borderColor: ctx => (ctx.p1.raw >= 0 ? '#10B981' : '#EF4444'),
        }
      }
    ]
  }
})

const chartOptions = computed(() => {
    const config = getChartConfig('network');
    
    // Customization for this specific chart
    config.plugins.legend = {
        display: true,
        position: 'top',
        labels: {
            color: '#9ca3af',
            font: { size: 12 },
            boxWidth: 15,
            padding: 20
        }
    };

    config.scales.y.title = {
      display: true,
      text: 'Puissance (kW)',
      color: '#9ca3af',
      font: {
        size: 12,
        weight: 'bold'
      }
    }

    // Modify tooltip to handle multiple datasets
    config.plugins.tooltip.displayColors = true;
    config.plugins.tooltip.callbacks.label = function(context) {
      const label = context.dataset.label || '';
      const value = context.parsed.y;
      let valueText = '';
      if (label.includes('Réseau')) {
        valueText = (value >= 0 ? 'Injection: +' : 'Soutirage: ') + Math.abs(value).toFixed(2) + ' kW';
      } else if (label.includes('Batterie')) {
        valueText = (value <= 0 ? 'Charge: ' : 'Décharge: ') + Math.abs(value).toFixed(2) + ' kW';
      } else {
        valueText = value.toFixed(2) + ' kW';
      }
      return `${label}: ${valueText}`;
    };


    return config;
})
</script>
