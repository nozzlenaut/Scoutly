"use client";

import { buildOutboundUrl } from "@/lib/api";
import {
  buildAmazonAllOptionsUrl,
  buildAmazonRenewedSearchUrl,
  buildAmazonUsedSearchUrl,
} from "@/lib/amazon";

export function AmazonLensFallback({ query }: { query: string }) {
  const usedUrl = buildOutboundUrl(buildAmazonUsedSearchUrl(query), {
    query,
    category: "lenses",
    provider: "Amazon",
    title: `Amazon used search: ${query}`,
  });
  const renewedUrl = buildOutboundUrl(buildAmazonRenewedSearchUrl(query), {
    query,
    category: "lenses",
    provider: "Amazon",
    title: `Amazon Renewed search: ${query}`,
  });
  const allOptionsUrl = buildOutboundUrl(buildAmazonAllOptionsUrl(query), {
    query,
    category: "lenses",
    provider: "Amazon",
    title: `Amazon all options search: ${query}`,
  });

  return (
    <div className="mt-5 rounded-2xl border border-ps-warning/40 bg-amber-50 p-4">
      <p className="text-xs font-bold uppercase tracking-[0.18em] text-ps-warning">
        Also check Amazon · paid links
      </p>
      <p className="mt-2 text-sm leading-6 text-ps-text-secondary">
        Amazon pricing and availability are not verified by PriceSift yet. These shortcuts favor the exact lens name,
        but Amazon may mix conditions or sellers.
      </p>
      <div className="mt-3 flex flex-wrap gap-2">
        <a href={usedUrl} target="_blank" rel="sponsored noreferrer" className="rounded-xl bg-ps-accent-strong px-4 py-2 text-sm font-bold text-white hover:bg-ps-accent-hover">
          Search used
        </a>
        <a href={renewedUrl} target="_blank" rel="sponsored noreferrer" className="rounded-xl border border-ps-border bg-ps-surface px-4 py-2 text-sm font-semibold text-ps-accent-hover hover:bg-ps-accent-soft">
          Search Renewed
        </a>
        <a href={allOptionsUrl} target="_blank" rel="sponsored noreferrer" className="rounded-xl border border-ps-border bg-ps-surface px-4 py-2 text-sm font-semibold text-ps-accent-hover hover:bg-ps-accent-soft">
          All options
        </a>
      </div>
    </div>
  );
}
