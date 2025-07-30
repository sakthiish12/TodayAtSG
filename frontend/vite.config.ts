import { fileURLToPath, URL } from 'node:url'

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig(({ command, mode }) => {
  // Load env file based on `mode` in the current working directory.
  // Set the third parameter to '' to load all env regardless of the `VITE_` prefix.
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    plugins: [
      vue(),
      // Only use devtools in development
      ...(mode === 'development' ? [vueDevTools()] : []),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      },
    },
    define: {
      // Define global constants for environment variables
      __VUE_PROD_DEVTOOLS__: mode === 'development',
      __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: mode === 'development',
    },
    build: {
      outDir: 'dist',
      assetsDir: 'static',
      sourcemap: mode === 'development',
      minify: mode === 'production' ? 'esbuild' : false,
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['vue', 'vue-router', 'pinia'],
            maps: ['@googlemaps/js-api-loader', '@googlemaps/markerclusterer'],
            ui: ['lucide-vue-next', '@vueuse/core'],
          }
        }
      },
      // Optimize chunk size for better loading performance
      chunkSizeWarningLimit: 1000,
    },
    server: {
      port: 5173,
      host: true,
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        }
      }
    },
    preview: {
      port: 4173,
      host: true,
    },
    // Environment variables configuration
    envPrefix: 'VITE_',
  }
})
