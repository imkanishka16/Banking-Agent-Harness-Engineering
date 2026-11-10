import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    // Calls to /api go to FastAPI, so the browser never makes a cross-origin request
    proxy: { "/api": "http://localhost:8000" },
  },
});