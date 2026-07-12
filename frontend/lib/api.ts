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
  listing_type: "fixed_price" | "auction" | string;
  buying_options: string[];
  bid_count: number | null;
  current_bid_price: number | null;
  item_end_date: string | null;
};

export type SearchResponse = {
  query: string;
  category: string | null;
  resolved_product: ProductMatch | null;
  results: SearchResult[];
  auction_results: SearchResult[];
};

export type AnalyticsSummary = {
  total_clicks: number;
  affiliate_clicks: number;
  active_bad_result_reports: number;
  filtered_listing_count: number;
  provider_counts: Record<string, number>;
  category_counts: Record<string, number>;
  latest_click: ClickRecord | null;
};

export type ClickRecord = {
  clicked_at: string;
  provider?: string | null;
  category?: string | null;
  product_id?: string | null;
  query?: string | null;
  title?: string | null;
  ebay_item_id?: string | null;
  affiliate_campaign_present?: boolean;
  affiliate_reference?: string | null;
  tracked_url?: string;
};


export type FilteredListingRecord = {
  filtered_at: string;
  provider?: string | null;
  category?: string | null;
  product_id?: string | null;
  query?: string | null;
  title?: string | null;
  listing_type?: string | null;
  reasons?: string[];
  ebay_item_id?: string | null;
  link_key?: string;
};

export type BadResultReport = {
  reported_at: string;
  expires_at: string;
  reason?: string;
  provider?: string | null;
  category?: string | null;
  product_id?: string | null;
  query?: string | null;
  title?: string | null;
  ebay_item_id?: string | null;
  link_key?: string;
};

const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function searchDeals(query: string, category = "cameras", providers = "ebay"): Promise<SearchResponse> {
  const url = `${baseUrl}/api/search?q=${encodeURIComponent(query)}&category=${encodeURIComponent(category)}&providers=${encodeURIComponent(providers)}&include_auctions=true&auction_hours=24`;
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

function adminQuery(token?: string): string {
  return token ? `?token=${encodeURIComponent(token)}` : "";
}

export async function getAnalyticsSummary(token?: string): Promise<AnalyticsSummary> {
  const response = await fetch(`${baseUrl}/api/analytics/summary${adminQuery(token)}`, { cache: "no-store" });
  if (!response.ok) throw new Error("Analytics summary failed");
  return response.json();
}

export async function getRecentClicks(token?: string): Promise<ClickRecord[]> {
  const separator = token ? `?token=${encodeURIComponent(token)}&limit=50` : "?limit=50";
  const response = await fetch(`${baseUrl}/api/analytics/clicks${separator}`, { cache: "no-store" });
  if (!response.ok) throw new Error("Click analytics failed");
  const data = await response.json();
  return data.clicks || [];
}

export async function getActiveReports(token?: string): Promise<BadResultReport[]> {
  const separator = token ? `?token=${encodeURIComponent(token)}&limit=50` : "?limit=50";
  const response = await fetch(`${baseUrl}/api/analytics/reports${separator}`, { cache: "no-store" });
  if (!response.ok) throw new Error("Report analytics failed");
  const data = await response.json();
  return data.reports || [];
}

export async function getRecentFilteredListings(token?: string): Promise<FilteredListingRecord[]> {
  const separator = token ? `?token=${encodeURIComponent(token)}&limit=75` : "?limit=75";
  const response = await fetch(`${baseUrl}/api/analytics/filtered${separator}`, { cache: "no-store" });
  if (!response.ok) throw new Error("Filtered listing analytics failed");
  const data = await response.json();
  return data.filtered || [];
}
