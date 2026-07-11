"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { suggestProducts, type ProductMatch } from "@/lib/api";
import { getCategory, searchCategories } from "@/lib/categoryCatalog";
import { StatusBadge } from "@/components/StatusBadge";

type SearchFormProps = {
  initialCategoryId?: string | null;
  initialQuery?: string | null;
  compact?: boolean;
};

export function SearchForm({ initialCategoryId, initialQuery, compact = false }: SearchFormProps) {
  const initialCategory = getCategory(initialCategoryId);
  const [categoryId, setCategoryId] = useState(initialCategory.id);
  const selectedCategory = getCategory(categoryId);
  const [query, setQuery] = useState(initialQuery?.trim() || initialCategory.defaultQuery);
  const [suggestions, setSuggestions] = useState<ProductMatch[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const didMountRef = useRef(false);
  const wrapperRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  function normalizeMatchValue(value: string | null | undefined) {
    return (value || "").toLowerCase().replace(/[^a-z0-9]+/g, "");
  }

  function hasExactSuggestion(value: string, matches: ProductMatch[]) {
    const normalizedValue = normalizeMatchValue(value);
    if (!normalizedValue) return false;

    return matches.some((match) => {
      if (match.confidence < 0.999) return false;
      return [match.product.display_name, match.matched_alias].some((candidate) =>
        normalizeMatchValue(candidate) === normalizedValue
      );
    });
  }

  useEffect(() => {
    if (!didMountRef.current) {
      didMountRef.current = true;
      return;
    }

    setQuery(selectedCategory.defaultQuery);
    setSuggestions([]);
    setShowSuggestions(false);
  }, [selectedCategory.defaultQuery]);

  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    const cleaned = query.trim();
    if (cleaned.length < 2) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    debounceRef.current = setTimeout(async () => {
      setIsLoading(true);
      const matches = await suggestProducts(cleaned, categoryId);
      setSuggestions(matches);
      setShowSuggestions(matches.length > 0 && !hasExactSuggestion(cleaned, matches));
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

    setShowSuggestions(false);
    inputRef.current?.blur();
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
    <div
      ref={wrapperRef}
      onBlur={(event) => {
        if (!wrapperRef.current?.contains(event.relatedTarget as Node | null)) {
          setShowSuggestions(false);
        }
      }}
      className={`relative z-50 mx-auto w-full rounded-[2rem] border border-white/10 bg-slate-950/35 text-left shadow-2xl shadow-black/30 backdrop-blur ${
        compact ? "max-w-5xl p-3 sm:p-4" : "max-w-3xl p-4 sm:p-5"
      }`}
    >
      <div className={compact ? "mb-3" : "mb-4"}>
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
        {!compact ? (
          <p className="mt-3 text-sm text-slate-400">
            {selectedCategory.group} · {selectedCategory.description}
          </p>
        ) : null}
      </div>

      <form onSubmit={handleSubmit} className="relative flex w-full flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <input
            ref={inputRef}
            value={query}
            onChange={(event) => {
              setQuery(event.target.value);
              setShowSuggestions(false);
            }}
            onFocus={() => {
              setShowSuggestions(suggestions.length > 0 && !hasExactSuggestion(query.trim(), suggestions));
            }}
            placeholder={selectedCategory.placeholder}
            className="min-h-14 w-full rounded-2xl border border-white/10 bg-white/10 px-5 text-base text-white outline-none placeholder:text-slate-400 focus:border-cyan-300"
          />

          {showSuggestions && suggestions.length > 0 ? (
            <div className="absolute left-0 right-0 top-16 z-[100] max-h-80 overflow-y-auto rounded-2xl border border-white/10 bg-slate-950/95 text-left shadow-2xl shadow-black/50 backdrop-blur">
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
        {compact
          ? "Search another exact item without going back."
          : "Start typing, pick the exact item from autocomplete, then Scoutly finds the best used listing."}
        {isLoading ? " Checking catalog..." : ""}
      </p>
    </div>
  );
}
