"use client";

import { useState } from "react";
import type {
  AnalyticsCategoryRow,
  AnalyticsDigest,
  AnalyticsTopSearch,
} from "@/lib/api";
import { allIndexedProducts } from "@/lib/allIndexedProducts";

type Props = {
  digest: AnalyticsDigest;
};

type DemandCategoryRow = AnalyticsCategoryRow & {
  demand_searches?: number;
  demand_no_results?: number;
  seo_page_searches?: number;
  last_24h_searches?: number;
  last_24h_demand_searches?: number;
  last_24h_seo_page_searches?: number;
};

type DemandTopSearch = AnalyticsTopSearch & {
  demand_searches?: number;
  demand_no_results?: number;
  seo_page_searches?: number;
  last_24h_searches?: number;
  last_24h_demand_searches?: number;
  last_24h_seo_page_searches?: number;
};

type DemandUnresolvedSearch = AnalyticsDigest["top_unresolved_searches"][number] & {
  last_24h_searches?: number;
};

type AnalyticsForensics = {
  rapid_repeat_window_seconds: number;
  rapid_repeat_count: number;
  rapid_repeat_rate: number | null;
  busiest_minute_searches: number;
  minutes_with_10_or_more_searches: number;
  minutes_with_20_or_more_searches: number;
};

type ExtendedDigest = AnalyticsDigest & {
  demand_search_count?: number;
  seo_page_search_count?: number;
  seo_origin_tracking_note?: string;
  last_24h_search_count?: number;
  last_24h_demand_search_count?: number;
  last_24h_seo_page_search_count?: number;
  last_24h_resolved_count?: number;
  last_24h_with_results_count?: number;
  last_24h_no_result_count?: number;
  last_24h_unresolved_count?: number;
  last_24h_us_only_count?: number;
  forensics?: AnalyticsForensics;
};

