import { defineConfig, transformWithOxc } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [
    {
      name: "treat-app-js-as-jsx",
      enforce: "pre",
      async transform(code, id) {
        if (!id.endsWith("/app.js")) return null;
        return transformWithOxc(code, id, {
          lang: "jsx",
          jsx: { runtime: "automatic" },
        });
      },
    },
    react(),
  ],
});
