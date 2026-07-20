import type { MetadataRoute } from "next";
import { getPublicKehCameraCatalog } from "@/lib/api";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = "https://www.pricesift.app";
  const routes: MetadataRoute.Sitemap = [
    { url: baseUrl, changeFrequency: "weekly", priority: 1 },
    { url: `${baseUrl}/cameras`, changeFrequency: "daily", priority: 0.9 },
    { url: `${baseUrl}/lenses`, changeFrequency: "daily", priority: 0.8 },
    { url: `${baseUrl}/feedback`, changeFrequency: "monthly", priority: 0.5 },
    { url: `${baseUrl}/disclosure`, changeFrequency: "yearly", priority: 0.3 },
  ];
  try {
    const cameraData = await getPublicKehCameraCatalog({ limit: 1000 });
    routes.push(
      ...cameraData.models.map((model) => ({
        url: `${baseUrl}/cameras/${model.slug}`,
        changeFrequency: "daily" as const,
        priority: model.provider_scope === "ebay_keh" ? 0.8 : 0.7,
      })),
    );
  } catch {
    // Keep the stable sitemap routes available during a feed sync or backend outage.
  }
  return routes;
}
