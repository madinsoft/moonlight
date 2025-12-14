<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    <!-- Production -->
    <div class="card p-5">
      <div class="flex items-start justify-between mb-3">
        <div class="p-2 bg-blue-primary bg-opacity-20 rounded-lg">
          <svg class="w-6 h-6 text-blue-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        </div>
        <span class="text-xs text-gray-light">kWh</span>
      </div>
      <div class="mb-1">
        <div class="text-2xl font-bold text-white">{{ stats.production.total.toFixed(1) }}</div>
        <div class="text-sm text-gray-light">Production totale</div>
      </div>
      <div class="text-xs text-gray-medium">
        Max: {{ stats.production.max.toFixed(1) }} kW à {{ stats.production.maxTime }}
      </div>
    </div>

    <!-- Consommation -->
    <div class="card p-5">
      <div class="flex items-start justify-between mb-3">
        <div class="p-2 bg-yellow-primary bg-opacity-20 rounded-lg">
          <svg class="w-6 h-6 text-yellow-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
        </div>
        <span class="text-xs text-gray-light">kWh</span>
      </div>
      <div class="mb-1">
        <div class="text-2xl font-bold text-white">{{ stats.consumption.total.toFixed(1) }}</div>
        <div class="text-sm text-gray-light">Consommation totale</div>
      </div>
      <div class="text-xs text-gray-medium">
        Max: {{ stats.consumption.max.toFixed(1) }} kW à {{ stats.consumption.maxTime }}
      </div>
    </div>

    <!-- Bilan -->
    <div class="card p-5">
      <div class="flex items-start justify-between mb-3">
        <div :class="['p-2 rounded-lg', stats.network.balance >= 0 ? 'bg-green-primary bg-opacity-20' : 'bg-red-primary bg-opacity-20']">
          <svg class="w-6 h-6" :class="stats.network.balance >= 0 ? 'text-green-primary' : 'text-red-primary'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
        </div>
        <span class="text-xs text-gray-light">kWh</span>
      </div>
      <div class="mb-1">
        <div class="text-2xl font-bold text-white">{{ Math.abs(stats.network.balance).toFixed(1) }}</div>
        <div class="text-sm text-gray-light">
          {{ stats.network.balance >= 0 ? 'Injection réseau' : 'Soutirage réseau' }}
        </div>
      </div>
      <div class="text-xs text-gray-medium">
        {{ stats.network.balance >= 0 ? 'Excédent' : 'Déficit' }} énergétique
      </div>
    </div>

    <!-- Autoproduction -->
    <div class="card p-5">
      <div class="flex items-start justify-between mb-3">
        <div class="p-2 bg-blue-secondary bg-opacity-20 rounded-lg">
          <svg class="w-6 h-6 text-blue-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <span class="text-xs text-gray-light">%</span>
      </div>
      <div class="mb-1">
        <div class="text-2xl font-bold text-white">{{ stats.selfConsumption.toFixed(0) }}%</div>
        <div class="text-sm text-gray-light">Autoconsommation</div>
      </div>
      <div class="text-xs text-gray-medium">
        Part de production consommée localement
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  stats: {
    type: Object,
    required: true
  }
})
</script>
