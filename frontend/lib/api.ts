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
  seller_feedback_score: number | null;
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
  warning_labels: string[];
  item_location: string | null;
  item_group_type: string | null;
};

export type PriceContext = {
  product_id: string | null;
  window_days: number;
  current_eligible_count: number;
  current_best_price: number | null;
  current_median_price: number | null;
  current_low_price: number | null;
  current_high_price: number | null;
  snapshot_count: number;
  available_snapshot_count: number;
  availability_rate: number | null;
  history_ready: boolean;
  typical_low_price: number | null;
  typical_high_price: number | null;
  historical_median_price: number | null;
  current_vs_median_percent: number | null;
  first_observed_at: string | null;
  last_observed_at: string | null;
};

export type SearchDiagnostics = {
  fixed_price_candidates: number;
  fixed_price_filtered: number;
  fixed_price_eligible: number;
  fixed_price_duplicates_removed: number;
  fixed_price_rejection_reasons: Record<string, number>;
  auction_candidates: number;
  auction_filtered: number;
  auction_eligible: number;
  auction_duplicates_removed: number;
  auction_rejection_reasons: Record<string, number>;
};

export type SearchResponse = {
  query: string;
  category: string | null;
  resolved_product: ProductMatch | null;
  suggested_products: ProductMatch[];
  results: SearchResult[];
  auction_results: SearchResult[];
  diagnostics: SearchDiagnostics;
  price_context: PriceContext;
};

export type PriceOverviewProduct = {
  product_id: string;
  category?: string | null;
  product_label?: string | null;
  provider?: string | null;
  last_observed_at?: string | null;
  latest_eligible_count: number;
  latest_best_price?: number | null;
  snapshot_count: number;
  history_ready: boolean;
  typical_low_price?: number | null;
  typical_high_price?: number | null;
  historical_median_price?: number | null;
  availability_rate?: number | null;
};

export type PriceOverview = {
  window_days: number;
  snapshot_count: number;
  product_count: number;
  history_ready_count: number;
  available_latest_count: number;
  products: PriceOverviewProduct[];
};

export type PriceCollectionResponse = {
  live_ebay: boolean;
  collected_count: number;
  remaining_products: number;
  collected: Array<{
    case_id?: string | null;
    query?: string | null;
    category?: string | null;
    expected_product_id?: string | null;
    resolved_product_id?: string | null;
    result_count: number;
    eligible_count: number;
    snapshot_count: number;
    last_observed_at?: string | null;
  }>;
};


export type KehInventoryItem = {
  aw_product_id: string;
  merchant_product_id?: string | null;
  title: string;
  product_type: "camera_body" | "lens" | string;
  price: number;
  currency: string;
  condition_grade_code?: string | null;
  condition_grade_label?: string | null;
  affiliate_url: string;
  merchant_url?: string | null;
  image_url?: string | null;
  brand?: string | null;
  mpn?: string | null;
  upc?: string | null;
  in_stock: boolean;
  is_for_sale: boolean;
  matched_product_id?: string | null;
  matched_product_label?: string | null;
  match_confidence?: number | null;
  match_status: "matched" | "unmatched" | "ambiguous" | string;
  match_reason?: string | null;
  synced_at?: string | null;
};

export type KehSyncRun = {
  id: string;
  started_at: string;
  completed_at?: string | null;
  status: string;
  feed_items: number;
  scoped_items: number;
  matched_items: number;
  unmatched_items: number;
  ambiguous_items: number;
  error_items: number;
  error_message?: string | null;
};

export type KehOverview = {
  enabled: boolean;
  configured: boolean;
  public_results_enabled: boolean;
  public_product_ids?: string[];
  pilot_product_ids: string[];
  latest_sync?: KehSyncRun | null;
  active_item_count: number;
  matched_count: number;
  unmatched_count: number;
  ambiguous_count: number;
  lens_inventory_count?: number;
  matched_product_count: number;
  items: KehInventoryItem[];
};

export type KehLensFacet = { value: string; label: string; count: number };

export type KehLensListing = {
  aw_product_id: string;
  title: string;
  price: number | null;
  currency: string;
  condition_grade_code?: string | null;
  condition_grade_label?: string | null;
  affiliate_url: string;
  image_url?: string | null;
  mpn?: string | null;
};

