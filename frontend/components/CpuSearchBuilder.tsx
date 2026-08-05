"use client";

import { useMemo, useState } from "react";
import {
  buildCpuQuery,
  cpuGenerationOptions,
  cpuManufacturers,
  cpuModelOptions,
  cpuSelectionIsComplete,
  cpuSocketOptions,
  parseCpuQuery,
  type CpuBuilderSelection,
  type SpecOption,
} from "@/lib/specBuilders";

type Props = {
  initialQuery?: string | null;
  compact?: boolean;
  isNavigating?: boolean;
  onSearch: (query: string) => void;
  theme?: "dark" | "light";
};

type ChoiceFieldProps = {
  label: string;
  step: number;
  value: string;
  options: SpecOption[];
  disabled?: boolean;
  onChange: (value: string) => void;
  theme?: "dark" | "light";
};

function ChoiceField({ label, step, value, options, disabled = false, onChange, theme = "dark" }: ChoiceFieldProps) {
  return (
    <fieldset disabled={disabled} className="min-w-0">
      <legend className={`mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.17em] ${theme === "light" ? "text-ps-text-secondary" : "text-slate-300"}`}>
        <span className={`flex h-6 w-6 items-center justify-center rounded-full border text-[11px] ${theme === "light" ? "border-ps-border bg-ps-control text-ps-accent-hover" : "border-cyan-300/30 bg-cyan-300/10 text-cyan-100"}`}>
          {step}
        </span>
        {label}
      </legend>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => {
          const selected = value === option.id;
          return (
            <button
              key={`${label}-${option.id}`}
              type="button"
              aria-pressed={selected}
              onClick={() => onChange(option.id)}
              className={`rounded-xl border px-3 py-2 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-35 ${theme === "light" ? "focus:border-ps-accent-strong focus:ring-2 focus:ring-ps-accent-strong" : ""} ${
                selected
                  ? theme === "light"
                    ? "border-ps-accent-strong bg-ps-control text-ps-text-primary"
                    : "border-cyan-200 bg-cyan-200 text-slate-950"
                  : theme === "light"
                    ? "border-ps-border bg-ps-surface text-ps-text-secondary hover:border-ps-border-strong hover:bg-ps-control"
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

export function CpuSearchBuilder({ initialQuery, compact = false, isNavigating = false, onSearch, theme = "dark" }: Props) {
  const [selection, setSelection] = useState<CpuBuilderSelection>(() => parseCpuQuery(initialQuery));
  const sockets = useMemo(() => cpuSocketOptions(selection), [selection]);
  const generations = useMemo(() => cpuGenerationOptions(selection), [selection]);
  const models = useMemo(() => cpuModelOptions(selection), [selection]);
  const query = buildCpuQuery(selection);

  return (
    <div className={compact ? "mt-2" : "mt-1"}>
      <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className={theme === "light" ? "text-xs uppercase tracking-[0.22em] text-ps-accent-hover" : "text-xs uppercase tracking-[0.22em] text-cyan-200"}>Build your CPU search</p>
          <p className={theme === "light" ? "mt-2 max-w-3xl text-sm leading-6 text-ps-text-secondary" : "mt-2 max-w-3xl text-sm leading-6 text-slate-300"}>
            Consumer desktop CPUs only. Choose an exact model; suffixes such as K, KF, F, G, and X3D remain separate because they change the chip.
          </p>
        </div>
        <span className={theme === "light" ? "w-fit rounded-full border border-ps-border bg-ps-surface px-3 py-1 text-xs font-semibold text-ps-success" : "w-fit rounded-full border border-emerald-300/25 bg-emerald-300/10 px-3 py-1 text-xs font-semibold text-emerald-100"}>
          CPUs Active
        </span>
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <ChoiceField
          label="Manufacturer"
          step={1}
          value={selection.manufacturer}
          options={cpuManufacturers}
          onChange={(value) =>
            setSelection({ manufacturer: value as CpuBuilderSelection["manufacturer"], socket: "", generation: "", model: "" })
          }
          theme={theme}
        />
        <ChoiceField
          label="Socket"
          step={2}
          value={selection.socket}
          options={sockets}
          disabled={!selection.manufacturer}
          onChange={(value) => setSelection((current) => ({ ...current, socket: value, generation: "", model: "" }))}
          theme={theme}
        />
        <ChoiceField
          label="Generation / series"
          step={3}
          value={selection.generation}
          options={generations}
          disabled={!selection.socket}
          onChange={(value) => setSelection((current) => ({ ...current, generation: value, model: "" }))}
          theme={theme}
        />
      </div>

      {selection.generation ? (
        <div className={theme === "light" ? "mt-6 rounded-2xl border border-ps-border bg-ps-surface p-4" : "mt-6 rounded-2xl border border-white/10 bg-slate-950/35 p-4"}>
          <ChoiceField
            label="Exact model"
            step={4}
            value={selection.model}
            options={models}
            onChange={(value) => setSelection((current) => ({ ...current, model: value }))}
            theme={theme}
          />
          <p className={theme === "light" ? "mt-4 text-xs leading-5 text-ps-neutral" : "mt-4 text-xs leading-5 text-slate-500"}>
            CPU-only, OEM/tray, and boxed chips are valid. Motherboard bundles, coolers-only, engineering samples, damaged chips, lots, and full computers are filtered.
          </p>
        </div>
      ) : null}

      <div className={theme === "light" ? "mt-6 flex flex-col gap-3 rounded-2xl border border-ps-border bg-ps-surface p-4 sm:flex-row sm:items-center sm:justify-between" : "mt-6 flex flex-col gap-3 rounded-2xl border border-white/10 bg-white/[0.04] p-4 sm:flex-row sm:items-center sm:justify-between"}>
        <div>
          <p className={theme === "light" ? "text-xs uppercase tracking-[0.16em] text-ps-neutral" : "text-xs uppercase tracking-[0.16em] text-slate-400"}>Structured search</p>
          <p className={theme === "light" ? "mt-1 font-semibold text-ps-text-primary" : "mt-1 font-semibold text-white"}>{query || "Choose manufacturer, socket, generation, and exact model"}</p>
        </div>
        <button
          type="button"
          disabled={!cpuSelectionIsComplete(selection) || isNavigating || !query}
          onClick={() => query && onSearch(query)}
          className={theme === "light" ? "flex min-h-12 items-center justify-center gap-3 rounded-2xl bg-ps-accent-strong px-6 font-semibold text-white transition hover:bg-ps-accent-hover focus:ring-2 focus:ring-ps-accent-strong disabled:cursor-not-allowed disabled:opacity-40" : "flex min-h-12 items-center justify-center gap-3 rounded-2xl bg-cyan-300 px-6 font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-40"}
        >
          {isNavigating ? (
            <>
              <span className={theme === "light" ? "h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" : "h-4 w-4 animate-spin rounded-full border-2 border-slate-950/20 border-t-slate-950"} />
              Searching…
            </>
          ) : (
            "Search CPUs"
          )}
        </button>
      </div>
    </div>
  );
}
