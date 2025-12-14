import { animationStore } from '@/services/animationStore';

// This plugin draws a vertical line on the chart to indicate the current time of the animation.
export const timeIndicatorPlugin = {
  id: 'timeIndicator',
  afterDraw: (chart) => {
    // We only draw the line if the animation is playing and we have a valid index.
    if (animationStore.isPlaying && animationStore.currentIndex !== null) {
      const ctx = chart.ctx;
      const xAxis = chart.scales.x;
      const yAxis = chart.scales.y;
      
      // Get the x-coordinate for the current animation index.
      const x = xAxis.getPixelForValue(animationStore.currentIndex);

      // Draw the vertical line.
      ctx.save();
      ctx.beginPath();
      ctx.moveTo(x, yAxis.top);
      ctx.lineTo(x, yAxis.bottom);
      ctx.lineWidth = 2;
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)';
      ctx.shadowColor = 'rgba(255, 255, 255, 1)';
      ctx.shadowBlur = 5;
      ctx.stroke();
      ctx.restore();
    }
  }
};
