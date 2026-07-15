"use client";

import { useState } from "react";
import type { AnalyticsDigest } from "@/lib/api";

type Props = {
  digest: AnalyticsDigest;
};

export function AdminAnalyticsDigest({ digest }: Props) {
  const [copyStatus, setCopyStatus] = useState<"idle" | "summary" | "json" | "error">("idle");

  async function copy(value: string, nextStatus: "summary" | "json") {
    try {
      await navigator.clipboard.writeText(value);
      setCopyStatus(nextStatus);
    } catch {
      setCopyStatus("error");
    }
    window.setTimeout(() => setCopyStatus("idle"), 2200);
  }

  function formatPercent(value: number | null): string {
    return value == null ? "—" : `${value.toFixed(1)}%`;
  }

  return (
    <section className="mt-10 rounded-3xl border border-cyan-200/15 bg-cyan-200/[0.04] p-5">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan-200">Light analytics</p>
          <h2 className="mt-2 text-2xl font-black">Last {digest.days} days</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
            Search and click trends only. No IP addresses, accounts, cookies, or personal identifiers are stored.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => copy(digest.summary_text, "summary")}
            className="rounded-2xl bg-cyan-200 px-4 py-2 text-sm font-bold text-slate-950 transition hover:bg-cyan-100"
          >
            {copyStatus === "summary" ? "Summary copied" : "Copy summary"}
          </button>
          <button
            type="button"
            onClick={() => copy(JSON.stringify(digest, null, 2), "json")}
            className="rounded-2xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200 transition hover:bg-white/[0.08]"
          >
            {copyStatus === "json" ? "JSON copied" : "Copy full JSON"}
          </button>
        </div>
      </div>

      {copyStatus === "error" ? <p className="mt-3 text-sm text-amber-200">Clipboard access failed. Select the text below manually.</p> : null}

      <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-6">
        <Metric label="Searches" value={String(digest.search_count)} />
        <Metric label="With results" value={String(digest.with_results_count)} />
        <Metric label="No-result rate" value={formatPercent(digest.no_result_rate)} />
        <Metric label="Listing clicks" value={String(digest.click_count)} />
        <Metric label="Approx. click rate" value={formatPercent(digest.approximate_click_rate)} />
        <Metric label="US-only use" value={formatPercent(digest.us_only_rate)} />
      </div>

      <div className="mt-5 grid gap-5 lg:grid-cols-2">
        <div className="rounded-2xl border border-white/10 bg-slate-950/35 p-4">
          <h3 className="font-bold">Categories</h3>
          <div className="mt-3 space-y-2 text-sm">
            {digest.category_rows.slice(0, 10).map((row) => (
              <div key={row.category} className="flex items-center justify-between gap-4 border-b border-white/5 pb-2">
                <span className="font-semibold capitalize text-slate-200">{row.category}</span>
                <span className="text-right text-slate-400">{row.searches} searches · {row.no_results} empty · {row.clicks} clicks</span>
              </div>
            ))}
            {digest.category_rows.length === 0 ? <p className="text-slate-500">No public searches logged yet.</p> : null}
          </div>
        </div>

        <div className="rounded-2xl border border-white/10 bg-slate-950/35 p-4">
          <h3 className="font-bold">Most searched</h3>
          <div className="mt-3 space-y-2 text-sm">
            {digest.top_searches.slice(0, 10).map((row, index) => (
              <div key={`${row.product_id || row.label}-${index}`} className="border-b border-white/5 pb-2">
                <p className="font-semibold text-slate-200">{row.label}</p>
                <p className="mt-1 text-xs text-slate-500">{row.category} · {row.searches} searches · {row.no_results} empty · {row.clicks} clicks</p>
              </div>
            ))}
            {digest.top_searches.length === 0 ? <p className="text-slate-500">No public searches logged yet.</p> : null}
          </div>
        </div>
      </div>

      <details className="mt-5 rounded-2xl border border-white/10 bg-slate-950/35 p-4">
        <summary className="cursor-pointer font-semibold text-slate-200">Paste-ready summary</summary>
        <pre className="mt-4 overflow-x-auto whitespace-pre-wrap text-xs leading-6 text-slate-400">{digest.summary_text}</pre>
      </details>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.05] p-4">
      <p className="text-xs uppercase tracking-[0.15em] text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-black text-white">{value}</p>
    </div>
  );
}
