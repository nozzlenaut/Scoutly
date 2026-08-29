import type { MetadataRoute } from "next";
import { getPublicKehCameraCatalog } from "@/lib/api";
import { allIndexedProducts } from "@/lib/allIndexedProducts";
import { buyingGuides } from "@/lib/buyingGuides";
import { popularBooks } from "@/lib/popularBooks";

export const revalidate = 21600;

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = "https://www.pricesift.app";
  const routes: MetadataRoute.Sitemap = [
    { url: baseUrl },
    { url: `${baseUrl}/cameras` },
    { url: `${baseUrl}/lenses` },
    { url: `${baseUrl}/used` },
    { url: `${baseUrl}/used/market` },
    { url: `${baseUrl}/used/noise` },
    { url: `${baseUrl}/used/retro-game-consoles` },
    { url: `${baseUrl}/used/current-game-consoles` },
    { url: `${baseUrl}/used/popular-books` },
    { url: `${baseUrl}/buying-guides` },
    { url: `${baseUrl}/buying-guides/used-listing-red-flags` },
    { url: `${baseUrl}/reuse` },
    { url: `${baseUrl}/feedback` },
    { url: `${baseUrl}/disclosure` },
    ...buyingGuides.map((guide) => ({
      url: `${baseUrl}/buying-guides/${guide.slug}`,
    })),
    ...allIndexedProducts.map((product) => ({
      url: `${baseUrl}/used/${product.slug}`,
    })),
    ...popularBooks.map((book) => ({
      url: `${baseUrl}/used/${book.slug}`,
    })),
  ];

  try {
    const cameraData = await getPublicKehCameraCatalog({ limit: 1000, revalidateSeconds: revalidate });
    routes.push(
      ...cameraData.models.map((model) => ({
        url: `${baseUrl}/cameras/${model.slug}`,
      })),
    );
  } catch {
    // Keep stable sitemap routes available during a feed sync or backend outage.
  }

  return routes;
}
