<template>
  <div class="card p-4 flex items-center justify-center space-x-6">
    <button @click="handlePlay" :disabled="animationStore.isPlaying" class="btn-icon" aria-label="Play Animation">
      <img src="../assets/icons/play.svg" class="w-8 h-8" alt="Play"/>
    </button>
    <button @click="handleStop" :disabled="!animationStore.isPlaying" class="btn-icon" aria-label="Stop Animation">
      <img src="../assets/icons/stop.svg" class="w-8 h-8" alt="Stop"/>
    </button>
    <div v-if="animationStore.currentIndex !== null" class="text-lg text-white font-mono">
      Heure: {{ currentTime }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { animationStore } from '@/services/animationStore';

const props = defineProps({
  timeLabels: {
    type: Array,
    required: true
  }
});

const currentTime = computed(() => {
  if (animationStore.currentIndex !== null && props.timeLabels[animationStore.currentIndex]) {
    return props.timeLabels[animationStore.currentIndex];
  }
  return '00:00';
});

const handlePlay = () => {
  animationStore.play(props.timeLabels.length);
};

const handleStop = () => {
  animationStore.stop();
};
</script>

<style scoped>
.btn-icon {
  @apply p-2 bg-dark-border rounded-full transition-colors duration-200;
}
.btn-icon:not(:disabled) {
  @apply hover:bg-blue-primary;
}
.btn-icon:disabled {
  @apply opacity-50 cursor-not-allowed;
}
</style>
