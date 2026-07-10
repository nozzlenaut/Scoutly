export type Product = {
  id: string;
  category: string;
  brand: string;
  chipset_brand: string;
  model: string;
  variant: string | null;
  generation: string | null;
  vram_gb: number | null;
  memory_type: string | null;
  aliases: string[];
  required_terms: string[];
  excluded_terms: string[];
  active: boolean;
  display_name: string;
};

export type ProductMatch = {
  product: Product;
  confidence: number;
  matched_alias: string | null;
};

export type SearchResult = {
  provider: string;
  title: string;
  price: number;
  shipping: number;
  total_price: number;
  condition: string;
  seller_rating: number | null;
  url: string;
  image_url: string | null;
  score: number;
};

export type SearchResponse = {
  query: string;
  resolved_product: ProductMatch | null;
  results: SearchResult[];
};

export async function searchDeals(query: string, providers = "ebay,amazon"): Promise<SearchResponse> {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const url = `${baseUrl}/api/search?q=${encodeURIComponent(query)}&providers=${encodeURIComponent(providers)}`;
  const response = await fetch(url, { cache: "no-store" });

  if (!response.ok) {
    throw new Error("Search failed");
  }

  return response.json();
}
