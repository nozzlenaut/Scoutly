"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { collectQaPriceBatch, type PriceCollectionResponse } from "@/lib/api";

const categories = [
  ["", "All categories"],
  ["cameras", "Cameras"],
  ["gpus", "GPUs"],
  ["ram", "RAM"],
  ["cpus", "CPUs"],
  ["consoles", "Consoles"],
  ["lego", "LEGO"],
] as const;

export function PriceCollector({ token }: { token: string }) {
  const router = useRouter();
  const [category, setCategory] = useState("");
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<PriceCollectionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function collect() {
    setRunning(true);
    setError(null);
    try {
      const response = await collectQaPriceBatch(token, { limit: 5, category: category || undefined });
      setResult(response);
      router.refresh();
    } catch {
      setError("The collection batch could not be completed.");
    } finally {
      setRunning(false);
    }
  }

  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.05] p-5">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h2 className="text-2xl font-bold">Collect QA price snapshots</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
            Normal buyer searches and QA runs save snapshots automatically. This collector rotates through the least-recently observed QA products in small API-friendly batches.
          </p>
        </div>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <label className="text-sm text-slate-300">
            <span className="mb-1 block text-xs uppercase tracking-[0.16em] text-slate-500">Category</span>
            <select
              value={category}
              onChange={(event) => setCategory(event.target.value)}
              className="rounded-2xl border border-white/10 bg-slate-900 px-4 py-3 text-white"
            >
              {categories.map(([value, label]) => <option key={value || "all"} value={value}>{label}</option>)}
            </select>
          </label>
          <button
            type="button"
            onClick={collect}
            disabled={running}
            className="rounded-2xl bg-cyan-200 px-5 py-3 font-bold text-slate-950 transition hover:bg-cyan-100 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {running ? "Collecting…" : "Collect next 5"}
          </button>
        </div>
      </div>

      {result ? (
        <div className="mt-4 rounded-2xl border border-emerald-300/20 bg-emerald-300/10 p-4 text-sm text-emerald-100">
          Collected {result.collected_count} products. {result.live_ebay ? "Live eBay observations were saved." : "Live eBay credentials were not detected, so mock results were not persisted."}
        </div>
      ) : null}
      {error ? <div className="mt-4 rounded-2xl border border-rose-300/20 bg-rose-300/10 p-4 text-sm text-rose-100">{error}</div> : null}
    </section>
  );
}
