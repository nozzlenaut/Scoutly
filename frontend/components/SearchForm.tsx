"use client";

/* eslint-disable react-hooks/set-state-in-effect -- Search state intentionally follows browser preferences and debounced catalog requests. */

import { useEffect, useId, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { suggestProducts, type ProductMatch } from "@/lib/api";
import { getCategory, searchCategories } from "@/lib/categoryCatalog";
import { commitDeliveryZip, currentDeliveryZip } from "@/lib/ephemeralDelivery";
import { StatusBadge } from "@/components/StatusBadge";
import { BookIsbnScanner } from "@/components/BookIsbnScanner";
import { SpecSearchBuilder } from "@/components/SpecSearchBuilder";
import { CpuSearchBuilder } from "@/components/CpuSearchBuilder";

type SearchFormProps = {
  initialCategoryId?: string | null;
  initialQuery?: string | null;
  initialUsOnly?: boolean | null;
  compact?: boolean;
  bare?: boolean;
  theme?: "dark" | "light";
};

function announceSearchStart() {
  window.dispatchEvent(new CustomEvent("pricesift:search-start"));
}

export function SearchForm({
  initialCategoryId,
  initialQuery,
  initialUsOnly,
  compact = false,
  bare = false,
  theme = "dark",
}: SearchFormProps) {
  const router = useRouter();
  const initialCategory = getCategory(initialCategoryId);
  const [categoryId, setCategoryId] = useState(initialCategory.id);
  const selectedCategory = getCategory(categoryId);
  const [query, setQuery] = useState(
    initialQuery === undefined || initialQuery === null
      ? ""
      : initialQuery.trim(),
  );
  const [suggestions, setSuggestions] = useState<ProductMatch[]>([]);
  const [usOnly, setUsOnly] = useState(Boolean(initialUsOnly));
  const [deliveryPostalCode, setDeliveryPostalCode] = useState("");
  const [deliveryPostalError, setDeliveryPostalError] = useState<string | null>(null);
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
  const deliveryPostalId = useId();

  useEffect(() => {
    const current = currentDeliveryZip();
    if (current) setDeliveryPostalCode(current);
  }, []);

  useEffect(() => {
    if (initialUsOnly !== undefined && initialUsOnly !== null) {
      setUsOnly(Boolean(initialUsOnly));
      return;
    }
    try {
      setUsOnly(window.localStorage.getItem("pricesift:us-only") === "true");
    } catch {
      // Local storage may be unavailable in privacy modes. The toggle still works for this page.
    }
  }, [initialUsOnly]);

  function changeUsOnly(next: boolean) {
    setUsOnly(next);
    setDeliveryPostalError(null);
    if (!next) {
      setDeliveryPostalCode("");
      commitDeliveryZip("");
    }
    try {
      window.localStorage.setItem("pricesift:us-only", String(next));
    } catch {
      // Keep the in-memory preference even when storage is blocked.
    }
  }

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

    if (categoryId === "ram" || categoryId === "cpus" || categoryId === "books") {
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
    const currentDestination = `${window.location.pathname}${window.location.search}`;
    if (currentDestination === destination) return;
    setIsNavigating(true);
    announceSearchStart();
    router.push(destination);
  }

  function submitSearch(value = query) {
    const cleaned = value.trim();
    if (!cleaned) return;

    const cleanedPostalCode = usOnly ? deliveryPostalCode.trim() : "";
    if (cleanedPostalCode && !/^\d{5}(?:-\d{4})?$/.test(cleanedPostalCode)) {
      setDeliveryPostalError("Enter a five-digit US ZIP code.");
      return;
    }
    setDeliveryPostalError(null);
    commitDeliveryZip(cleanedPostalCode);

    const params = new URLSearchParams({ category: categoryId, q: cleaned });
    if (usOnly) params.set("us_only", "1");
    navigate(`/search?${params.toString()}`);
  }

  function handleCategoryChange(nextCategoryId: string) {
    if (nextCategoryId === categoryId) return;

    if (nextCategoryId === "lenses") {
      navigate("/lenses");
      return;
    }

    if (compact) {
      // A results page must never show cards from one category while another
      // category is selected. Start a clean category page immediately.
      const params = new URLSearchParams({ category: nextCategoryId, q: "" });
      if (usOnly) params.set("us_only", "1");
      navigate(`/search?${params.toString()}`);
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

  const searchLabelClasses =
    theme === "light" ? "sr-only text-ps-text-secondary" : "sr-only";
  const searchInputClasses =
    theme === "light"
      ? "min-h-14 w-full rounded-2xl border border-ps-border bg-ps-control px-5 text-base text-ps-text-primary outline-none placeholder:text-ps-text-muted focus:border-ps-accent-strong focus:ring-2 focus:ring-ps-accent focus:ring-offset-2 focus:ring-offset-ps-surface"
      : "min-h-14 w-full rounded-2xl border border-white/10 bg-white/10 px-5 text-base text-white outline-none placeholder:text-slate-400 focus:border-cyan-300";
  const suggestionPanelClasses =
    theme === "light"
      ? "absolute left-0 right-0 top-16 z-[100] max-h-80 overflow-y-auto rounded-2xl border border-ps-border bg-ps-surface text-left shadow-2xl shadow-slate-900/10 backdrop-blur"
      : "absolute left-0 right-0 top-16 z-[100] max-h-80 overflow-y-auto rounded-2xl border border-white/10 bg-slate-950/95 text-left shadow-2xl shadow-black/50 backdrop-blur";
  const suggestionLabelClasses =
    theme === "light"
      ? "border-b border-ps-border px-4 py-2 text-xs uppercase tracking-[0.2em] text-ps-neutral"
      : "border-b border-white/10 px-4 py-2 text-xs uppercase tracking-[0.2em] text-slate-400";
  const suggestionRowClasses = (selected: boolean) =>
    `flex w-full items-center justify-between gap-4 px-4 py-3 text-left transition ${
      theme === "light"
        ? selected
          ? "bg-ps-accent-soft"
          : "hover:bg-ps-accent-soft"
        : selected
          ? "bg-white/10"
          : "hover:bg-white/10"
    }`;
  const suggestionPrimaryTextClasses =
    theme === "light" ? "block font-semibold text-ps-text-primary" : "block font-semibold text-white";
  const suggestionSecondaryTextClasses =
    theme === "light" ? "text-xs text-ps-text-secondary" : "text-xs text-slate-300";
  const suggestionMatchClasses =
    theme === "light"
      ? "rounded-full border border-ps-border-strong bg-ps-accent-soft px-2 py-1 text-xs font-medium text-ps-info"
      : "rounded-full border border-cyan-300/20 bg-cyan-300/10 px-2 py-1 text-xs font-medium text-cyan-100";
  const searchButtonClasses =
    theme === "light"
      ? "flex min-h-14 w-full items-center justify-center gap-3 rounded-2xl bg-ps-accent-strong px-7 font-semibold text-white transition hover:bg-ps-accent-hover focus:ring-2 focus:ring-ps-accent focus:ring-offset-2 focus:ring-offset-ps-canvas disabled:cursor-wait disabled:opacity-80 sm:w-auto"
      : "flex min-h-14 items-center justify-center gap-3 rounded-2xl bg-cyan-300 px-7 font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-wait disabled:opacity-80";
  const categoryListClasses =
    theme === "light" ? "grid grid-cols-2 gap-2 sm:flex sm:flex-wrap" : "flex flex-wrap gap-2";
  const helpTextClasses =
    theme === "light" ? "mt-3 text-sm text-ps-text-secondary" : "mt-3 text-sm text-slate-300";

  return (
    <div
      ref={wrapperRef}
      onBlur={(event) => {
        if (!wrapperRef.current?.contains(event.relatedTarget as Node | null)) {
          setShowSuggestions(false);
          setActiveSuggestionIndex(-1);
        }
      }}
      className={
        bare
          ? "relative z-50 mx-auto w-full max-w-4xl text-left"
          : theme === "light"
            ? `relative z-50 mx-auto w-full rounded-[2rem] border border-ps-border bg-ps-surface text-left shadow-xl shadow-slate-900/10 ${
                compact ? "max-w-6xl p-3 sm:p-4" : "max-w-3xl p-4 sm:p-5"
              }`
            : `relative z-50 mx-auto w-full rounded-[2rem] border border-white/10 bg-slate-950/35 text-left shadow-2xl shadow-black/30 backdrop-blur ${
                compact ? "max-w-6xl p-3 sm:p-4" : "max-w-3xl p-4 sm:p-5"
              }`
      }
    >
      <div className={compact ? "mb-3" : "mb-4"}>
        <p
          className={`mb-2 text-xs uppercase tracking-[0.22em] ${
            theme === "light" ? "text-ps-neutral" : "text-slate-400"
          }`}
        >
          Choose a category
        </p>
        <div
          className={categoryListClasses}
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
                className={`flex items-center justify-center gap-2 rounded-2xl border px-4 py-3 text-sm font-semibold transition disabled:cursor-wait disabled:opacity-70 ${
                  theme === "light" ? "min-h-11 w-full whitespace-nowrap sm:w-auto" : ""
                } ${
                  isSelected
                    ? theme === "light"
                      ? "border-ps-accent-strong bg-ps-accent-soft text-ps-text-primary"
                      : "border-white bg-white text-slate-950"
                    : theme === "light"
                      ? "border-ps-border bg-ps-surface text-ps-text-secondary hover:border-ps-border-strong hover:bg-ps-accent-soft"
                      : "border-white/10 bg-white/[0.04] text-slate-200 hover:bg-white/[0.08]"
                }`}
              >
                <span>{category.label}</span>
                {theme === "light" ? (
                  category.status === "beta" ? (
                    <span className="shrink-0 text-[10px] font-bold uppercase tracking-[0.12em] text-ps-info">
                      Beta
                    </span>
                  ) : null
                ) : (
                  <StatusBadge status={category.status} selected={isSelected} />
                )}
              </button>
            );
          })}
        </div>
        {!compact && theme !== "light" ? (
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
          theme={theme}
        />
      ) : selectedCategory.id === "cpus" ? (
        <CpuSearchBuilder
          key={`cpu-builder:${initialQuery || "new"}`}
          initialQuery={initialQuery}
          compact={compact}
          isNavigating={isNavigating}
          onSearch={submitSearch}
          theme={theme}
        />
      ) : (
        <>
          <form
            onSubmit={handleSubmit}
            className="relative w-full"
          >
            <div className="flex w-full flex-col gap-3 sm:flex-row">
              <div className="relative flex-1">
              <label htmlFor={inputId} className={searchLabelClasses}>
                {selectedCategory.id === "books"
                  ? "Search by ISBN-10 or ISBN-13"
                  : `Search exact ${selectedCategory.label.toLowerCase()} item`}
              </label>
              <input
                id={inputId}
                ref={inputRef}
                value={query}
                inputMode={selectedCategory.id === "books" ? "text" : undefined}
                autoComplete="off"
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
                role={selectedCategory.id === "books" ? undefined : "combobox"}
                aria-autocomplete={selectedCategory.id === "books" ? undefined : "list"}
                aria-expanded={selectedCategory.id === "books" ? undefined : showSuggestions}
                aria-controls={selectedCategory.id !== "books" && showSuggestions ? listboxId : undefined}
                aria-activedescendant={
                  selectedCategory.id !== "books" && showSuggestions && activeSuggestionIndex >= 0
                    ? `${listboxId}-option-${activeSuggestionIndex}`
                    : undefined
                }
                aria-describedby={statusId}
                className={searchInputClasses}
              />

              {showSuggestions && suggestions.length > 0 ? (
                <div
                  id={listboxId}
                  role="listbox"
                  aria-label={`Matching ${selectedCategory.label}`}
                  className={suggestionPanelClasses}
                >
                  <div className={suggestionLabelClasses}>
                    Searchable models for {selectedCategory.label.toLowerCase()}
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
                        className={suggestionRowClasses(selected)}
                      >
                        <span>
                          <span className={suggestionPrimaryTextClasses}>
                            {match.product.display_name}
                          </span>
                          <span className={suggestionSecondaryTextClasses}>
                            {match.product.metadata?.provider_scope === "keh"
                              ? "Current KEH model · KEH only"
                              : match.product.metadata?.provider_scope === "ebay_keh"
                                ? "PriceSift catalog item · eBay + KEH"
                                : `Exact catalog item · ${match.product.product_type.replace("_", " ")}`}
                          </span>
                        </span>
                        <span className={suggestionMatchClasses}>
                          Product match {Math.round(match.confidence * 100)}%
                        </span>
                      </button>
                    );
                  })}
                </div>
              ) : null}
              </div>

              <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
                <button
                  disabled={isNavigating}
                  className={searchButtonClasses}
                >
                  {isNavigating ? (
                    <>
                      <span className={theme === "light" ? "h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" : "h-4 w-4 animate-spin rounded-full border-2 border-slate-950/20 border-t-slate-950"} />
                      Searching…
                    </>
                  ) : (
                    "Search"
                  )}
                </button>
                <UsOnlyToggle checked={usOnly} onChange={changeUsOnly} theme={theme} />
              </div>
            </div>

            {usOnly ? (
              <DeliveryPostalField
                inputId={deliveryPostalId}
                value={deliveryPostalCode}
                error={deliveryPostalError}
                theme={theme}
                onChange={(value) => {
                  setDeliveryPostalCode(value);
                  setDeliveryPostalError(null);
                }}
              />
            ) : null}
          </form>

          {selectedCategory.id === "books" ? <BookIsbnScanner usOnly={usOnly} theme={theme} /> : null}

          <p
            id={statusId}
            aria-live="polite"
            className={helpTextClasses}
          >
            {selectedCategory.id === "books"
              ? "Enter an ISBN-10 or ISBN-13. PriceSift searches that exact used-book edition; title-only searches are not sent to eBay."
              : selectedCategory.id === "cameras"
                ? "Pick a PriceSift catalog camera for eBay + KEH, or a current KEH model for KEH-only results. Unsupported text is never sent to eBay."
                : "Type or pick a supported catalog item. Unsupported text will not be sent to the marketplace."}
            {isLoading ? " Checking catalog…" : ""}
            {usOnly ? " Filtering eBay to US-located items; KEH results are unchanged." : ""}
            {isNavigating ? " Loading fresh results…" : ""}
          </p>
          {selectedCategory.id === "cameras" ? (
            <p className={theme === "light" ? "mt-2 text-xs text-ps-neutral" : "mt-2 text-xs text-slate-400"}>
              <Link
                href="/cameras"
                className={
                  theme === "light"
                    ? "font-semibold text-ps-accent-hover hover:text-ps-accent-strong"
                    : "font-semibold text-cyan-200 hover:text-cyan-100"
                }
              >
                Browse every camera model currently available at KEH
              </Link>
            </p>
          ) : null}
        </>
      )}

      {selectedCategory.id === "ram" || selectedCategory.id === "cpus" ? (
        <div className="mt-4">
          <div className="flex justify-end">
            <UsOnlyToggle checked={usOnly} onChange={changeUsOnly} theme={theme} />
          </div>
          {usOnly ? (
            <DeliveryPostalField
              inputId={deliveryPostalId}
              value={deliveryPostalCode}
              error={deliveryPostalError}
              theme={theme}
              onChange={(value) => {
                setDeliveryPostalCode(value);
                setDeliveryPostalError(null);
              }}
            />
          ) : null}
        </div>
      ) : null}
    </div>
  );
}

