import type { MetadataRoute } from "next";
import { buyingGuides } from "@/lib/buyingGuides";
import { indexedProducts } from "@/lib/indexedProducts";

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = "https://www.pricesift.app";
  return [
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
    ...indexedProducts.map((product) => ({
      url: `${baseUrl}/used/${product.slug}`,
    })),
  ];
}
