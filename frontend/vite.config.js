import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Saat `npm run dev`, semua request /api diteruskan ke FastAPI (uvicorn, port 8000).
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
  build: { outDir: 'dist' },
})