function DeliveryPostalField({
  inputId,
  value,
  error,
  onChange,
  theme = "dark",
}: {
  inputId: string;
  value: string;
  error: string | null;
  onChange: (value: string) => void;
  theme?: "dark" | "light";
}) {
  return (
    <div className={theme === "light" ? "mt-3 flex flex-col gap-2 border-t border-ps-border pt-3 sm:flex-row sm:items-end sm:gap-4" : "mt-3 flex flex-col gap-2 border-t border-white/10 pt-3 sm:flex-row sm:items-end sm:gap-4"}>
      <label htmlFor={inputId} className="block w-full sm:w-48">
        <span className={theme === "light" ? "mb-1 block text-xs font-bold uppercase tracking-[0.16em] text-ps-text-secondary" : "mb-1 block text-xs font-bold uppercase tracking-[0.16em] text-cyan-100"}>
          Delivery ZIP (optional)
        </span>
        <input
          id={inputId}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          inputMode="numeric"
          autoComplete="off"
          maxLength={10}
          placeholder="48035"
          aria-invalid={Boolean(error)}
          className={theme === "light" ? "min-h-11 w-full rounded-xl border border-ps-border bg-ps-control px-4 text-ps-text-primary outline-none placeholder:text-ps-text-muted focus:border-ps-accent-strong focus:ring-2 focus:ring-ps-accent" : "min-h-11 w-full rounded-xl border border-white/10 bg-white/10 px-4 text-white outline-none placeholder:text-slate-500 focus:border-cyan-300"}
        />
      </label>
      <p className={`flex-1 text-xs leading-5 ${error ? (theme === "light" ? "text-ps-warning" : "text-amber-200") : (theme === "light" ? "text-ps-text-secondary" : "text-slate-400")}`} role={error ? "alert" : undefined}>
        {error || "Delivery details will appear inside each eBay result. PriceSift does not save your ZIP."}
      </p>
    </div>
  );
}

function UsOnlyToggle({
  checked,
  onChange,
  theme = "dark",
}: {
  checked: boolean;
  onChange: (checked: boolean) => void;
  theme?: "dark" | "light";
}) {
  return (
    <label
      className={
        theme === "light"
          ? "flex min-h-12 w-full cursor-pointer items-center justify-center gap-3 rounded-2xl border border-ps-border bg-ps-control px-4 text-sm font-semibold text-ps-text-primary transition hover:border-ps-border-strong hover:bg-ps-accent-soft sm:w-auto"
          : "flex min-h-12 cursor-pointer items-center gap-3 rounded-2xl border border-white/10 bg-white/[0.05] px-4 text-sm font-semibold text-slate-200 transition hover:bg-white/[0.08]"
      }
    >
      <input
        type="checkbox"
        checked={checked}
        onChange={(event) => onChange(event.target.checked)}
        className={theme === "light" ? "h-4 w-4 accent-ps-accent-strong" : "h-4 w-4 accent-cyan-300"}
      />
      <span>US listings only</span>
    </label>
  );
}
