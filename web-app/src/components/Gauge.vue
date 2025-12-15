<template>
  <div class="flex flex-col items-center w-12 text-xs">
    <!-- Value Display -->
    <div class="font-mono font-bold text-white order-1 text-sm">{{ value.toFixed(1) }}</div>
    <div class="text-gray-400 order-2 text-[10px]">{{ unit }}</div>

    <!-- Vertical Bar -->
    <div class="w-3 h-[50px] bg-dark-border rounded-full my-1 flex order-3" :class="isBidirectional ? 'flex-col' : 'flex-col-reverse'">
      <!-- Positive Bar -->
      <div class="w-full rounded-full" 
           :style="{ height: positiveHeight, backgroundColor: barColor }">
      </div>
      <!-- Negative Bar (for bidirectional) -->
      <div v-if="isBidirectional" 
           class="w-full rounded-full"
           :style="{ height: negativeHeight, backgroundColor: negativeColor }">
      </div>
    </div>

    <!-- Label -->
    <div class="font-semibold text-gray-300 order-4 text-center text-[11px]">{{ label }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  label: { type: String, required: true },
  value: { type: Number, default: 0 },
  unit: { type: String, default: 'kW' },
  max: { type: Number, default: 100 },
  isBidirectional: { type: Boolean, default: false },
  positiveColor: { type: String, default: '#10b981' },
  negativeColor: { type: String, default: '#ef4444' }
});

const positiveHeight = computed(() => {
  if (props.value >= 0) {
    const percentage = Math.min(100, (props.value / Math.max(1, props.max)) * 100);
    return props.isBidirectional ? `${percentage / 2}%` : `${percentage}%`;
  }
  return props.isBidirectional ? '50%' : '0%';
});

const negativeHeight = computed(() => {
  if (props.isBidirectional && props.value < 0) {
    const percentage = Math.min(100, (Math.abs(props.value) / Math.max(1, props.max)) * 100);
    return `${percentage / 2}%`;
  }
  return '0%';
});

const barColor = computed(() => {
  if (props.isBidirectional) {
    return props.positiveColor; // In bidirectional, top is always positive color
  }
  return props.value >= 0 ? props.positiveColor : props.negativeColor;
});
</script>
