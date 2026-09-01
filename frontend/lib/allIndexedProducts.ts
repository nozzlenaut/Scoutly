import {
  findIndexedCameraProduct,
  indexedProducts,
} from "@/lib/indexedProducts";
import { indexedConsoleExtras } from "@/lib/indexedConsoleExtras";
import { indexedProductExtras } from "@/lib/indexedProductExtras";
import type { AllIndexedProduct } from "@/lib/allIndexedProductTypes";

const searchLabelOverrides: Record<string, Pick<AllIndexedProduct, "title" | "query">> = {
  "nvidia-rtx-3070": {
    title: "NVIDIA RTX 3070 8GB",
    query: "NVIDIA RTX 3070 8GB",
  },
  "lego-75192-millennium-falcon": {
    title: "LEGO Star Wars Millennium Falcon 75192",
    query: "LEGO Star Wars Millennium Falcon 75192",
  },
};

export const allIndexedProducts: AllIndexedProduct[] = [
  ...indexedProducts.map((product) => ({
    ...product,
    ...(searchLabelOverrides[product.slug] || {}),
  })),
  ...indexedProductExtras,
  ...indexedConsoleExtras,
];

export function getAllIndexedProduct(slug: string): AllIndexedProduct | undefined {
  return allIndexedProducts.find((product) => product.slug === slug);
}

function normalizedProductName(value?: string | null): string {
  return (value || "")
    .toLowerCase()
    .replace(/\bbody\b/g, "")
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

export function findAllIndexedCameraProduct(
  catalogProductLabel?: string | null,
  modelName?: string | null,
): AllIndexedProduct | undefined {
  const existing = findIndexedCameraProduct(catalogProductLabel, modelName);
  if (existing) return existing;

  const names = new Set(
    [catalogProductLabel, modelName]
      .map(normalizedProductName)
      .filter(Boolean),
  );
  if (!names.size) return undefined;

  return indexedProductExtras.find(
    (product) =>
      product.category === "cameras" &&
      [product.title, product.query].some((value) =>
        names.has(normalizedProductName(value)),
      ),
  );
}
