import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000, // React runs on http://localhost:3000

    // Proxy API calls to the FastAPI backend.
    // When the frontend calls "/api/auth/login", Vite forwards it
    // to "http://localhost:8000/auth/login" behind the scenes.
    // This avoids CORS issues during development.
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
