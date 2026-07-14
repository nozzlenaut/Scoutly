"use client";

import { useMemo, useState } from "react";
import {
  buildRamQuery,
  parseRamQuery,
  ramBrands,
  ramCapacityOptions,
  ramConfigurationOptions,
  ramFormFactors,
  ramGenerations,
  ramSelectionIsComplete,
  ramSpeedOptions,
  type RamBuilderSelection,
  type SpecOption,
} from "@/lib/specBuilders";

type Props = {
  initialQuery?: string | null;
  compact?: boolean;
  isNavigating?: boolean;
  onSearch: (query: string) => void;
};

type FieldProps = {
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
}: FieldProps) {
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

export function SpecSearchBuilder({
  initialQuery,
  compact = false,
  isNavigating = false,
  onSearch,
}: Props) {
  const [selection, setSelection] = useState<RamBuilderSelection>(() =>
    parseRamQuery(initialQuery),
  );

  const capacities = useMemo(() => ramCapacityOptions(selection), [selection]);
  const configurations = useMemo(
    () => ramConfigurationOptions(selection),
    [selection],
  );
  const speeds = useMemo(() => ramSpeedOptions(selection), [selection]);
  const query = buildRamQuery(selection);

  function changeFormFactor(value: string) {
    setSelection({
      formFactor: value as RamBuilderSelection["formFactor"],
      generation: "",
      totalCapacity: "",
      configuration: "",
      speed: "",
      brand: "",
    });
  }

  function changeGeneration(value: string) {
    setSelection((current) => ({
      ...current,
      generation: value as RamBuilderSelection["generation"],
      totalCapacity: "",
      configuration: "",
      speed: "",
    }));
  }

  function changeCapacity(value: string) {
    setSelection((current) => ({
      ...current,
      totalCapacity: value,
      configuration: "",
    }));
  }

  return (
    <div className={compact ? "mt-2" : "mt-1"}>
      <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.22em] text-cyan-200">
            Build your RAM search
          </p>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
            Required choices use strict matching. PriceSift rejects unclear
            stick counts, conflicting DDR types, laptop/desktop mismatches,
            ECC/server RAM, and seller variation listings.
          </p>
        </div>
        <span className="w-fit rounded-full border border-cyan-300/25 bg-cyan-300/10 px-3 py-1 text-xs font-semibold text-cyan-100">
          RAM Lab
        </span>
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <ChoiceField
          label="Desktop or laptop"
          step={1}
          value={selection.formFactor}
          options={ramFormFactors}
          onChange={changeFormFactor}
        />
        <ChoiceField
          label="DDR generation"
          step={2}
          value={selection.generation}
          options={ramGenerations}
          disabled={!selection.formFactor}
          onChange={changeGeneration}
        />
        <ChoiceField
          label="Total capacity"
          step={3}
          value={selection.totalCapacity}
          options={capacities}
          disabled={!selection.generation}
          onChange={changeCapacity}
        />
        <ChoiceField
          label="Stick configuration"
          step={4}
          value={selection.configuration}
          options={configurations}
          disabled={!selection.totalCapacity}
          onChange={(value) =>
            setSelection((current) => ({ ...current, configuration: value }))
          }
        />
      </div>

      {selection.configuration ? (
        <div className="mt-6 rounded-2xl border border-white/10 bg-slate-950/35 p-4">
          <p className="mb-4 text-xs font-semibold uppercase tracking-[0.18em] text-slate-300">
            Optional refinements
          </p>
          <div className="grid gap-5 lg:grid-cols-2">
            <ChoiceField
              label="Speed"
              step={5}
              value={selection.speed}
              options={speeds}
              onChange={(value) =>
                setSelection((current) => ({ ...current, speed: value }))
              }
            />
            <ChoiceField
              label="Brand"
              step={6}
              value={selection.brand}
              options={ramBrands}
              onChange={(value) =>
                setSelection((current) => ({ ...current, brand: value }))
              }
            />
          </div>
        </div>
      ) : null}

      <div className="mt-6 flex flex-col gap-3 rounded-2xl border border-white/10 bg-white/[0.04] p-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.16em] text-slate-400">
            Structured search
          </p>
          <p className="mt-1 font-semibold text-white">
            {query || "Complete the first four choices"}
          </p>
        </div>
        <button
          type="button"
          disabled={
            !ramSelectionIsComplete(selection) || isNavigating || !query
          }
          onClick={() => query && onSearch(query)}
          className="flex min-h-12 items-center justify-center gap-3 rounded-2xl bg-cyan-300 px-6 font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {isNavigating ? (
            <>
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-950/20 border-t-slate-950" />
              Searching…
            </>
          ) : (
            "Search RAM"
          )}
        </button>
      </div>
    </div>
  );
}
