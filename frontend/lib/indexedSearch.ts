import type { SearchResponse } from "@/lib/api";

const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function getIndexedSearchResults(
  query: string,
  category: string,
): Promise<SearchResponse | null> {
  const params = new URLSearchParams({
    q: query,
    category,
    providers: "ebay",
    include_auctions: "false",
    auction_hours: "24",
    us_only: "false",
    analytics: "false",
  });

  try {
    const response = await fetch(`${baseUrl}/api/search?${params.toString()}`, {
      next: { revalidate: 1800 },
    });
    if (!response.ok) return null;
    return response.json();
  } catch {
    return null;
  }
}
