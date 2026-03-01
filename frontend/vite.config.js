import { defineConfig } from "vite";

export default defineConfig(({ command }) => ({
  // Render static-site deployment expects built assets at /assets/*.
  base: "/",
  esbuild: {
    jsxInject: 'import React from "react"'
  },
  server: {
    host: "127.0.0.1",
    port: 5174,
    strictPort: true,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true
      }
    }
  }
}));
