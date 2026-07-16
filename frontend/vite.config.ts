import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'node:path'

export default defineConfig(({ mode }) => {
  const envDir = path.resolve(__dirname, '..')
  const env = loadEnv(mode, envDir, '')
  const apiTarget = env.VITE_DEV_API_TARGET

  return {
    envDir,
    plugins: [react(), tailwindcss()],
    server: apiTarget
      ? {
          proxy: {
            '/chat': apiTarget,
            '/files': apiTarget,
            '/paper-analyses': apiTarget,
            '/papers': apiTarget,
          },
        }
      : undefined,
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
  }
})
