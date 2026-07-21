import { adminFetch } from "@/lib/api";

export type ShippingQaOption = {
  cost: number | null;
  currency: string | null;
  cost_type: string | null;
  carrier: string | null;
  service: string | null;
  speed: string | null;
  min_delivery: string | null;
  max_delivery: string | null;
  import_charges: number | null;
  import_currency: string | null;
  fulfilled_through: string | null;
  estimate_country: string | null;
  estimate_postal_code: string | null;
};

export type ShippingQaItem = {
  item_id: string | null;
  title: string;
  condition: string;
  price: number | null;
  currency: string | null;
  shipping_cost: number | null;
  total_price: number | null;
  item_location: string | null;
  url: string | null;
  summary_option_count: number;
  detail_option_count: number;
  detail_loaded: boolean;
  detail_error: string | null;
  shipping_options: ShippingQaOption[];
  best_shipping_option: ShippingQaOption | null;
};

export type ShippingQaResponse = {
  query: string;
  category: string | null;
  country: string;
  postal_code: string;
  availability_filter_applied: boolean;
  search_total: number | null;
  returned: number;
  coverage: {
    shipping_cost: number;
    delivery_window: number;
    method: number;
    detail_loaded: number;
    import_charges: number;
  };
  items: ShippingQaItem[];
};

const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function runShippingQa(
  token: string,
  options: { query: string; category: string; postalCode: string; country?: string; limit?: number },
): Promise<ShippingQaResponse> {
  const params = new URLSearchParams({
    token,
    q: options.query,
    category: options.category,
    postal_code: options.postalCode,
    country: options.country || "US",
    limit: String(options.limit ?? 5),
  });
  const response = await adminFetch(`${baseUrl}/api/qa/shipping?${params.toString()}`, { cache: "no-store" });
  if (!response.ok) {
    const detail = await response.json().catch(() => null);
    throw new Error(detail?.detail || `Shipping QA failed (${response.status})`);
  }
  return response.json();
}