export type KehLensModel = {
  model_key: string;
  model_name: string;
  mount: string;
  lens_type: string;
  focal_group: string;
  focal_min?: number | null;
  focal_max?: number | null;
  brand: string;
  listing_count: number;
  lowest_price?: number | null;
  highest_price?: number | null;
  currency: string;
  condition_grades: string[];
  image_url?: string | null;
  listings: KehLensListing[];
};

export type KehLensBuilderResponse = {
  summary: {
    listing_count: number;
    model_count: number;
    filtered_listing_count: number;
    filtered_model_count: number;
  };
  selected: {
    mount?: string | null;
    lens_type?: string | null;
    focal_group?: string | null;
    brand?: string | null;
    query?: string | null;
  };
  facets: {
    mounts: KehLensFacet[];
    lens_types: KehLensFacet[];
    focal_groups: KehLensFacet[];
    brands: KehLensFacet[];
  };
  models: KehLensModel[];
};

export type StorageStatus = {
  configured: boolean;
  connected: boolean;
  backend: "postgresql" | "file" | "file_fallback" | string;
  last_connected_at?: string | null;
  error?: string | null;
};

export type AnalyticsCategoryRow = {
  category: string;
  searches: number;
  with_results: number;
  no_results: number;
  no_result_rate: number | null;
  clicks: number;
};

export type AnalyticsTopSearch = {
  category: string;
  product_id?: string | null;
  label: string;
  searches: number;
  no_results: number;
  clicks: number;
};

export type AnalyticsDigest = {
  days: number;
  search_count: number;
  resolved_count: number;
  with_results_count: number;
  no_result_count: number;
  no_result_rate: number | null;
  us_only_count: number;
  us_only_rate: number | null;
  click_count: number;
  affiliate_click_count: number;
  approximate_click_rate: number | null;
  category_rows: AnalyticsCategoryRow[];
  top_searches: AnalyticsTopSearch[];
  provider_shown_counts: Record<string, number>;
  provider_click_counts: Record<string, number>;
  daily: Array<{ date: string; searches: number; clicks: number; no_results: number }>;
  summary_text: string;
  privacy_note: string;
};

