<template>
  <div class="card overflow-hidden">
    <div class="p-6 pb-4 border-b border-dark-border">
      <div class="flex items-start justify-between">
        <div class="flex items-center gap-3">
          <div :class="['p-2.5 rounded-lg', `bg- $ {color}-primary bg-opacity-20`]">
            <component :is="iconComponent" :class="['w-6 h-6', `text- $ {color}-${color === 'yellow' ? 'primary' : 'accent'}`]" />
          </div>
          <div>
            <h3 class="text-lg font-semibold text-white">{{ title }}</h3>
            <p v-if="subtitle" class="text-sm text-gray-light mt-0.5">{{ subtitle }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="p-6">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: String,
  subtitle: String,
  icon: String,
  color: {
    type: String,
    default: 'blue'
  }
})

const iconComponent = computed(() => {
  const icons = {
    sun: {
      template: `
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
      `
    },
    home: {
      template: `
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
      `
    },
    activity: {
      template: `
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
      `
    }
  }
  
  return icons[props.icon] || icons.sun
})
</script>
