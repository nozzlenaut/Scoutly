"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import type { MarketIndexModel } from "@/lib/marketIndex";

type MarketIndexRow = MarketIndexModel & { href: string };
type SortKey = "product_label" | "category" | "latest_median_price" | "percent_change" | "history_days" | "snapshot_count";
type SortDirection = "asc" | "desc";

const categoryLabels: Record<string, string> = {
  cameras: "Cameras",
  consoles: "Consoles",
  gpus: "GPUs",
  cpus: "CPUs",
  lego: "LEGO",
};

function money(value: number | null): string {
  if (value === null) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

function signedPercent(value: number | null): string {
  if (value === null) return "—";
  if (Math.abs(value) < 0.05) return "0.0%";
  return `${value > 0 ? "+" : ""}${value.toFixed(1)}%`;
}

function directionClass(value: number | null): string {
  if (value === null) return "text-ps-neutral";
  if (value > 0.05) return "text-rose-700";
  if (value < -0.05) return "text-emerald-700";
  return "text-ps-text-secondary";
}

function sortValue(row: MarketIndexRow, key: SortKey): string | number | null {
  return row[key];
}

export function MarketIndexTable({ rows }: { rows: MarketIndexRow[] }) {
  const [sortKey, setSortKey] = useState<SortKey>("product_label");
  const [sortDirection, setSortDirection] = useState<SortDirection>("asc");
  const [category, setCategory] = useState("all");

  const categories = useMemo(
    () => Array.from(new Set(rows.map((row) => row.category))).sort(),
    [rows],
  );

  const visibleRows = useMemo(() => {
    const filtered = category === "all" ? rows : rows.filter((row) => row.category === category);
    return [...filtered].sort((left, right) => {
      const leftValue = sortValue(left, sortKey);
      const rightValue = sortValue(right, sortKey);
      if (leftValue === null && rightValue === null) {
        return left.product_label.localeCompare(right.product_label);
      }
      if (leftValue === null) return 1;
      if (rightValue === null) return -1;

      let comparison = 0;
      if (typeof leftValue === "number" && typeof rightValue === "number") {
        comparison = leftValue - rightValue;
      } else {
        comparison = String(leftValue).localeCompare(String(rightValue), undefined, { sensitivity: "base" });
      }
      if (comparison === 0) comparison = left.product_label.localeCompare(right.product_label);
      return sortDirection === "asc" ? comparison : -comparison;
    });
  }, [category, rows, sortDirection, sortKey]);

  function changeSort(nextKey: SortKey) {
    if (nextKey === sortKey) {
      setSortDirection((current) => (current === "asc" ? "desc" : "asc"));
      return;
    }
    setSortKey(nextKey);
    setSortDirection(nextKey === "product_label" || nextKey === "category" ? "asc" : "desc");
  }

  function header(label: string, key: SortKey) {
    const active = sortKey === key;
    return (
      <button
        type="button"
        onClick={() => changeSort(key)}
        className="inline-flex items-center gap-1 font-bold text-ps-text-primary hover:text-ps-accent-hover"
        aria-label={`Sort by ${label}${active ? `, currently ${sortDirection}ending` : ""}`}
      >
        {label}
        <span aria-hidden="true" className="text-xs text-ps-neutral">
          {active ? (sortDirection === "asc" ? "▲" : "▼") : "↕"}
        </span>
      </button>
    );
  }

  if (rows.length === 0) {
    return (
      <div className="mt-6 rounded-3xl border border-ps-border bg-ps-surface p-6 text-ps-text-secondary">
        Price history is still building. Models appear here after PriceSift stores usable marketplace observations.
      </div>
    );
  }

  return (
    <div className="mt-6">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-ps-text-secondary">
          {visibleRows.length} tracked model{visibleRows.length === 1 ? "" : "s"}. Tap any column heading to sort.
        </p>
        <label className="flex items-center gap-2 text-sm font-semibold text-ps-text-secondary">
          Category
          <select
            value={category}
            onChange={(event) => setCategory(event.target.value)}
            className="rounded-xl border border-ps-border bg-ps-surface px-3 py-2 text-ps-text-primary"
          >
            <option value="all">All</option>
            {categories.map((value) => (
              <option key={value} value={value}>{categoryLabels[value] || value}</option>
            ))}
          </select>
        </label>
      </div>

      <div className="overflow-x-auto rounded-3xl border border-ps-border bg-ps-surface">
        <table className="min-w-[960px] w-full border-collapse text-left text-sm">
          <thead className="bg-ps-accent-soft text-xs uppercase tracking-[0.12em] text-ps-neutral">
            <tr>
              <th className="px-5 py-4">{header("Model", "product_label")}</th>
              <th className="px-5 py-4">{header("Category", "category")}</th>
              <th className="px-5 py-4 text-right">{header("Current median", "latest_median_price")}</th>
              <th className="px-5 py-4 text-right">{header("Change", "percent_change")}</th>
              <th className="px-5 py-4 text-right">{header("History", "history_days")}</th>
              <th className="px-5 py-4 text-right">{header("Qualifying snapshots", "snapshot_count")}</th>
            </tr>
          </thead>
          <tbody>
            {visibleRows.map((row) => {
              const comparable = row.status === "comparable";
              return (
                <tr key={row.product_id} className="border-t border-ps-border align-middle">
                  <td className="px-5 py-4">
                    <Link href={row.href} className="font-bold text-ps-text-primary hover:text-ps-accent-hover hover:underline">
                      {row.product_label}
                    </Link>
                    {comparable ? (
                      <p className="mt-1 text-xs text-ps-neutral">Smoothed baseline {money(row.baseline_median_price)}</p>
                    ) : (
                      <p className="mt-1 max-w-sm text-xs leading-5 text-ps-neutral">
                        {row.status === "stale" ? "History is stale." : "Insufficient history."} {row.insufficient_reason || "More qualifying snapshots are needed."}
                      </p>
                    )}
                  </td>
                  <td className="px-5 py-4 text-ps-text-secondary">{categoryLabels[row.category] || row.category}</td>
                  <td className="px-5 py-4 text-right font-semibold text-ps-text-primary">
                    {comparable ? money(row.latest_median_price) : "Insufficient history"}
                  </td>
                  <td className={`px-5 py-4 text-right font-black ${directionClass(row.percent_change)}`}>
                    {signedPercent(row.percent_change)}
                  </td>
                  <td className="px-5 py-4 text-right text-ps-text-secondary">{row.history_days.toFixed(1)}d</td>
                  <td className="px-5 py-4 text-right text-ps-text-secondary">{row.snapshot_count}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="mt-3 text-xs leading-5 text-ps-neutral">
        A price increase is shown in red and a decrease in green from a buyer’s perspective. Models without five qualifying snapshots spanning at least 24 hours stay visible as insufficient history instead of publishing a shaky percentage move.
      </p>
    </div>
  );
}
