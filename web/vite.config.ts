import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  // Relative, so the build works wherever FastAPI mounts it.
  base: './',
  plugins: [react()],
  // In development the panel runs on 5173 and the API on 8000; in production
  // FastAPI serves both from one origin, which is why every request is /api/...
  server: { proxy: { '/api': 'http://127.0.0.1:8000' } },
  test: { environment: 'jsdom', globals: true, css: false, setupFiles: './src/test/setup.ts' },
});
