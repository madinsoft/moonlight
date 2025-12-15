import { animationStore } from '@/services/animationStore';

// This plugin draws a "luminous point" on each dataset's curve to indicate the current time of the animation.
export const timeIndicatorPlugin = {
  id: 'timeIndicator',
  afterDraw: (chart) => {
    // We only draw the points if the animation is playing and we have a valid index.
    if (animationStore.isPlaying && animationStore.currentIndex !== null) {
      const ctx = chart.ctx;
      
      chart.data.datasets.forEach((dataset, i) => {
        const meta = chart.getDatasetMeta(i);
        
        // Ensure the dataset is visible and has data for the current index
        if (meta.hidden || !meta.data[animationStore.currentIndex]) {
          return;
        }

        const point = meta.data[animationStore.currentIndex];
        const { x, y } = point.getProps(['x', 'y'], true);
        const pointColor = dataset.borderColor || 'rgba(255, 255, 255, 0.8)';

        // Draw the luminous point
        ctx.save();
        ctx.fillStyle = pointColor;
        ctx.shadowColor = pointColor;
        ctx.shadowBlur = 8;
        
        ctx.beginPath();
        ctx.arc(x, y, 5, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      });
    }
  }
};
