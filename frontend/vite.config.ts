import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  preview: {
    port: 3000,
  },
  server: {
    host: true,
    port: 3000,
    strictPort: true,
    hmr: {
      host: '127.0.0.1',
      clientPort: 3000,
    },
    // Proxy API requests to the backend server to avoid CORS issues during development
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
