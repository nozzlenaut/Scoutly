import type { MetadataRoute } from "next";
import { getPublicKehCameraCatalog } from "@/lib/api";
import { allIndexedProducts, findAllIndexedCameraProduct } from "@/lib/allIndexedProducts";
import { buyingGuides } from "@/lib/buyingGuides";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = "https://www.pricesift.app";
  const routes: MetadataRoute.Sitemap = [
    { url: baseUrl },
    { url: `${baseUrl}/cameras` },
    { url: `${baseUrl}/lenses` },
    { url: `${baseUrl}/used` },
    { url: `${baseUrl}/used/market` },
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
  ];

  try {
    const cameraData = await getPublicKehCameraCatalog({ limit: 1000 });
    routes.push(
      ...cameraData.models
        .filter(
          (model) =>
            !findAllIndexedCameraProduct(
              model.catalog_product_label,
              model.model_name,
            ),
        )
        .map((model) => ({
          url: `${baseUrl}/cameras/${model.slug}`,
        })),
    );
  } catch {
    // Keep stable sitemap routes available during a feed sync or backend outage.
  }

  return routes;
}
