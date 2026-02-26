import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  timeout: 60000,
  webServer: [
    {
      command: 'APP_TEST_MODE=1 python3 -m uvicorn backend.app:app --host 127.0.0.1 --port 8000',
      url: 'http://127.0.0.1:8000/health',
      reuseExistingServer: true,
      cwd: '..'
    },
    {
      command: 'npm run dev -- --host 127.0.0.1 --port 5173',
      url: 'http://127.0.0.1:5173',
      reuseExistingServer: true
    }
  ],
  use: {
    baseURL: 'http://127.0.0.1:5173',
    headless: true
  }
});