export type AnalyticsSummary = {
  total_clicks: number;
  affiliate_clicks: number;
  active_bad_result_reports: number;
  beta_feedback_count?: number;
  filtered_listing_count: number;
  manual_filter_rule_count?: number;
  provider_counts: Record<string, number>;
  category_counts: Record<string, number>;
  latest_click: ClickRecord | null;
  storage?: StorageStatus;
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

export type ManualFilterRule = {
  id: string;
  phrase: string;
  category?: string | null;
  product_id?: string | null;
  except_phrases: string[];
  note?: string | null;
  source_title?: string | null;
  source_item_id?: string | null;
  enabled: boolean;
  created_at: string;
};

export type ManualFilterRulePayload = {
  phrase: string;
  category?: string | null;
  product_id?: string | null;
  except_phrases?: string[];
  note?: string | null;
  source_title?: string | null;
  source_item_id?: string | null;
};


export type QaOutcome = "pass" | "top3_only" | "fail" | "no_inventory";

export type QaEvaluation = {
  id: string;
  case_id: string;
  category: string;
  query: string;
  expected_product_id?: string | null;
  expected_label?: string | null;
  resolved_product_id?: string | null;
  resolved_label?: string | null;
  resolution_correct: boolean;
  outcome: QaOutcome;
  issue_tags: string[];
  notes?: string | null;
  result_titles: string[];
  diagnostics: Record<string, unknown>;
  created_at: string;
};

export type QaCase = {
  id: string;
  category: "consoles" | "lego" | string;
  query: string;
  expected_product_id: string;
  expected_label: string;
  goal: string;
  priority: "high" | "medium" | "low" | string;
  attempt_count: number;
  latest_evaluation?: QaEvaluation | null;
};

export type QaSummary = {
  total_cases: number;
  tested_cases: number;
  available_inventory_cases: number;
  counts: Record<QaOutcome | "untested", number>;
  category_counts: Record<string, Record<QaOutcome | "untested", number>>;
  quality_rate: number | null;
  overall_rate: number | null;
};

export type QaCasesResponse = {
  cases: QaCase[];
  summary: QaSummary;
};

export type QaEvaluationPayload = {
  case_id: string;
  category: string;
  query: string;
  expected_product_id?: string | null;
  expected_label?: string | null;
  resolved_product_id?: string | null;
  resolved_label?: string | null;
  resolution_correct: boolean;
  outcome: QaOutcome;
  issue_tags?: string[];
  notes?: string | null;
  result_titles?: string[];
  diagnostics?: Record<string, unknown>;
};

const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function searchDeals(
  query: string,
  category = "cameras",
  providers = "ebay",
  options: { includeAuctions?: boolean; auctionHours?: number; usOnly?: boolean; trackAnalytics?: boolean } = {},
): Promise<SearchResponse> {
  const params = new URLSearchParams({
    q: query,
    category,
    providers,
    include_auctions: options.includeAuctions ? "true" : "false",
    auction_hours: String(options.auctionHours ?? 24),
    us_only: options.usOnly ? "true" : "false",
    analytics: options.trackAnalytics ? "true" : "false",
  });
  const url = `${baseUrl}/api/search?${params.toString()}`;
  const response = await fetch(url, { cache: "no-store" });

  if (!response.ok) {
    throw new Error("Search failed");
  }

  return response.json();
}

export async function searchAuctions(
  query: string,
  category = "cameras",
  providers = "ebay",
  options: { auctionHours?: number; usOnly?: boolean } = {},
): Promise<SearchResponse> {
  const params = new URLSearchParams({
    q: query,
    category,
    providers,
    auction_hours: String(options.auctionHours ?? 24),
    us_only: options.usOnly ? "true" : "false",
  });
  const url = `${baseUrl}/api/search/auctions?${params.toString()}`;
  const response = await fetch(url, { cache: "no-store" });

  if (!response.ok) {
    throw new Error("Auction search failed");
  }

  return response.json();
}

export async function suggestProducts(
  query: string,
  category = "cameras",
  limit = 8,
): Promise<ProductMatch[]> {
  if (query.trim().length < 2) return [];

  const url = `${baseUrl}/api/products/suggest?q=${encodeURIComponent(query)}&category=${encodeURIComponent(category)}&limit=${limit}`;
  const response = await fetch(url, { cache: "no-store" });

  if (!response.ok) {
    return [];
  }

  return response.json();
}

export type BetaFeedbackPayload = {
  feedback_type: string;
  category?: string;
  message: string;
  email?: string;
  page_url?: string;
  website?: string;
};

export type BetaFeedbackRecord = {
  id: string;
  submitted_at: string;
  feedback_type: string;
  category?: string | null;
  message: string;
  email?: string | null;
  page_url?: string | null;
};

export type ReportBadResultPayload = {
  url: string;
  title?: string;
  provider?: string;
  category?: string;
  product_id?: string;
  query?: string;
  reason?: string;
};

export async function submitBetaFeedback(payload: BetaFeedbackPayload): Promise<void> {
  const response = await fetch(`${baseUrl}/api/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error("Feedback failed");
}

export async function reportBadResult(
  payload: ReportBadResultPayload,
): Promise<void> {
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
  metadata: {
    query?: string;
    category?: string;
    productId?: string;
    provider?: string;
    title?: string;
  } = {},
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

export async function getAnalyticsDigest(
  token?: string,
  days = 30,
): Promise<AnalyticsDigest> {
  const params = new URLSearchParams({ days: String(days) });
  if (token) params.set("token", token);
  const response = await fetch(`${baseUrl}/api/analytics/digest?${params.toString()}`, { cache: "no-store" });
  if (!response.ok) throw new Error("Analytics digest failed");
  return response.json();
}

export async function getAnalyticsSummary(
  token?: string,
): Promise<AnalyticsSummary> {
  const response = await fetch(
    `${baseUrl}/api/analytics/summary${adminQuery(token)}`,
    { cache: "no-store" },
  );
  if (!response.ok) throw new Error("Analytics summary failed");
  return response.json();
}

export async function getRecentClicks(token?: string): Promise<ClickRecord[]> {
  const separator = token
    ? `?token=${encodeURIComponent(token)}&limit=50`
    : "?limit=50";
  const response = await fetch(`${baseUrl}/api/analytics/clicks${separator}`, {
    cache: "no-store",
  });
  if (!response.ok) throw new Error("Click analytics failed");
  const data = await response.json();
  return data.clicks || [];
}

export async function getActiveReports(
  token?: string,
): Promise<BadResultReport[]> {
  const separator = token
    ? `?token=${encodeURIComponent(token)}&limit=50`
    : "?limit=50";
  const response = await fetch(`${baseUrl}/api/analytics/reports${separator}`, {
    cache: "no-store",
  });
  if (!response.ok) throw new Error("Report analytics failed");
  const data = await response.json();
  return data.reports || [];
}

export async function getRecentFilteredListings(
  token?: string,
): Promise<FilteredListingRecord[]> {
  const separator = token
    ? `?token=${encodeURIComponent(token)}&limit=75`
    : "?limit=75";
  const response = await fetch(
    `${baseUrl}/api/analytics/filtered${separator}`,
    { cache: "no-store" },
  );
  if (!response.ok) throw new Error("Filtered listing analytics failed");
  const data = await response.json();
  return data.filtered || [];
}

export async function getBetaFeedback(token?: string): Promise<BetaFeedbackRecord[]> {
  const separator = token
    ? `?token=${encodeURIComponent(token)}&limit=100`
    : "?limit=100";
  const response = await fetch(`${baseUrl}/api/analytics/beta-feedback${separator}`, {
    cache: "no-store",
  });
  if (!response.ok) throw new Error("Beta feedback failed");
  const data = await response.json();
  return data.feedback || [];
}

export async function getManualFilterRules(
  token?: string,
): Promise<ManualFilterRule[]> {
  const response = await fetch(
    `${baseUrl}/api/analytics/filter-rules${adminQuery(token)}`,
    { cache: "no-store" },
  );
  if (!response.ok) throw new Error("Manual filter rules failed");
  const data = await response.json();
  return data.rules || [];
}

export async function createManualFilterRule(
  payload: ManualFilterRulePayload,
  token?: string,
): Promise<ManualFilterRule> {
  const query = adminQuery(token);
  const response = await fetch(
    `${baseUrl}/api/analytics/filter-rules${query}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
  );

  if (!response.ok) {
    throw new Error("Could not create filter rule");
  }

  return response.json();
}

export async function deleteManualFilterRule(
  id: string,
  token?: string,
): Promise<void> {
  const query = adminQuery(token);
  const response = await fetch(
    `${baseUrl}/api/analytics/filter-rules/${encodeURIComponent(id)}${query}`,
    {
      method: "DELETE",
    },
  );

  if (!response.ok) {
    throw new Error("Could not delete filter rule");
  }
}

export async function deleteBadResultReport(
  linkKey: string,
  token?: string,
  options: { productId?: string | null; category?: string | null } = {},
): Promise<void> {
  const params = new URLSearchParams();
  if (token) params.set("token", token);
  if (options.productId) params.set("product_id", options.productId);
  if (options.category) params.set("category", options.category);
  const query = params.toString() ? `?${params.toString()}` : "";
  const response = await fetch(
    `${baseUrl}/api/analytics/reports/${encodeURIComponent(linkKey)}${query}`,
    {
      method: "DELETE",
    },
  );

  if (!response.ok) {
    throw new Error("Could not delete report");
  }
}

const ebayCategoryIds: Record<string, string> = {
  cameras: "31388",
  lenses: "3323",
  gpus: "27386",
  lego: "19006",
  consoles: "139971",
  ram: "170083",
  cpus: "164",
  books: "267",
};

export function buildEbaySearchUrl(query: string, category?: string): string {
  const params = new URLSearchParams({
    _nkw: query,
    LH_BIN: "1",
    _sop: "15",
  });
  const categoryId = category ? ebayCategoryIds[category] : undefined;
  if (categoryId) params.set("_sacat", categoryId);
  return `https://www.ebay.com/sch/i.html?${params.toString()}`;
}


export async function getQaCases(token?: string): Promise<QaCasesResponse> {
  const response = await fetch(
    `${baseUrl}/api/qa/cases${adminQuery(token)}`,
    { cache: "no-store" },
  );
  if (!response.ok) throw new Error("QA cases failed");
  return response.json();
}

export async function saveQaEvaluation(
  payload: QaEvaluationPayload,
  token?: string,
): Promise<QaEvaluation> {
  const response = await fetch(
    `${baseUrl}/api/qa/evaluations${adminQuery(token)}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
  );
  if (!response.ok) throw new Error("Could not save QA evaluation");
  return response.json();
}


export async function getPriceOverview(
  token?: string,
  days = 30,
): Promise<PriceOverview> {
  const params = new URLSearchParams({ days: String(days), limit: "1000" });
  if (token) params.set("token", token);
  // Use the same direct Railway API pattern as the working KEH admin page.
  // This works during server rendering and in the browser because the API
  // already exposes the required public-beta CORS policy.
  const response = await fetch(`${baseUrl}/api/prices/overview?${params.toString()}`, { cache: "no-store" });
  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(detail || `Price overview failed (${response.status})`);
  }
  return response.json();
}

export async function collectQaPriceBatch(
  token: string,
  options: { limit?: number; category?: string } = {},
): Promise<PriceCollectionResponse> {
  const response = await fetch(`${baseUrl}/api/prices/collect/qa?token=${encodeURIComponent(token)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ limit: options.limit ?? 5, category: options.category ?? null }),
    cache: "no-store",
  });
  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(detail || `Price collection failed (${response.status})`);
  }
  return response.json();
}


