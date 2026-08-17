"use client";

import { useCallback, useEffect, useState } from "react";
import { PriceCollector } from "@/components/PriceCollector";
import { adminFetch, getPriceOverview, type PriceOverview } from "@/lib/api";

type MarketSignal = {
  product_id: string;
  product_label: string;
  category?: string | null;
  primary_signal: string;
  signal_tags: string[];
  video_score: number;
  video_worthy: boolean;
  confidence: string;
  latest_best_price?: number | null;
  latest_median_price?: number | null;
  latest_eligible_count: number;
  baseline_median_price?: number | null;
  baseline_eligible_count?: number | null;
  median_change_percent?: number | null;
  best_vs_baseline_percent?: number | null;
  inventory_change_percent?: number | null;
  prior_snapshot_count: number;
  story_angle: string;
};

type MarketSignalResponse = {
  window_days: number;
  product_count: number;
  ready_product_count: number;
  building_product_count: number;
  signal_count: number;
  video_worthy_count: number;
  signals: MarketSignal[];
};

async function getMarketSignals(token: string): Promise<MarketSignalResponse> {
  const params = new URLSearchParams({ token, days: "30", limit: "12" });
  const response = await adminFetch(`/api/prices/signals?${params.toString()}`, { cache: "no-store" });
  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(detail || `Market signals failed (${response.status})`);
  }
  return response.json();
}

