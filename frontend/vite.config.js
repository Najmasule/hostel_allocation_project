import { defineConfig } from "vite";

export default defineConfig(({ command }) => ({
  // Use root path in dev so React routes work, but keep /static/ assets for Django build.
  base: command === "serve" ? "/" : "/static/",
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
