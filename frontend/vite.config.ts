import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), 'VITE_')
  const backend = (env.VITE_API_BASE_URL ?? '').replace(/\/+$/, '')

  return {
    plugins: [react()],
    server: {
      port: 5173,
      ...(backend
        ? {
            proxy: {
              '/api': {
                target: backend,
                changeOrigin: true,
                ws: true,
              },
            },
          }
        : {}),
    },
  }
})
