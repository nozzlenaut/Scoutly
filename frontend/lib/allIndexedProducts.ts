import {
  findIndexedCameraProduct,
  indexedProducts,
  type IndexedProduct,
} from "@/lib/indexedProducts";
import { indexedProductExtras } from "@/lib/indexedProductExtras";

export const allIndexedProducts: IndexedProduct[] = [
  ...indexedProducts,
  ...indexedProductExtras,
];

export function getAllIndexedProduct(slug: string): IndexedProduct | undefined {
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
): IndexedProduct | undefined {
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
