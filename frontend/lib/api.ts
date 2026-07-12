export type Product = {
  id: string;
  category: string;
  category_label: string;
  product_type: string;
  brand: string;
  model: string;
  variant: string | null;
  aliases: string[];
  required_terms: string[];
  excluded_terms: string[];
  metadata: Record<string, unknown>;
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
  affiliate_url_used: boolean;
  affiliate_url_has_campaign_id: boolean;
  score: number;
};

export type SearchResponse = {
  query: string;
  category: string | null;
  resolved_product: ProductMatch | null;
  results: SearchResult[];
};

const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function searchDeals(query: string, category = "cameras", providers = "ebay"): Promise<SearchResponse> {
  const url = `${baseUrl}/api/search?q=${encodeURIComponent(query)}&category=${encodeURIComponent(category)}&providers=${encodeURIComponent(providers)}`;
  const response = await fetch(url, { cache: "no-store" });

  if (!response.ok) {
    throw new Error("Search failed");
  }

  return response.json();
}

export async function suggestProducts(query: string, category = "cameras", limit = 8): Promise<ProductMatch[]> {
  if (query.trim().length < 2) return [];

  const url = `${baseUrl}/api/products/suggest?q=${encodeURIComponent(query)}&category=${encodeURIComponent(category)}&limit=${limit}`;
  const response = await fetch(url, { cache: "no-store" });

  if (!response.ok) {
    return [];
  }

  return response.json();
}

export function buildOutboundUrl(url: string): string {
  return `${baseUrl}/api/out?url=${encodeURIComponent(url)}`;
}
