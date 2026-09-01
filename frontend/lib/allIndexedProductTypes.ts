import type { IndexedProduct } from "@/lib/indexedProducts";

export type AllIndexedProduct = Omit<IndexedProduct, "category"> & {
  category: IndexedProduct["category"] | "cpus";
};
