import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Durante el desarrollo, las llamadas a /api se redirigen a la API de Flask.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { '/api': 'http://127.0.0.1:5000' },
  },
})
