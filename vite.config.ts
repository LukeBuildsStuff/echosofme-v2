import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: '0.0.0.0',  // Listen on all interfaces (IPv4 and IPv6)
    port: 5173,
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      '192.168.150.117',  // Your network IP
      'echosofme.io',
      '.trycloudflare.com'  // Allow all trycloudflare.com subdomains
    ],
    proxy: {
      '/api': {
        target: 'http://localhost:8504',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
