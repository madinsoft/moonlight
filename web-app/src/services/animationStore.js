import { reactive } from 'vue';

export const animationStore = reactive({
  isPlaying: false,
  currentIndex: null,
  timer: null,
  animationSpeed: 200, // ms per step

  play(totalSteps) {
    if (this.isPlaying) {
      return;
    }

    this.isPlaying = true;
    this.currentIndex = this.currentIndex !== null ? this.currentIndex : 0;

    this.timer = setInterval(() => {
      if (this.currentIndex < totalSteps - 1) {
        this.currentIndex++;
      } else {
        this.stop();
      }
    }, this.animationSpeed);
  },

  stop() {
    clearInterval(this.timer);
    this.timer = null;
    this.isPlaying = false;
    this.currentIndex = null;
  }
});
