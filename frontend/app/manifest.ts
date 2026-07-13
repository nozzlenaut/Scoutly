import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "PriceSift",
    short_name: "PriceSift",
    description: "Find cleaner used listings and better prices for the exact item you already want.",
    start_url: "/",
    display: "standalone",
    background_color: "#020617",
    theme_color: "#083344",
    icons: [
      {
        src: "/icon.svg",
        sizes: "any",
        type: "image/svg+xml",
      },
    ],
  };
}
