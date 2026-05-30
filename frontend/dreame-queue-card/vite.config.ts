import { resolve } from "node:path";
import { defineConfig } from "vite";

export default defineConfig({
  build: {
    target: "es2020",
    sourcemap: false,
    outDir: "../../custom_components/ha_dreame/frontend",
    emptyOutDir: true,
    rollupOptions: {
      input: {
        "ha-dreame-queue-card": resolve(__dirname, "src/ha-dreame-queue-card.ts"),
      },
      output: {
        entryFileNames: "[name].js",
        chunkFileNames: "[name]-[hash].js",
        assetFileNames: "[name]-[hash][extname]",
      },
    },
  },
});
