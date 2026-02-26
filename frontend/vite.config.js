import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/auth': 'http://127.0.0.1:8000',
      '/chat': 'http://127.0.0.1:8000',
      '/api': 'http://127.0.0.1:8000',
      '/profile': 'http://127.0.0.1:8000',
      '/edit': 'http://127.0.0.1:8000',
      '/translate': 'http://127.0.0.1:8000'
    }
  },
  test: {
    globals: true,
    include: ['src/**/*.test.{js,jsx,ts,tsx}'],
    environment: 'jsdom',
    setupFiles: './src/tests/setup.js',
    coverage: {
      reporter: ['text', 'json-summary'],
      include: ['src/components/**/*.jsx']
    }
  }
});