function normalizeLabel(value: string): string {
  return value
    .toLowerCase()
    .replace(/\bbody\b/g, "")
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

export function AdminAnalyticsDigest({ digest }: Props) {
  const [copyStatus, setCopyStatus] = useState<"idle" | "summary" | "json" | "error">("idle");
  const extended = digest as ExtendedDigest;
  const unresolvedSearches = (digest.top_unresolved_searches || []) as DemandUnresolvedSearch[];
  const categoryRows = digest.category_rows as DemandCategoryRow[];
  const topSearches = digest.top_searches as DemandTopSearch[];
  const demandSearchCount = extended.demand_search_count ?? digest.search_count;
  const seoPageSearchCount = extended.seo_page_search_count ?? 0;
  const indexedKeys = new Set(
    allIndexedProducts.flatMap((product) => [
      `${product.category}:${normalizeLabel(product.title)}`,
      `${product.category}:${normalizeLabel(product.query)}`,
    ]),
  );

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
            Search and click trends only. No IP addresses, accounts, or cookies are stored. SEO-page launches are tracked separately so curated pages do not masquerade as fresh search demand. Parenthetical +X counts are the rolling last 24 hours.
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

      <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-8">
        <Metric label="Searches" value={String(digest.search_count)} recent={extended.last_24h_search_count} />
        <Metric label="Demand searches" value={String(demandSearchCount)} recent={extended.last_24h_demand_search_count} />
        <Metric label="SEO launches" value={String(seoPageSearchCount)} recent={extended.last_24h_seo_page_search_count} />
        <Metric label="With results" value={String(digest.with_results_count)} recent={extended.last_24h_with_results_count} />
        <Metric label="No-result rate" value={formatPercent(digest.no_result_rate)} />
        <Metric label="Unresolved" value={String(digest.unresolved_count ?? 0)} recent={extended.last_24h_unresolved_count} />
        <Metric label="Tracked clicks" value={String(digest.click_count)} />
        <Metric label="US-only use" value={formatPercent(digest.us_only_rate)} />
      </div>

      {extended.seo_origin_tracking_note ? (
        <p className="mt-4 rounded-2xl border border-cyan-300/15 bg-cyan-300/[0.05] px-4 py-3 text-xs leading-5 text-cyan-100/80">
          {extended.seo_origin_tracking_note}
        </p>
      ) : null}

      {digest.historical_click_count > 0 ? (
        <p className="mt-4 rounded-2xl border border-amber-300/20 bg-amber-300/10 px-4 py-3 text-sm text-amber-100">
          {digest.historical_click_count} older click{digest.historical_click_count === 1 ? "" : "s"} occurred in this window but could not be linked to a tracked search. They are excluded from the click rate and provider totals.
        </p>
      ) : null}

      <div className="mt-5 grid gap-5 lg:grid-cols-3">
        <div className="rounded-2xl border border-white/10 bg-slate-950/35 p-4">
          <h3 className="font-bold">Categories</h3>
          <div className="mt-3 space-y-2 text-sm">
            {categoryRows.slice(0, 10).map((row) => (
              <div key={row.category} className="flex items-center justify-between gap-4 border-b border-white/5 pb-2">
                <span className="font-semibold capitalize text-slate-200">{row.category}</span>
                <span className="text-right text-slate-400">
                  {row.demand_searches ?? row.searches} demand · {row.searches} total
                  {row.last_24h_searches !== undefined ? ` (+${row.last_24h_searches} 24h)` : ""} · {row.clicks} clicks
                </span>
              </div>
            ))}
            {categoryRows.length === 0 ? <p className="text-slate-500">No public searches logged yet.</p> : null}
          </div>
        </div>

        <div className="rounded-2xl border border-emerald-300/20 bg-emerald-300/[0.04] p-4">
          <h3 className="font-bold text-emerald-100">Top searches</h3>
          <p className="mt-1 text-xs leading-5 text-slate-500">
            One list now handles both demand and SEO opportunities. Curated pages are marked; unresolved products live in the next panel.
          </p>
          <div className="mt-3 space-y-2 text-sm">
            {topSearches.slice(0, 10).map((row, index) => {
              const indexed = indexedKeys.has(`${row.category}:${normalizeLabel(row.label)}`);
              const demandSearches = row.demand_searches ?? row.searches;
              const seoLaunches = row.seo_page_searches ?? 0;
              return (
                <div key={`${row.product_id || row.label}-${index}`} className="border-b border-white/5 pb-2">
                  <div className="flex items-start justify-between gap-3">
                    <p className="font-semibold text-slate-200">{row.label}</p>
                    <span className={`shrink-0 rounded-full px-2 py-0.5 text-[11px] font-bold ${indexed ? "bg-cyan-300/10 text-cyan-200" : "bg-emerald-300/10 text-emerald-200"}`}>
                      {indexed ? "SEO page live" : "SEO candidate"}
                    </span>
                  </div>
                  <p className="mt-1 text-xs text-slate-500">
                    {row.category} · {demandSearches} demand · {row.searches} total
                    {row.last_24h_searches !== undefined ? ` (+${row.last_24h_searches} 24h)` : ""}
                    {seoLaunches > 0 ? ` · ${seoLaunches} SEO launches` : ""}
                    {` · ${row.no_results} empty · ${row.clicks} clicks`}
                  </p>
                </div>
              );
            })}
            {topSearches.length === 0 ? <p className="text-slate-500">No public searches logged yet.</p> : null}
          </div>
        </div>

        <div className="rounded-2xl border border-amber-300/20 bg-amber-300/[0.04] p-4">
          <h3 className="font-bold text-amber-100">Unresolved demand</h3>
          <p className="mt-1 text-xs leading-5 text-slate-500">
            These queries need catalog support first. Obvious punctuation, casing, and typo variants are grouped conservatively.
          </p>
          <div className="mt-3 space-y-2 text-sm">
            {unresolvedSearches.slice(0, 10).map((row, index) => (
              <div key={`${row.category}-${row.normalized_query}-${index}`} className="border-b border-white/5 pb-2">
                <div className="flex items-start justify-between gap-3">
                  <p className="font-semibold text-amber-100">{row.query}</p>
                  <span className="shrink-0 rounded-full bg-amber-300/10 px-2 py-0.5 text-xs font-bold text-amber-200">
                    {row.searches}
                  </span>
                </div>
                <p className="mt-1 text-xs text-slate-500">
                  {row.category} · catalog support needed first
                  {row.last_24h_searches !== undefined ? ` · +${row.last_24h_searches} 24h` : ""}
                  {row.variants.length > 1 ? ` · ${row.variants.length} grouped variants` : ""}
                </p>
                {row.variants.length > 1 ? (
                  <p className="mt-1 text-xs leading-5 text-slate-600">
                    {row.variants.map((variant) => `${variant.query} (${variant.searches})`).join(" · ")}
                  </p>
                ) : null}
              </div>
            ))}
            {unresolvedSearches.length === 0 ? (
              <p className="text-slate-500">No unresolved public searches in this period.</p>
            ) : null}
          </div>
        </div>
      </div>

      <div className="mt-5 grid gap-5 lg:grid-cols-2">
        <div className="rounded-2xl border border-violet-300/20 bg-violet-300/[0.04] p-4">
          <h3 className="font-bold text-violet-100">Provider performance</h3>
          <p className="mt-1 text-xs leading-5 text-slate-500">Verified outbound clicks by marketplace/provider.</p>
          <div className="mt-3 space-y-2 text-sm">
            {Object.entries(digest.provider_click_counts || {})
              .sort((left, right) => right[1] - left[1])
              .map(([provider, clicks]) => (
                <div key={provider} className="flex items-center justify-between gap-4 border-b border-white/5 pb-2">
                  <span className="font-semibold text-violet-100">{provider}</span>
                  <span className="text-slate-400">{clicks} clicks</span>
                </div>
              ))}
            {Object.keys(digest.provider_click_counts || {}).length === 0 ? (
              <p className="text-slate-500">No provider clicks in this period.</p>
            ) : null}
          </div>
        </div>

        <div className="rounded-2xl border border-sky-300/20 bg-sky-300/[0.04] p-4">
          <h3 className="font-bold text-sky-100">Traffic forensics</h3>
          <p className="mt-1 text-xs leading-5 text-slate-500">Burst signals are diagnostic only, not proof that traffic is automated.</p>
          {extended.forensics ? (
            <div className="mt-3 grid grid-cols-2 gap-3 text-sm">
              <MiniMetric label="Rapid repeats" value={`${extended.forensics.rapid_repeat_count} (${formatPercent(extended.forensics.rapid_repeat_rate)})`} />
              <MiniMetric label="Busiest minute" value={String(extended.forensics.busiest_minute_searches)} />
              <MiniMetric label="Minutes 10+" value={String(extended.forensics.minutes_with_10_or_more_searches)} />
              <MiniMetric label="Minutes 20+" value={String(extended.forensics.minutes_with_20_or_more_searches)} />
            </div>
          ) : (
            <p className="mt-3 text-sm text-slate-500">No forensic data available.</p>
          )}
        </div>
      </div>

      <details className="mt-5 rounded-2xl border border-white/10 bg-slate-950/35 p-4">
        <summary className="cursor-pointer font-semibold text-slate-200">Paste-ready summary</summary>
        <pre className="mt-4 overflow-x-auto whitespace-pre-wrap text-xs leading-6 text-slate-400">{digest.summary_text}</pre>
      </details>
    </section>
  );
}

function Metric({ label, value, recent }: { label: string; value: string; recent?: number }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.05] p-4">
      <p className="text-xs uppercase tracking-[0.15em] text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-black text-white">
        {value}
        {recent !== undefined ? (
          <span className="ml-2 text-sm font-bold text-cyan-200">(+{recent})</span>
        ) : null}
      </p>
    </div>
  );
}

function MiniMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-slate-950/30 p-3">
      <p className="text-[11px] uppercase tracking-[0.12em] text-slate-500">{label}</p>
      <p className="mt-1 font-bold text-slate-200">{value}</p>
    </div>
  );
}
