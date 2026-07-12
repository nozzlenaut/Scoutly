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

export type ReportBadResultPayload = {
  url: string;
  title?: string;
  provider?: string;
  category?: string;
  product_id?: string;
  query?: string;
  reason?: string;
};

export async function reportBadResult(payload: ReportBadResultPayload): Promise<void> {
  const response = await fetch(`${baseUrl}/api/results/report`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Report failed");
  }
}

export function buildOutboundUrl(
  url: string,
  metadata: { query?: string; category?: string; productId?: string; provider?: string; title?: string } = {},
): string {
  const params = new URLSearchParams({ url });
  if (metadata.query) params.set("q", metadata.query);
  if (metadata.category) params.set("category", metadata.category);
  if (metadata.productId) params.set("product_id", metadata.productId);
  if (metadata.provider) params.set("provider", metadata.provider);
  if (metadata.title) params.set("title", metadata.title);

  return `${baseUrl}/api/out?${params.toString()}`;
}
