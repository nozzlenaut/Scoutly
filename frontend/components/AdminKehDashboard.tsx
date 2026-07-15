"use client";

import { useMemo, useState } from "react";
import { getKehOverview, syncKehFeed, type KehOverview } from "@/lib/api";

function money(value: number, currency = "USD"): string {
  try {
    return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(value);
  } catch {
    return `$${value.toFixed(2)}`;
  }
}

function dateLabel(value?: string | null): string {
  if (!value) return "Never";
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
}

export function AdminKehDashboard({ initialOverview, token }: { initialOverview: KehOverview; token: string }) {
  const [overview, setOverview] = useState(initialOverview);
  const [filter, setFilter] = useState<"all" | "matched" | "unmatched" | "ambiguous">("all");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const items = useMemo(
    () => overview.items.filter((item) => filter === "all" || item.match_status === filter),
    [overview.items, filter],
  );

  async function refresh() {
    setBusy(true);
    setMessage(null);
    try {
      setOverview(await getKehOverview(token, 1000));
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not refresh KEH overview.");
    } finally {
      setBusy(false);
    }
  }

  async function sync() {
    setBusy(true);
    setMessage(null);
    try {
      const run = await syncKehFeed(token);
      setMessage(`Sync complete: ${run.matched_items} matched pilot listings from ${run.scoped_items} camera/lens items.`);
      setOverview(await getKehOverview(token, 1000));
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "KEH sync failed.");
    } finally {
      setBusy(false);
    }
  }

  const latest = overview.latest_sync;
  return (
    <>
      <section className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5"><p className="text-sm text-slate-400">Feed status</p><p className={`mt-2 text-xl font-black ${overview.configured && overview.enabled ? "text-emerald-300" : "text-amber-300"}`}>{overview.configured ? (overview.enabled ? "Ready" : "Disabled") : "URL missing"}</p></div>
        <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5"><p className="text-sm text-slate-400">Scoped inventory</p><p className="mt-2 text-3xl font-black">{overview.active_item_count}</p></div>
        <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5"><p className="text-sm text-slate-400">Matched listings</p><p className="mt-2 text-3xl font-black">{overview.matched_count}</p></div>
        <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5"><p className="text-sm text-slate-400">Pilot products found</p><p className="mt-2 text-3xl font-black">{overview.matched_product_count}/{overview.pilot_product_ids.length}</p></div>
        <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5"><p className="text-sm text-slate-400">Public results</p><p className="mt-2 text-xl font-black text-cyan-200">{overview.public_results_enabled ? "Enabled" : "Shadow only"}</p></div>
      </section>

      <section className="mt-8 rounded-3xl border border-white/10 bg-white/[0.04] p-5">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold">Feed sync</h2>
            <p className="mt-1 text-sm text-slate-500">Last run: {dateLabel(latest?.completed_at)}</p>
          </div>
          <div className="flex gap-3">
            <button type="button" onClick={() => void refresh()} disabled={busy} className="rounded-2xl border border-white/10 px-4 py-2 font-semibold text-slate-200 disabled:opacity-50">Refresh</button>
            <button type="button" onClick={() => void sync()} disabled={busy || !overview.configured || !overview.enabled} className="rounded-2xl bg-cyan-200 px-5 py-2 font-bold text-slate-950 disabled:cursor-not-allowed disabled:opacity-40">{busy ? "Working…" : "Sync KEH now"}</button>
          </div>
        </div>
        {latest ? <p className="mt-4 text-sm text-slate-400">Feed rows {latest.feed_items} · camera/lens rows {latest.scoped_items} · matched {latest.matched_items} · unmatched {latest.unmatched_items} · ambiguous {latest.ambiguous_items}</p> : null}
        {message ? <p className="mt-4 rounded-2xl border border-cyan-200/20 bg-cyan-200/10 p-3 text-sm text-cyan-50">{message}</p> : null}
        {!overview.configured ? <p className="mt-4 text-sm text-amber-200">Add AWIN_KEH_FEED_URL to Railway before syncing.</p> : null}
        {overview.configured && !overview.enabled ? <p className="mt-4 text-sm text-amber-200">Set KEH_FEED_ENABLED=true in Railway to allow shadow syncs.</p> : null}
      </section>

      <section className="mt-8 rounded-3xl border border-white/10 bg-white/[0.04] p-5">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div><h2 className="text-2xl font-bold">Shadow inventory</h2><p className="mt-1 text-sm text-slate-500">The 12 camera QA products plus the two body models in the sample feed are eligible to match by default.</p></div>
          <select value={filter} onChange={(event) => setFilter(event.target.value as typeof filter)} className="rounded-xl border border-white/10 bg-slate-900 px-3 py-2 text-sm text-white">
            <option value="all">All matches</option><option value="matched">Matched</option><option value="ambiguous">Ambiguous</option><option value="unmatched">Unmatched</option>
          </select>
        </div>
        <div className="mt-5 overflow-x-auto">
          <table className="w-full min-w-[1250px] text-left text-sm">
            <thead className="text-slate-500"><tr><th className="py-2 pr-4">KEH listing</th><th className="py-2 pr-4">Matched PriceSift product</th><th className="py-2 pr-4">Grade</th><th className="py-2 pr-4">Price</th><th className="py-2 pr-4">Status</th><th className="py-2 pr-4">Compare</th></tr></thead>
            <tbody className="divide-y divide-white/10 text-slate-300">
              {items.map((item) => (
                <tr key={item.aw_product_id}>
                  <td className="max-w-xl py-3 pr-4"><a href={item.affiliate_url} target="_blank" rel="noreferrer" className="font-semibold text-white hover:text-cyan-200">{item.title}</a><p className="mt-1 text-xs text-slate-500">KEH ID {item.merchant_product_id || item.aw_product_id}</p></td>
                  <td className="py-3 pr-4">{item.matched_product_label || "—"}<p className="mt-1 text-xs text-slate-500">{item.match_reason || "—"}</p></td>
                  <td className="py-3 pr-4">{item.condition_grade_code || "Used"}<p className="text-xs text-slate-500">{item.condition_grade_label || ""}</p></td>
                  <td className="py-3 pr-4 font-semibold text-white">{money(item.price, item.currency)}</td>
                  <td className="py-3 pr-4"><span className={`rounded-full px-3 py-1 text-xs font-bold ${item.match_status === "matched" ? "bg-emerald-300/15 text-emerald-200" : item.match_status === "ambiguous" ? "bg-amber-300/15 text-amber-200" : "bg-slate-700 text-slate-300"}`}>{item.match_status}</span></td>
                  <td className="py-3 pr-4">{item.matched_product_label ? <a href={`/search?category=cameras&q=${encodeURIComponent(item.matched_product_label)}`} target="_blank" className="text-cyan-200 hover:text-cyan-100">Open eBay search</a> : "—"}</td>
                </tr>
              ))}
              {items.length === 0 ? <tr><td colSpan={6} className="py-5 text-slate-500">No KEH inventory has been synced for this filter yet.</td></tr> : null}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}
