import type { MetadataRoute } from "next";
import { getPublicKehCameraCatalog } from "@/lib/api";
import { buyingGuides } from "@/lib/buyingGuides";
import { indexedProducts } from "@/lib/indexedProducts";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = "https://www.pricesift.app";
  const routes: MetadataRoute.Sitemap = [
    { url: baseUrl, changeFrequency: "weekly", priority: 1 },
    { url: `${baseUrl}/cameras`, changeFrequency: "daily", priority: 0.9 },
    { url: `${baseUrl}/lenses`, changeFrequency: "daily", priority: 0.8 },
    { url: `${baseUrl}/used`, changeFrequency: "weekly", priority: 0.8 },
    { url: `${baseUrl}/buying-guides`, changeFrequency: "monthly", priority: 0.8 },
    { url: `${baseUrl}/reuse`, changeFrequency: "monthly", priority: 0.75 },
    { url: `${baseUrl}/feedback`, changeFrequency: "monthly", priority: 0.5 },
    { url: `${baseUrl}/disclosure`, changeFrequency: "yearly", priority: 0.3 },
    ...buyingGuides.map((guide) => ({
      url: `${baseUrl}/buying-guides/${guide.slug}`,
      changeFrequency: "monthly" as const,
      priority: guide.categoryId === "cameras" ? 0.8 : 0.7,
    })),
    ...indexedProducts.map((product) => ({
      url: `${baseUrl}/used/${product.slug}`,
      changeFrequency: "daily" as const,
      priority: 0.75,
    })),
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
