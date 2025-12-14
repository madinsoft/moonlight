export function getChartConfig(type) {
  const baseConfig = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false
    },
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(26, 31, 46, 0.95)',
        titleColor: '#f3f4f6',
        bodyColor: '#f3f4f6',
        borderColor: '#2d3748',
        borderWidth: 1,
        padding: 12,
        displayColors: false,
        callbacks: {
          label: function(context) {
            return `${context.parsed.y.toFixed(2)} kW`
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(45, 55, 72, 0.5)',
          drawBorder: false
        },
        ticks: {
          color: '#9ca3af',
          maxRotation: 0,
          autoSkip: true,
          maxTicksLimit: 12,
          font: {
            size: 11
          }
        }
      },
      y: {
        grid: {
          color: 'rgba(45, 55, 72, 0.5)',
          drawBorder: false
        },
        ticks: {
          color: '#9ca3af',
          font: {
            size: 11
          },
          callback: function(value) {
            return value.toFixed(0) + ' kW'
          }
        }
      }
    }
  }

  // Configuration spécifique par type
  if (type === 'network') {
    baseConfig.scales.y.ticks.callback = function(value) {
      return (value >= 0 ? '+' : '') + value.toFixed(0) + ' kW'
    }
    baseConfig.plugins.tooltip.callbacks.label = function(context) {
      const value = context.parsed.y
      const label = value >= 0 ? 'Injection: +' : 'Soutirage: '
      return label + Math.abs(value).toFixed(2) + ' kW'
    }
  }

  if (type === 'batterySoc') {
    baseConfig.scales.y.ticks.callback = function(value) {
        return value.toFixed(0) + ' %';
    };
    baseConfig.plugins.tooltip.callbacks.label = function(context) {
        return `Charge: ${context.parsed.y.toFixed(1)} %`;
    };
  }

  return baseConfig
}