export async function getKehOverview(token: string, limit = 500): Promise<KehOverview> {
  const params = new URLSearchParams({ token, limit: String(limit) });
  const response = await fetch(`${baseUrl}/api/keh/overview?${params.toString()}`, { cache: "no-store" });
  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(detail || `KEH overview failed (${response.status})`);
  }
  return response.json();
}

export async function syncKehFeed(token: string): Promise<KehSyncRun> {
  const response = await fetch(`${baseUrl}/api/keh/sync?token=${encodeURIComponent(token)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ force: true }),
  });
  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(detail || `KEH sync failed (${response.status})`);
  }
  return response.json();
}

export async function getKehLensBuilder(
  token: string,
  filters: { mount?: string; lensType?: string; focalGroup?: string; brand?: string; query?: string; limit?: number } = {},
): Promise<KehLensBuilderResponse> {
  const params = new URLSearchParams({ token, limit: String(filters.limit ?? 100) });
  if (filters.mount) params.set("mount", filters.mount);
  if (filters.lensType) params.set("lens_type", filters.lensType);
  if (filters.focalGroup) params.set("focal_group", filters.focalGroup);
  if (filters.brand) params.set("brand", filters.brand);
  if (filters.query) params.set("q", filters.query);
  const response = await fetch(`${baseUrl}/api/keh/lenses/builder?${params.toString()}`, { cache: "no-store" });
  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(detail || `KEH lens builder failed (${response.status})`);
  }
  return response.json();
}

export type BookLabStatus = {
  configured: boolean;
  public: boolean;
  mode: string;
};

export type BookIsbnIdentity = {
  input: string;
  normalized: string;
  valid: boolean;
  input_type: "ISBN-10" | "ISBN-13" | null;
  isbn10: string | null;
  isbn13: string | null;
  query_isbns: string[];
};

export type BookQueryAttempt = {
  isbn: string;
  role: "primary" | "fallback" | string;
  candidate_count: number;
  eligible_count: number;
  standard_count: number;
  collectible_count: number;
  bundle_count: number;
  duplicates_removed: number;
  consensus_tokens: string[];
  rejection_reasons: Record<string, number>;
  used_as_results: boolean;
};

export type BookLabResponse = {
  isbn: BookIsbnIdentity;
  candidate_count: number;
  eligible_count: number;
  standard_count: number;
  collectible_count: number;
  bundle_count: number;
  duplicates_removed: number;
  rejection_reasons: Record<string, number>;
  query_attempts: BookQueryAttempt[];
  selected_query_isbn: string | null;
  fallback_used: boolean;
  top_results: SearchResult[];
  results: SearchResult[];
  collectible_results: SearchResult[];
  bundle_results: SearchResult[];
};

export async function getBooksLabStatus(token: string): Promise<BookLabStatus> {
  const params = new URLSearchParams({ token });
  const response = await fetch(`${baseUrl}/api/books/lab/status?${params.toString()}`, { cache: "no-store" });
  if (!response.ok) throw new Error("Books lab access failed");
  return response.json();
}

export async function searchPublicBooksByIsbn(
  isbn: string,
  limit = 35,
  options: { usOnly?: boolean; trackAnalytics?: boolean } = {},
): Promise<BookLabResponse> {
  const params = new URLSearchParams({
    isbn,
    limit: String(limit),
    us_only: options.usOnly ? "true" : "false",
    analytics: options.trackAnalytics ? "true" : "false",
  });
  const response = await fetch(`${baseUrl}/api/books/search?${params.toString()}`, { cache: "no-store" });
  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(detail || `Book search failed (${response.status})`);
  }
  return response.json();
}

export async function searchBooksByIsbn(token: string, isbn: string, limit = 35): Promise<BookLabResponse> {
  const params = new URLSearchParams({ token, isbn, limit: String(limit) });
  const response = await fetch(`${baseUrl}/api/books/lab/search?${params.toString()}`, { cache: "no-store" });
  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(detail || `Book search failed (${response.status})`);
  }
  return response.json();
}
