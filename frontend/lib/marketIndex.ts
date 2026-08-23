export type MarketIndexCategory = {
  category: string;
  model_count: number;
  median_percent_change: number | null;
  index_value: number | null;
  first_observed_at: string;
  last_observed_at: string;
  minimum_models_required: number;
};

export type MarketIndexModel = {
  product_id: string;
  category: string;
  product_label: string;
  query: string;
  provider: string;
  baseline_median_price: number;
  latest_median_price: number;
  percent_change: number;
  snapshot_count: number;
  first_observed_at: string;
  last_observed_at: string;
  history_days: number;
};

export type MarketIndexResponse = {
  generated_at: string;
  history_window_days: number;
  stale_after_days: number;
  minimum_history_hours: number;
  minimum_category_models: number;
  tracked_snapshot_count: number;
  comparable_model_count: number;
  methodology: string;
  categories: MarketIndexCategory[];
  models: MarketIndexModel[];
};

const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function getMarketIndex(): Promise<MarketIndexResponse | null> {
  try {
    const response = await fetch(`${baseUrl}/api/prices/market-index`, {
      next: { revalidate: 21600 },
    });
    if (!response.ok) return null;
    return response.json();
  } catch {
    return null;
  }
}
