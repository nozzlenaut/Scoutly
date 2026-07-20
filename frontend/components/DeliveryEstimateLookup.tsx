"use client";

import { useMemo, useState } from "react";
import {
  getDeliveryEstimates,
  type DeliveryEstimateItem,
  type SearchResult,
} from "@/lib/api";

function money(value?: number | null, currency = "USD"): string {
  if (value === null || value === undefined) return "Not provided";
  return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(value);
}

function dateLabel(value?: string | null): string | null {
  if (!value) return null;
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return null;
  return parsed.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

function deliveryWindow(item: DeliveryEstimateItem): string {
  const option = item.best_shipping_option;
  const first = dateLabel(option?.min_delivery);
  const last = dateLabel(option?.max_delivery);
  if (first && last && first !== last) return `${first}–${last}`;
  return first || last || "Delivery date not provided";
}

export function DeliveryEstimateLookup({ results }: { results: SearchResult[] }) {
  const ebayItems = useMemo(
    () => results.filter((result) => result.provider.toLowerCase() === "ebay" && result.marketplace_item_id).slice(0, 3),
    [results],
  );
  const [postalCode, setPostalCode] = useState("");
  const [items, setItems] = useState<DeliveryEstimateItem[]>([]);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  if (!ebayItems.length) return null;

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const cleaned = postalCode.trim();
    if (!/^\d{5}(?:-\d{4})?$/.test(cleaned)) {
      setMessage("Enter a five-digit US ZIP code.");
      setItems([]);
      return;
    }
    setBusy(true);
    setMessage(null);
    setItems([]);
    try {
      const response = await getDeliveryEstimates(
        cleaned,
        ebayItems.map((result) => result.marketplace_item_id as string),
      );
      setItems(response.items);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not load delivery estimates.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mx-auto mt-4 max-w-6xl rounded-2xl border border-cyan-200/15 bg-cyan-200/[0.06] p-4">
      <form onSubmit={submit} className="flex flex-col gap-3 lg:flex-row lg:items-end">
        <label className="block flex-1">
          <span className="mb-2 block text-xs font-bold uppercase tracking-[0.18em] text-cyan-100">
            Delivery ZIP (optional)
          </span>
          <input
            value={postalCode}
            onChange={(event) => setPostalCode(event.target.value)}
            inputMode="numeric"
            autoComplete="postal-code"
            maxLength={10}
            placeholder="48035"
            className="min-h-12 w-full rounded-xl border border-white/10 bg-slate-950/70 px-4 text-white outline-none placeholder:text-slate-500 focus:border-cyan-300"
          />
        </label>
        <button
          type="submit"
          disabled={busy || !postalCode.trim()}
          className="min-h-12 rounded-xl bg-cyan-200 px-5 font-bold text-slate-950 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {busy ? "Checking…" : "Check delivery"}
        </button>
      </form>
      <p className="mt-2 text-xs leading-5 text-slate-400">
        Used only to check eBay delivery estimates for these listings. PriceSift does not save your ZIP.
      </p>

      {message ? <p className="mt-3 text-sm text-amber-200">{message}</p> : null}
      {items.length ? (
        <div className="mt-4 grid gap-3 lg:grid-cols-3">
          {items.map((item) => {
            const option = item.best_shipping_option;
            const method = option?.service || option?.carrier || option?.speed;
            return (
              <article key={item.item_id} className="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
                <p className="line-clamp-2 text-sm font-semibold text-white">{item.title}</p>
                {item.detail_loaded ? (
                  <>
                    <p className="mt-3 font-bold text-emerald-200">eBay estimate: {deliveryWindow(item)}</p>
                    <p className="mt-1 text-xs text-slate-400">
                      Shipping {money(item.shipping_cost)}{method ? ` · ${method}` : ""}
                    </p>
                  </>
                ) : (
                  <p className="mt-3 text-sm text-slate-400">eBay did not provide a delivery estimate.</p>
                )}
              </article>
            );
          })}
        </div>
      ) : null}
    </section>
  );
}
