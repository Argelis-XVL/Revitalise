import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// Shape prescribed by knowledge/technology/code-apps.md -> "Vite Configuration".
// `base: "./"` and port 3000 are required by the Power Apps local host; port 3000
// also matches `localAppUrl` in power.config.json, which `pac code init` wrote.
export default defineConfig({
  plugins: [react()],
  base: "./",
  server: {
    host: "::",
    port: 3000,
  },
  build: {
    outDir: "dist", // matches power.config.json -> buildPath "./dist"
    sourcemap: false, // never ship sourcemaps to a shared environment
  },
});
