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
    <div className="mt-5 rounded-2xl border border-orange-300/20 bg-orange-300/[0.05] p-4">
      <p className="text-xs font-bold uppercase tracking-[0.18em] text-orange-200">
        Also check Amazon · paid links
      </p>
      <p className="mt-2 text-sm leading-6 text-slate-300">
        Amazon pricing and availability are not verified by PriceSift yet. These shortcuts favor the exact lens name,
        but Amazon may mix conditions or sellers.
      </p>
      <div className="mt-3 flex flex-wrap gap-2">
        <a href={usedUrl} target="_blank" rel="sponsored noreferrer" className="rounded-xl bg-orange-200 px-4 py-2 text-sm font-bold text-slate-950 hover:bg-orange-100">
          Search used
        </a>
        <a href={renewedUrl} target="_blank" rel="sponsored noreferrer" className="rounded-xl border border-white/15 bg-white/[0.06] px-4 py-2 text-sm font-semibold text-white hover:bg-white/[0.1]">
          Search Renewed
        </a>
        <a href={allOptionsUrl} target="_blank" rel="sponsored noreferrer" className="rounded-xl border border-white/15 bg-white/[0.06] px-4 py-2 text-sm font-semibold text-white hover:bg-white/[0.1]">
          All options
        </a>
      </div>
    </div>
  );
}
