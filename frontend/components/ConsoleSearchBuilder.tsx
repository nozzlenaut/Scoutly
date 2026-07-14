"use client";

import { useMemo, useState } from "react";
import {
  buildConsoleQuery,
  consoleBrands,
  consoleFamilyOptions,
  consoleModelOptions,
  consoleSelectionIsSearchable,
  parseConsoleQuery,
  type ConsoleBuilderSelection,
  type SpecOption,
} from "@/lib/specBuilders";

type Props = {
  initialQuery?: string | null;
  compact?: boolean;
  isNavigating?: boolean;
  onSearch: (query: string) => void;
};

type ChoiceFieldProps = {
  label: string;
  step: number;
  value: string;
  options: SpecOption[];
  disabled?: boolean;
  onChange: (value: string) => void;
};

function ChoiceField({
  label,
  step,
  value,
  options,
  disabled = false,
  onChange,
}: ChoiceFieldProps) {
  return (
    <fieldset disabled={disabled} className="min-w-0">
      <legend className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.17em] text-slate-300">
        <span className="flex h-6 w-6 items-center justify-center rounded-full border border-cyan-300/30 bg-cyan-300/10 text-[11px] text-cyan-100">
          {step}
        </span>
        {label}
      </legend>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => {
          const selected = value === option.id;
          return (
            <button
              key={`${label}-${option.id || "any"}`}
              type="button"
              aria-pressed={selected}
              onClick={() => onChange(option.id)}
              className={`rounded-xl border px-3 py-2 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-35 ${
                selected
                  ? "border-cyan-200 bg-cyan-200 text-slate-950"
                  : "border-white/10 bg-white/[0.05] text-slate-200 hover:bg-white/[0.1]"
              }`}
            >
              {option.label}
            </button>
          );
        })}
      </div>
    </fieldset>
  );
}

export function ConsoleSearchBuilder({
  initialQuery,
  compact = false,
  isNavigating = false,
  onSearch,
}: Props) {
  const [selection, setSelection] = useState<ConsoleBuilderSelection>(() =>
    parseConsoleQuery(initialQuery),
  );
  const families = useMemo(() => consoleFamilyOptions(selection), [selection]);
  const models = useMemo(() => consoleModelOptions(selection), [selection]);
  const query = buildConsoleQuery(selection);

  function searchNext(next: ConsoleBuilderSelection) {
    setSelection(next);
    const nextQuery = buildConsoleQuery(next);
    if (nextQuery) onSearch(nextQuery);
  }

  function changeBrand(value: string) {
    setSelection({
      brand: value as ConsoleBuilderSelection["brand"],
      family: "",
      model: "",
      storage: "",
      edition: "",
    });
  }

  function changeFamily(value: string) {
    searchNext({ ...selection, family: value, model: "", storage: "", edition: "" });
  }

  function changeModel(value: string) {
    searchNext({ ...selection, model: value, storage: "", edition: "" });
  }

  return (
    <div className={compact ? "mt-2" : "mt-1"}>
      <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.22em] text-cyan-200">
            Build your console search
          </p>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
            Pick the core console model you want. Storage, color, Disc/Digital,
            and bundle variants are grouped underneath that model for now.
          </p>
        </div>
        <span className="w-fit rounded-full border border-emerald-300/25 bg-emerald-300/10 px-3 py-1 text-xs font-semibold text-emerald-100">
          Consoles Active
        </span>
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <ChoiceField
          label="Brand"
          step={1}
          value={selection.brand}
          options={consoleBrands}
          onChange={changeBrand}
        />
        <ChoiceField
          label="Family / generation"
          step={2}
          value={selection.family}
          options={families}
          disabled={!selection.brand || isNavigating}
          onChange={changeFamily}
        />
      </div>

      {selection.family ? (
        <div className="mt-6 rounded-2xl border border-white/10 bg-slate-950/35 p-4">
          <p className="mb-4 text-xs font-semibold uppercase tracking-[0.18em] text-slate-300">
            Choose the core model
          </p>
          <ChoiceField
            label="Model"
            step={3}
            value={selection.model}
            options={models}
            disabled={isNavigating}
            onChange={changeModel}
          />
          <p className="mt-4 text-xs leading-5 text-slate-500">
            Variant narrowing is intentionally paused. A Series S search can include
            512GB and 1TB systems; a PS5 Slim search can include Disc and Digital systems.
          </p>
        </div>
      ) : null}

      <div className="mt-6 flex flex-col gap-3 rounded-2xl border border-white/10 bg-white/[0.04] p-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.16em] text-slate-400">
            Structured search
          </p>
          <p className="mt-1 font-semibold text-white">
            {query || "Choose a brand, family / generation, and model"}
          </p>
        </div>
        <button
          type="button"
          disabled={!consoleSelectionIsSearchable(selection) || isNavigating || !query}
          onClick={() => query && onSearch(query)}
          className="flex min-h-12 items-center justify-center gap-3 rounded-2xl bg-cyan-300 px-6 font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {isNavigating ? (
            <>
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-950/20 border-t-slate-950" />
              Updating…
            </>
          ) : (
            "Refresh console results"
          )}
        </button>
      </div>
    </div>
  );
}
