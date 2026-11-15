// @ts-check
import { defineConfig } from "astro/config";

// De oude Kirby-site had adressen zonder slash (/koorscholing): die houden we aan.
export default defineConfig({
  site: "https://www.annemiekmaissan.nl",
  trailingSlash: "never",
  build: { format: "file" },
  image: {
    service: {
      entrypoint: "astro/assets/services/sharp",
      config: { avif: { effort: 2 }, webp: { effort: 3 } },
    },
  },
});
