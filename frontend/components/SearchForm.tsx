"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { suggestProducts, type ProductMatch } from "@/lib/api";
import { getCategory, searchCategories } from "@/lib/categoryCatalog";
import { StatusBadge } from "@/components/StatusBadge";

export function SearchForm() {
  const [categoryId, setCategoryId] = useState(searchCategories[0].id);
  const selectedCategory = getCategory(categoryId);
  const [query, setQuery] = useState(selectedCategory.defaultQuery);
  const [suggestions, setSuggestions] = useState<ProductMatch[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    setQuery(selectedCategory.defaultQuery);
    setSuggestions([]);
  }, [selectedCategory.defaultQuery]);

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
      const matches = await suggestProducts(cleaned, categoryId);
      setSuggestions(matches);
      setShowSuggestions(true);
      setIsLoading(false);
    }, 180);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [categoryId, query]);

  function submitSearch(value = query) {
    const cleaned = value.trim();
    if (!cleaned) return;
    router.push(`/search?category=${encodeURIComponent(categoryId)}&q=${encodeURIComponent(cleaned)}`);
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
    <div className="mx-auto w-full max-w-3xl rounded-[2rem] border border-white/10 bg-slate-950/35 p-4 text-left shadow-2xl shadow-black/30 backdrop-blur sm:p-5">
      <div className="mb-4">
        <p className="mb-2 text-xs uppercase tracking-[0.22em] text-slate-500">Choose a category</p>
        <div className="flex flex-wrap gap-2">
          {searchCategories.map((category) => {
            const isSelected = category.id === categoryId;
            return (
              <button
                key={category.id}
                type="button"
                onClick={() => setCategoryId(category.id)}
                className={`flex items-center gap-2 rounded-2xl border px-4 py-3 text-sm font-semibold transition ${
                  isSelected
                    ? "border-white bg-white text-slate-950"
                    : "border-white/10 bg-white/[0.04] text-slate-300 hover:bg-white/[0.08]"
                }`}
              >
                <span>{category.label}</span>
                <StatusBadge status={category.status} />
              </button>
            );
          })}
        </div>
        <p className="mt-3 text-sm text-slate-400">
          {selectedCategory.group} · {selectedCategory.description}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="relative flex w-full flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            onFocus={() => setShowSuggestions(true)}
            placeholder={selectedCategory.placeholder}
            className="min-h-14 w-full rounded-2xl border border-white/10 bg-white/10 px-5 text-base text-white outline-none placeholder:text-slate-400 focus:border-cyan-300"
          />

          {showSuggestions && suggestions.length > 0 ? (
            <div className="absolute left-0 right-0 top-16 z-20 overflow-hidden rounded-2xl border border-white/10 bg-slate-950/95 text-left shadow-2xl shadow-black/50 backdrop-blur">
              <div className="border-b border-white/10 px-4 py-2 text-xs uppercase tracking-[0.2em] text-slate-500">
                Matching {selectedCategory.label.toLowerCase()}
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
                      {match.product.category_label} · {match.product.product_type.replace("_", " ")}
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
        Start typing, pick the exact item from autocomplete, then Scoutly finds the best used listing.
        {isLoading ? " Checking catalog..." : ""}
      </p>
    </div>
  );
}
