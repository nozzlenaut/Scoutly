"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { suggestProducts, type ProductMatch } from "@/lib/api";

export function SearchForm() {
  const [query, setQuery] = useState("RTX 3060 12GB");
  const [suggestions, setSuggestions] = useState<ProductMatch[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    const cleaned = query.trim();
    if (cleaned.length < 2) {
      setSuggestions([]);
      return;
    }

    debounceRef.current = setTimeout(async () => {
      setIsLoading(true);
      const matches = await suggestProducts(cleaned);
      setSuggestions(matches);
      setShowSuggestions(true);
      setIsLoading(false);
    }, 180);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [query]);

  function submitSearch(value = query) {
    const cleaned = value.trim();
    if (!cleaned) return;
    router.push(`/search?q=${encodeURIComponent(cleaned)}`);
  }

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    submitSearch();
  }

  function pickSuggestion(match: ProductMatch) {
    const value = match.product.display_name;
    setQuery(value);
    setShowSuggestions(false);
    submitSearch(value);
  }

  return (
    <div className="mx-auto w-full max-w-2xl">
      <form onSubmit={handleSubmit} className="relative flex w-full flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            onFocus={() => setShowSuggestions(true)}
            placeholder="Try 3060, rtx3060, rx6700xt..."
            className="min-h-14 w-full rounded-2xl border border-white/10 bg-white/10 px-5 text-base text-white outline-none placeholder:text-slate-400 focus:border-cyan-300"
          />

          {showSuggestions && suggestions.length > 0 ? (
            <div className="absolute left-0 right-0 top-16 z-20 overflow-hidden rounded-2xl border border-white/10 bg-slate-950/95 text-left shadow-2xl shadow-black/50 backdrop-blur">
              <div className="border-b border-white/10 px-4 py-2 text-xs uppercase tracking-[0.2em] text-slate-500">
                Matching products
              </div>
              {suggestions.map((match) => (
                <button
                  key={match.product.id}
                  type="button"
                  onMouseDown={(event) => event.preventDefault()}
                  onClick={() => pickSuggestion(match)}
                  className="flex w-full items-center justify-between gap-4 px-4 py-3 text-left transition hover:bg-white/10"
                >
                  <span>
                    <span className="block font-semibold text-white">{match.product.display_name}</span>
                    <span className="text-xs text-slate-400">
                      {match.product.chipset_brand} · {match.product.generation} · {match.product.memory_type}
                    </span>
                  </span>
                  <span className="rounded-full bg-cyan-300/10 px-2 py-1 text-xs font-medium text-cyan-200">
                    {Math.round(match.confidence * 100)}%
                  </span>
                </button>
              ))}
            </div>
          ) : null}
        </div>

        <button className="min-h-14 rounded-2xl bg-cyan-300 px-7 font-semibold text-slate-950 transition hover:bg-cyan-200">
          Search
        </button>
      </form>

      <p className="mt-3 text-sm text-slate-400">
        Free typing works. The dropdown just helps Scoutly lock onto the exact product.
        {isLoading ? " Checking catalog..." : ""}
      </p>
    </div>
  );
}
