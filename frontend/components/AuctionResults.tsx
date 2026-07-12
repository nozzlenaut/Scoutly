"use client";

import { useEffect, useState } from "react";
import { ResultCard } from "@/components/ResultCard";
import { searchAuctions, type SearchResult } from "@/lib/api";

type Props = {
  query: string;
  category: string;
  productId?: string;
};

export function AuctionResults({ query, category, productId }: Props) {
  const [status, setStatus] = useState<"loading" | "done" | "error">("loading");
  const [results, setResults] = useState<SearchResult[]>([]);

  useEffect(() => {
    let cancelled = false;

    async function loadAuctions() {
      setStatus("loading");
      try {
        const data = await searchAuctions(query, category, "ebay", { auctionHours: 24 });
        if (cancelled) return;
        setResults(data.auction_results || []);
        setStatus("done");
      } catch {
        if (cancelled) return;
        setStatus("error");
      }
    }

    loadAuctions();

    return () => {
      cancelled = true;
    };
  }, [category, query]);

  return (
    <section className="mt-10 rounded-3xl border border-white/10 bg-white/[0.035] p-5">
      <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
        <div>
          <p className="text-sm uppercase tracking-[0.25em] text-slate-500">Auction comparison</p>
          <h2 className="mt-2 text-2xl font-black">Ending soon</h2>
          <p className="mt-2 max-w-2xl text-sm text-slate-400">
            Buy It Now results load first. Scoutly checks auctions after that so the page stays fast.
          </p>
        </div>
        {status === "loading" ? (
          <div className="flex items-center gap-3 rounded-2xl border border-cyan-300/20 bg-cyan-300/10 px-4 py-3 text-sm font-semibold text-cyan-100">
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-cyan-100/30 border-t-cyan-100" />
            Checking auctions…
          </div>
        ) : null}
      </div>

      {status === "done" && results.length > 0 ? (
        <div className="mt-5 grid gap-5 xl:grid-cols-3">
          {results.map((result) => (
            <ResultCard
              key={`auction-${result.provider}-${result.title}`}
              result={result}
              query={query}
              category={category}
              productId={productId}
              variant="auction"
            />
          ))}
        </div>
      ) : null}

      {status === "done" && results.length === 0 ? (
        <div className="mt-5 rounded-3xl border border-white/10 bg-white/[0.04] p-5 text-sm text-slate-400">
          No safe auction ending soon found for this exact item.
        </div>
      ) : null}

      {status === "error" ? (
        <div className="mt-5 rounded-3xl border border-amber-300/20 bg-amber-300/10 p-5 text-sm text-amber-100">
          Auction check failed. Buy It Now results are still usable.
        </div>
      ) : null}
    </section>
  );
}
