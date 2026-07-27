
import {
  adminFetch,
  buildEbaySearchUrl,
  buildOutboundUrl,
  type BookLabResponse,
  type SearchResult,
} from "@/lib/api";

const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type GoodreadsSearchMetadata = {
  batchId: string;
  shelf: string;
  importedCount: number;
  searchableCount: number;
  digitalCount: number;
  missingIsbnCount: number;
  usOnly?: boolean;
};

export type GoodreadsBatchAnalytics = {
  batch_id: string;
  shelf: string | null;
  imported_count: number;
  searchable_count: number;
  digital_count: number;
  missing_isbn_count: number;
  searched_count: number;
  found_count: number;
  no_result_count: number;
  candidate_count: number;
  filtered_count: number;
  us_only: boolean;
  started_at: string | null;
  completed_at: string | null;
  complete: boolean;
};

export type GoodreadsAnalyticsDigest = {
  days: number;
  import_count: number;
  completed_import_count: number;
  search_count: number;
  found_count: number;
  no_result_count: number;
  exact_success_rate: number | null;
  candidate_count: number;
  filtered_count: number;
  exact_listing_click_count: number;
  other_editions_click_count: number;
  average_searches_per_import: number | null;
  imported_row_count: number;
  searchable_row_count: number;
  digital_skipped_count: number;
  missing_isbn_count: number;
  recent_batches: GoodreadsBatchAnalytics[];
  summary_text: string;
  privacy_note: string;
};

export async function searchGoodreadsIsbn(
  isbn: string,
  metadata: GoodreadsSearchMetadata,
  book: { title: string; author: string },
): Promise<BookLabResponse> {
  const params = new URLSearchParams({
    isbn,
    limit: "75",
    us_only: metadata.usOnly ? "true" : "false",
    analytics: "true",
    source: "goodreads",
    batch_id: metadata.batchId,
    shelf: metadata.shelf,
    imported_count: String(metadata.importedCount),
    searchable_count: String(metadata.searchableCount),
    digital_count: String(metadata.digitalCount),
    missing_isbn_count: String(metadata.missingIsbnCount),
  });
  if (book.title) params.set("expected_title", book.title.slice(0, 300));
  if (book.author) params.set("expected_author", book.author.slice(0, 200));

  const response = await fetch(
    `${baseUrl}/api/books/search?${params.toString()}`,
    { cache: "no-store" },
  );
  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(detail || `Book search failed (${response.status})`);
  }
  return response.json();
}

export async function getGoodreadsAnalyticsDigest(
  token: string,
  days = 30,
): Promise<GoodreadsAnalyticsDigest> {
  const params = new URLSearchParams({
    token,
    days: String(days),
  });
  const response = await adminFetch(
    `${baseUrl}/api/analytics/goodreads?${params.toString()}`,
    { cache: "no-store" },
  );
  if (!response.ok) {
    throw new Error("Goodreads analytics failed");
  }
  return response.json();
}

export function exactListingOutboundUrl(
  result: SearchResult,
  batchId: string,
  isbn: string,
): string {
  return buildOutboundUrl(result.url, {
    query: isbn,
    category: "books",
    productId: `goodreads:${batchId}:${isbn}`,
    provider: result.provider,
    title: result.title,
  });
}

export function otherEditionsOutboundUrl(
  title: string,
  author: string,
  batchId: string,
): string {
  const query = [title, author].filter(Boolean).join(" ");
  return buildOutboundUrl(buildEbaySearchUrl(query, "books"), {
    query,
    category: "books",
    productId: `goodreads-other:${batchId}`,
    provider: "eBay",
    title: `Search other editions: ${title}`,
  });
}