function finiteNumber(value: unknown): number | null {
  if (value === null || value === undefined || value === "") return null;
  const parsed = typeof value === "number" ? value : Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function money(value: unknown): string {
  const parsed = finiteNumber(value);
  return parsed === null ? "—" : `$${parsed.toFixed(2)}`;
}

function percent(value: unknown): string {
  const parsed = finiteNumber(value);
  return parsed === null ? "—" : `${parsed.toFixed(1)}%`;
}

function dateLabel(value?: string | null): string {
  if (!value) return "—";
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
}

function signalLabel(value: string): string {
  return value.replaceAll("_", " ");
}

export function AdminPriceDashboard({ initialOverview, token }: { initialOverview: PriceOverview; token: string }) {
  const [overview, setOverview] = useState<PriceOverview | null>(initialOverview);
  const [signals, setSignals] = useState<MarketSignalResponse | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("ready");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [signalError, setSignalError] = useState<string | null>(null);

  const loadSignals = useCallback(async () => {
    setSignalError(null);
    try {
      setSignals(await getMarketSignals(token));
    } catch (error) {
      setSignalError(error instanceof Error ? error.message : "Unknown market-signal error");
    }
  }, [token]);

  const load = useCallback(async () => {
    setStatus("loading");
    setErrorMessage(null);
    setSignalError(null);
    try {
      const [nextOverview, nextSignals] = await Promise.all([
        getPriceOverview(token, 30),
        getMarketSignals(token),
      ]);
      setOverview(nextOverview);
      setSignals(nextSignals);
      setStatus("ready");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown price-history error");
      setStatus("error");
    }
  }, [token]);

  useEffect(() => {
    setOverview(initialOverview);
    setStatus("ready");
    void loadSignals();
  }, [initialOverview, loadSignals]);

  if (status === "loading" && !overview) {
    return <div className="mt-8 rounded-3xl border border-white/10 bg-white/[0.04] p-6 text-slate-300">Loading price history…</div>;
  }

  if (status === "error" && !overview) {
    return (
      <div className="mt-8 rounded-3xl border border-amber-300/25 bg-amber-300/10 p-6 text-amber-50">
        <h2 className="text-xl font-bold">Price history could not load</h2>
        <p className="mt-2 text-sm leading-6">The page loaded, but PriceSift could not retrieve the overview through the Vercel-to-Railway proxy.</p>
        {errorMessage ? <p className="mt-3 break-words rounded-2xl bg-slate-950/40 p-3 font-mono text-xs text-amber-100/80">{errorMessage}</p> : null}
        <button type="button" onClick={() => void load()} className="mt-4 rounded-2xl bg-white px-4 py-2 font-semibold text-slate-950">Retry</button>
      </div>
    );
  }

  if (!overview) return null;

  return (
    <>
      <section className="mt-8 grid gap-4 md:grid-cols-4">
        <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5"><p className="text-sm text-slate-400">Snapshots</p><p className="mt-2 text-3xl font-black">{overview.snapshot_count}</p></div>
        <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5"><p className="text-sm text-slate-400">Products observed</p><p className="mt-2 text-3xl font-black">{overview.product_count}</p></div>
        <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5"><p className="text-sm text-slate-400">Typical range ready</p><p className="mt-2 text-3xl font-black">{overview.history_ready_count}</p></div>
        <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5"><p className="text-sm text-slate-400">Inventory in latest sample</p><p className="mt-2 text-3xl font-black">{overview.available_latest_count}</p></div>
      </section>

      <div className="mt-8"><PriceCollector token={token} /></div>

      <section className="mt-8 rounded-3xl border border-white/10 bg-white/[0.04] p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h2 className="text-2xl font-bold">Market signals / video ideas</h2>
            <p className="mt-1 text-sm text-slate-400">Deterministic signals from clean PriceSift snapshots. No AI call and no trend is claimed until enough prior observations exist.</p>
          </div>
          <button type="button" onClick={() => void loadSignals()} className="rounded-xl border border-white/10 px-3 py-2 text-sm text-slate-300 hover:bg-white/[0.06]">Refresh signals</button>
        </div>

        {signalError ? <p className="mt-4 rounded-2xl border border-amber-300/20 bg-amber-300/10 p-3 text-sm text-amber-100">{signalError}</p> : null}

        {signals ? (
          <>
            <div className="mt-5 grid gap-3 sm:grid-cols-3">
              <div className="rounded-2xl bg-slate-950/40 p-4"><p className="text-xs uppercase tracking-wide text-slate-500">Ready products</p><p className="mt-1 text-2xl font-black">{signals.ready_product_count}</p></div>
              <div className="rounded-2xl bg-slate-950/40 p-4"><p className="text-xs uppercase tracking-wide text-slate-500">Still building</p><p className="mt-1 text-2xl font-black">{signals.building_product_count}</p></div>
              <div className="rounded-2xl bg-slate-950/40 p-4"><p className="text-xs uppercase tracking-wide text-slate-500">Video-worthy now</p><p className="mt-1 text-2xl font-black">{signals.video_worthy_count}</p></div>
            </div>

            <div className="mt-5 space-y-3">
              {signals.signals.map((signal) => (
                <article key={signal.product_id} className="rounded-2xl border border-white/10 bg-slate-950/30 p-4">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <h3 className="font-bold text-white">{signal.product_label}</h3>
                        <span className="rounded-full border border-white/10 px-2 py-0.5 text-xs capitalize text-slate-300">{signalLabel(signal.primary_signal)}</span>
                        {signal.video_worthy ? <span className="rounded-full bg-white px-2 py-0.5 text-xs font-bold text-slate-950">VIDEO</span> : null}
                      </div>
                      <p className="mt-2 text-sm leading-6 text-slate-300">{signal.story_angle}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs uppercase tracking-wide text-slate-500">Video score</p>
                      <p className="text-2xl font-black text-white">{signal.video_score.toFixed(1)}</p>
                      <p className="text-xs capitalize text-slate-500">{signal.confidence} confidence</p>
                    </div>
                  </div>
                  <div className="mt-4 grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-5">
                    <div><p className="text-xs text-slate-500">Current median</p><p className="font-semibold text-white">{money(signal.latest_median_price)}</p></div>
                    <div><p className="text-xs text-slate-500">Prior median</p><p className="font-semibold text-white">{money(signal.baseline_median_price)}</p></div>
                    <div><p className="text-xs text-slate-500">Median move</p><p className="font-semibold text-white">{percent(signal.median_change_percent)}</p></div>
                    <div><p className="text-xs text-slate-500">Current best</p><p className="font-semibold text-white">{money(signal.latest_best_price)}</p></div>
                    <div><p className="text-xs text-slate-500">Clean listings</p><p className="font-semibold text-white">{signal.latest_eligible_count}</p></div>
                  </div>
                </article>
              ))}
              {signals.signals.length === 0 ? <p className="rounded-2xl bg-slate-950/30 p-4 text-sm text-slate-400">No meaningful signal yet. That is a valid result: PriceSift will keep collecting history until a move is supported by enough observations.</p> : null}
            </div>
          </>
        ) : <p className="mt-5 text-sm text-slate-500">Loading market signals…</p>}
      </section>

      <section className="mt-8 rounded-3xl border border-white/10 bg-white/[0.04] p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-2xl font-bold">Observed products</h2>
          <button type="button" onClick={() => void load()} className="rounded-xl border border-white/10 px-3 py-2 text-sm text-slate-300 hover:bg-white/[0.06]">Refresh</button>
        </div>
        <div className="mt-5 overflow-x-auto">
          <table className="w-full min-w-[1050px] text-left text-sm">
            <thead className="text-slate-500"><tr><th className="py-2 pr-4">Product</th><th className="py-2 pr-4">Category</th><th className="py-2 pr-4">Latest best</th><th className="py-2 pr-4">Eligible</th><th className="py-2 pr-4">Typical range</th><th className="py-2 pr-4">Availability</th><th className="py-2 pr-4">Snapshots</th><th className="py-2 pr-4">Last observed</th></tr></thead>
            <tbody className="divide-y divide-white/10 text-slate-300">
              {overview.products.map((product) => (
                <tr key={product.product_id}>
                  <td className="py-3 pr-4 font-semibold text-white">{product.product_label}</td>
                  <td className="py-3 pr-4">{product.category}</td>
                  <td className="py-3 pr-4">{money(product.latest_best_price)}</td>
                  <td className="py-3 pr-4">{product.latest_eligible_count}</td>
                  <td className="py-3 pr-4">{product.history_ready ? `${money(product.typical_low_price)}–${money(product.typical_high_price)}` : "Building"}</td>
                  <td className="py-3 pr-4">{percent(product.availability_rate)}</td>
                  <td className="py-3 pr-4">{product.snapshot_count}</td>
                  <td className="py-3 pr-4 text-slate-400">{dateLabel(product.last_observed_at)}</td>
                </tr>
              ))}
              {overview.products.length === 0 ? <tr><td colSpan={8} className="py-5 text-slate-500">No snapshots yet. Live searches and QA runs will begin filling this table automatically.</td></tr> : null}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}
