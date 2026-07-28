import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: '/WEOS/',
  build: {
    outDir: 'dist',
    chunkSizeWarningLimit: 600,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('three')) {
            return 'three-vendor'
          }

          if (id.includes('world-atlas') || id.includes('topojson-client')) {
            return 'globe-data'
          }

          if (id.includes('react')) {
            return 'react-vendor'
          }
        },
      },
    },
  },
})
