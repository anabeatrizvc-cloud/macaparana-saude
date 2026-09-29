import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "/build/",
  publicDir: false,
  build: { outDir: "../static/build", emptyOutDir: true },
  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        configure(proxy) {
          proxy.on("proxyReq", (request) =>
            request.setHeader("Origin", "http://127.0.0.1:8000"),
          );
        },
      },
      "/docs": "http://127.0.0.1:8000",
      "/mark.svg": "http://127.0.0.1:8000",
    },
  },
});
