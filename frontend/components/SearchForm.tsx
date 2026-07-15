"use client";

import { useEffect, useId, useRef, useState } from "react";
import { suggestProducts, type ProductMatch } from "@/lib/api";
import { getCategory, searchCategories } from "@/lib/categoryCatalog";
import { StatusBadge } from "@/components/StatusBadge";
import { SpecSearchBuilder } from "@/components/SpecSearchBuilder";
import { CpuSearchBuilder } from "@/components/CpuSearchBuilder";

type SearchFormProps = {
  initialCategoryId?: string | null;
  initialQuery?: string | null;
  compact?: boolean;
};

function announceSearchStart() {
  window.dispatchEvent(new CustomEvent("pricesift:search-start"));
}

export function SearchForm({
  initialCategoryId,
  initialQuery,
  compact = false,
}: SearchFormProps) {
  const initialCategory = getCategory(initialCategoryId);
  const [categoryId, setCategoryId] = useState(initialCategory.id);
  const selectedCategory = getCategory(categoryId);
  const [query, setQuery] = useState(
    initialQuery === undefined || initialQuery === null
      ? ""
      : initialQuery.trim(),
  );
  const [suggestions, setSuggestions] = useState<ProductMatch[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [suggestionsEnabled, setSuggestionsEnabled] = useState(false);
  const [activeSuggestionIndex, setActiveSuggestionIndex] = useState(-1);
  const [isLoading, setIsLoading] = useState(false);
  const [isNavigating, setIsNavigating] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const didMountRef = useRef(false);
  const requestSequenceRef = useRef(0);
  const wrapperRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const listboxId = useId();
  const inputId = useId();
  const statusId = useId();

  useEffect(() => {
    if (!didMountRef.current) {
      didMountRef.current = true;
      return;
    }

    setQuery("");
    setSuggestions([]);
    setShowSuggestions(false);
    setSuggestionsEnabled(false);
    setActiveSuggestionIndex(-1);
  }, [categoryId]);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);

    if (!suggestionsEnabled) {
      requestSequenceRef.current += 1;
      setSuggestions([]);
      setShowSuggestions(false);
      setActiveSuggestionIndex(-1);
      setIsLoading(false);
      return;
    }

    if (categoryId === "ram" || categoryId === "cpus") {
      requestSequenceRef.current += 1;
      setSuggestions([]);
      setShowSuggestions(false);
      setActiveSuggestionIndex(-1);
      setIsLoading(false);
      return;
    }

    const cleaned = query.trim();
    if (cleaned.length < 2) {
      requestSequenceRef.current += 1;
      setSuggestions([]);
      setShowSuggestions(false);
      setActiveSuggestionIndex(-1);
      setIsLoading(false);
      return;
    }

    const requestSequence = requestSequenceRef.current + 1;
    requestSequenceRef.current = requestSequence;

    debounceRef.current = setTimeout(async () => {
      setIsLoading(true);
      const matches = await suggestProducts(cleaned, categoryId);
      if (requestSequence !== requestSequenceRef.current) return;

      setSuggestions(matches);
      setShowSuggestions(matches.length > 0);
      setActiveSuggestionIndex(matches.length > 0 ? 0 : -1);
      setIsLoading(false);
    }, 180);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [categoryId, query, suggestionsEnabled]);

  function navigate(destination: string) {
    setSuggestionsEnabled(false);
    setShowSuggestions(false);
    setActiveSuggestionIndex(-1);
    inputRef.current?.blur();
    setIsNavigating(true);
    announceSearchStart();
    window.location.assign(destination);
  }

  function submitSearch(value = query) {
    const cleaned = value.trim();
    if (!cleaned) return;

    navigate(
      `/search?category=${encodeURIComponent(categoryId)}&q=${encodeURIComponent(cleaned)}`,
    );
  }

  function handleCategoryChange(nextCategoryId: string) {
    if (nextCategoryId === categoryId) return;

    if (compact) {
      // A results page must never show cards from one category while another
      // category is selected. Start a clean category page immediately.
      navigate(`/search?category=${encodeURIComponent(nextCategoryId)}&q=`);
      return;
    }

    setCategoryId(nextCategoryId);
  }

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    submitSearch();
  }

  function pickSuggestion(match: ProductMatch) {
    const value = match.product.display_name;
    setQuery(value);
    submitSearch(value);
  }

  function handleInputKeyDown(event: React.KeyboardEvent<HTMLInputElement>) {
    if (!showSuggestions || suggestions.length === 0) {
      if (event.key === "ArrowDown" && suggestions.length > 0) {
        event.preventDefault();
        setShowSuggestions(true);
        setActiveSuggestionIndex(0);
      }
      return;
    }

    if (event.key === "ArrowDown") {
      event.preventDefault();
      setActiveSuggestionIndex((current) => (current + 1) % suggestions.length);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setActiveSuggestionIndex((current) =>
        current <= 0 ? suggestions.length - 1 : current - 1,
      );
    } else if (event.key === "Enter" && activeSuggestionIndex >= 0) {
      event.preventDefault();
      pickSuggestion(suggestions[activeSuggestionIndex]);
    } else if (event.key === "Escape") {
      event.preventDefault();
      setShowSuggestions(false);
      setActiveSuggestionIndex(-1);
    }
  }

  return (
    <div
      ref={wrapperRef}
      onBlur={(event) => {
        if (!wrapperRef.current?.contains(event.relatedTarget as Node | null)) {
          setShowSuggestions(false);
          setActiveSuggestionIndex(-1);
        }
      }}
      className={`relative z-50 mx-auto w-full rounded-[2rem] border border-white/10 bg-slate-950/35 text-left shadow-2xl shadow-black/30 backdrop-blur ${
        compact ? "max-w-6xl p-3 sm:p-4" : "max-w-3xl p-4 sm:p-5"
      }`}
    >
      <div className={compact ? "mb-3" : "mb-4"}>
        <p className="mb-2 text-xs uppercase tracking-[0.22em] text-slate-400">
          Choose a category
        </p>
        <div
          className="flex flex-wrap gap-2"
          role="group"
          aria-label="Search category"
        >
          {searchCategories.map((category) => {
            const isSelected = category.id === categoryId;
            return (
              <button
                key={category.id}
                type="button"
                aria-pressed={isSelected}
                disabled={isNavigating}
                onClick={() => handleCategoryChange(category.id)}
                className={`flex items-center gap-2 rounded-2xl border px-4 py-3 text-sm font-semibold transition disabled:cursor-wait disabled:opacity-70 ${
                  isSelected
                    ? "border-white bg-white text-slate-950"
                    : "border-white/10 bg-white/[0.04] text-slate-200 hover:bg-white/[0.08]"
                }`}
              >
                <span>{category.label}</span>
                <StatusBadge status={category.status} selected={isSelected} />
              </button>
            );
          })}
        </div>
        {!compact ? (
          <p className="mt-3 text-sm text-slate-300">
            {selectedCategory.group} · {selectedCategory.description}
          </p>
        ) : null}
      </div>

      {selectedCategory.id === "ram" ? (
        <SpecSearchBuilder
          key={`ram-builder:${initialQuery || "new"}`}
          initialQuery={initialQuery}
          compact={compact}
          isNavigating={isNavigating}
          onSearch={submitSearch}
        />
      ) : selectedCategory.id === "cpus" ? (
        <CpuSearchBuilder
          key={`cpu-builder:${initialQuery || "new"}`}
          initialQuery={initialQuery}
          compact={compact}
          isNavigating={isNavigating}
          onSearch={submitSearch}
        />
      ) : (
        <>
          <form
            onSubmit={handleSubmit}
            className="relative flex w-full flex-col gap-3 sm:flex-row"
          >
            <div className="relative flex-1">
              <label htmlFor={inputId} className="sr-only">
                Search exact {selectedCategory.label.toLowerCase()} item
              </label>
              <input
                id={inputId}
                ref={inputRef}
                value={query}
                onChange={(event) => {
                  setQuery(event.target.value);
                  setSuggestionsEnabled(true);
                  setShowSuggestions(false);
                  setActiveSuggestionIndex(-1);
                }}
                onFocus={() => {
                  setSuggestionsEnabled(true);
                  const shouldShow = suggestions.length > 0;
                  setShowSuggestions(shouldShow);
                  setActiveSuggestionIndex(
                    shouldShow ? Math.max(activeSuggestionIndex, 0) : -1,
                  );
                }}
                onKeyDown={handleInputKeyDown}
                placeholder={selectedCategory.placeholder}
                role="combobox"
                aria-autocomplete="list"
                aria-expanded={showSuggestions}
                aria-controls={showSuggestions ? listboxId : undefined}
                aria-activedescendant={
                  showSuggestions && activeSuggestionIndex >= 0
                    ? `${listboxId}-option-${activeSuggestionIndex}`
                    : undefined
                }
                aria-describedby={statusId}
                className="min-h-14 w-full rounded-2xl border border-white/10 bg-white/10 px-5 text-base text-white outline-none placeholder:text-slate-400 focus:border-cyan-300"
              />

              {showSuggestions && suggestions.length > 0 ? (
                <div
                  id={listboxId}
                  role="listbox"
                  aria-label={`Matching ${selectedCategory.label}`}
                  className="absolute left-0 right-0 top-16 z-[100] max-h-80 overflow-y-auto rounded-2xl border border-white/10 bg-slate-950/95 text-left shadow-2xl shadow-black/50 backdrop-blur"
                >
                  <div className="border-b border-white/10 px-4 py-2 text-xs uppercase tracking-[0.2em] text-slate-400">
                    Catalog matches for {selectedCategory.label.toLowerCase()}
                  </div>
                  {suggestions.map((match, index) => {
                    const selected = index === activeSuggestionIndex;
                    return (
                      <button
                        id={`${listboxId}-option-${index}`}
                        key={match.product.id}
                        type="button"
                        role="option"
                        aria-selected={selected}
                        onMouseDown={(event) => event.preventDefault()}
                        onMouseEnter={() => setActiveSuggestionIndex(index)}
                        onClick={() => pickSuggestion(match)}
                        className={`flex w-full items-center justify-between gap-4 px-4 py-3 text-left transition ${
                          selected ? "bg-white/10" : "hover:bg-white/10"
                        }`}
                      >
                        <span>
                          <span className="block font-semibold text-white">
                            {match.product.display_name}
                          </span>
                          <span className="text-xs text-slate-300">
                            Exact catalog item ·{" "}
                            {match.product.product_type.replace("_", " ")}
                          </span>
                        </span>
                        <span className="rounded-full border border-cyan-300/20 bg-cyan-300/10 px-2 py-1 text-xs font-medium text-cyan-100">
                          Product match {Math.round(match.confidence * 100)}%
                        </span>
                      </button>
                    );
                  })}
                </div>
              ) : null}
            </div>

            <button
              disabled={isNavigating}
              className="flex min-h-14 items-center justify-center gap-3 rounded-2xl bg-cyan-300 px-7 font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-wait disabled:opacity-80"
            >
              {isNavigating ? (
                <>
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-950/20 border-t-slate-950" />
                  Searching…
                </>
              ) : (
                "Search"
              )}
            </button>
          </form>

          <p
            id={statusId}
            aria-live="polite"
            className="mt-3 text-sm text-slate-300"
          >
            Type or pick a supported catalog item. Unsupported text will not be
            sent to the marketplace.
            {isLoading ? " Checking catalog…" : ""}
            {isNavigating ? " Loading fresh results…" : ""}
          </p>
        </>
      )}
    </div>
  );
}
