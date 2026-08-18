import type { SearchResponse } from "@/lib/api";

const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type SearchAnalyticsSource = "public" | "seo_page";

export async function searchDealsWithSource(
  query: string,
  category = "cameras",
  providers = "ebay",
  options: {
    includeAuctions?: boolean;
    auctionHours?: number;
    usOnly?: boolean;
    trackAnalytics?: boolean;
    analyticsSource?: SearchAnalyticsSource;
  } = {},
): Promise<SearchResponse> {
  const params = new URLSearchParams({
    q: query,
    category,
    providers,
    include_auctions: options.includeAuctions ? "true" : "false",
    auction_hours: String(options.auctionHours ?? 24),
    us_only: options.usOnly ? "true" : "false",
    analytics: options.trackAnalytics ? "true" : "false",
    analytics_source: options.analyticsSource ?? "public",
  });
  const response = await fetch(`${baseUrl}/api/search?${params.toString()}`, {
    cache: "no-store",
  });

  if (!response.ok) throw new Error("Search failed");
  return response.json();
}
