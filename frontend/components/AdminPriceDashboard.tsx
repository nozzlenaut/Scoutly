"use client";

import { useCallback, useEffect, useState } from "react";
import { PriceCollector } from "@/components/PriceCollector";
import { getPriceOverview, type PriceOverview } from "@/lib/api";

function money(value?: number | null): string {
  return value === null || value === undefined ? "—" : `$${value.toFixed(2)}`;
}

function dateLabel(value?: string | null): string {
  if (!value) return "—";
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
}

export function AdminPriceDashboard({ token }: { token: string }) {
  const [overview, setOverview] = useState<PriceOverview | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    setStatus("loading");
    setErrorMessage(null);
    try {
      setOverview(await getPriceOverview(token, 30));
      setStatus("ready");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown price-history error");
      setStatus("error");
    }
  }, [token]);

  useEffect(() => { void load(); }, [load]);

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
                  <td className="py-3 pr-4">{product.availability_rate == null ? "—" : `${product.availability_rate.toFixed(1)}%`}</td>
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
