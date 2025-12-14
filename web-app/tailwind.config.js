/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#0f1419',
          card: '#1a1f2e',
          border: '#2d3748',
        },
        blue: {
          primary: '#3b82f6',
          secondary: '#1e40af',
          accent: '#60a5fa',
        },
        gray: {
          light: '#9ca3af',
          medium: '#6b7280',
          dark: '#374151',
        }
      }
    },
  },
  plugins: [],
}
