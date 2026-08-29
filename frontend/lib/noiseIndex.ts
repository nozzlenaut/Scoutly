export type NoiseReason = {
  reason: string;
  count: number;
};

export type NoiseIndexModel = {
  product_id: string;
  category: string;
  product_label: string;
  query: string;
  provider: string;
  candidate_count: number;
  filtered_count: number;
  noise_rate: number | null;
  eligible_count: number;
  eligible_count_exact: boolean;
  duplicates_removed: number | null;
  duplicates_source: string;
  rejection_reasons: NoiseReason[];
  rejection_reason_breakdown_available: boolean;
  observed_at: string;
};

export type NoiseIndexCategory = {
  category: string;
  model_count: number;
  candidate_count: number;
  filtered_count: number;
  noise_rate: number | null;
  eligible_count: number;
  eligible_count_exact: boolean;
  duplicates_removed: number | null;
  duplicates_reported_model_count: number;
  duplicates_complete: boolean;
};

export type NoiseIndexResponse = {
  generated_at: string;
  latest_observed_at: string | null;
  oldest_observed_at: string | null;
  snapshot_mode: "current_marketplace_snapshot";
  historical_trends_available: boolean;
  stale_after_days: number;
  stale_model_count: number;
  minimum_ranking_candidates: number;
  model_count: number;
  methodology: string;
  categories: NoiseIndexCategory[];
  models: NoiseIndexModel[];
  noisiest: NoiseIndexModel[];
};

const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function getNoiseIndex(): Promise<NoiseIndexResponse | null> {
  try {
    const response = await fetch(`${baseUrl}/api/prices/noise-index`, {
      next: { revalidate: 1800 },
    });
    if (!response.ok) return null;
    return response.json();
  } catch {
    return null;
  }
}
