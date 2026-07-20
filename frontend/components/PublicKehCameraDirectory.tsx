"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import type { KehCameraCatalogResponse } from "@/lib/api";

function money(value?: number | null, currency = "USD"): string {
  if (value === null || value === undefined) return "Price unavailable";
  return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(value);
}

export function PublicKehCameraDirectory({ data }: { data: KehCameraCatalogResponse }) {
  const [query, setQuery] = useState("");
  const [scope, setScope] = useState<"all" | "ebay_keh" | "keh">("all");
  const visibleModels = useMemo(() => {
    const cleaned = query.trim().toLowerCase();
    return data.models.filter((model) => {
      if (scope !== "all" && model.provider_scope !== scope) return false;
      if (!cleaned) return true;
      return `${model.brand} ${model.model_name}`.toLowerCase().includes(cleaned);
    });
  }, [data.models, query, scope]);

  return (
    <>
      <section className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-3xl border border-white/10 bg-white/[0.05] p-5">
          <p className="text-sm text-slate-400">Current camera models</p>
          <p className="mt-2 text-3xl font-black">{data.summary.model_count}</p>
        </div>
        <div className="rounded-3xl border border-white/10 bg-white/[0.05] p-5">
          <p className="text-sm text-slate-400">KEH listings</p>
          <p className="mt-2 text-3xl font-black">{data.summary.listing_count}</p>
        </div>
        <div className="rounded-3xl border border-white/10 bg-white/[0.05] p-5">
          <p className="text-sm text-slate-400">eBay + KEH models</p>
          <p className="mt-2 text-3xl font-black">{data.summary.catalog_model_count}</p>
        </div>
        <div className="rounded-3xl border border-white/10 bg-white/[0.05] p-5">
          <p className="text-sm text-slate-400">KEH-only models</p>
          <p className="mt-2 text-3xl font-black">{data.summary.keh_only_model_count}</p>
        </div>
      </section>

      <section className="mt-8 rounded-3xl border border-white/10 bg-white/[0.04] p-5">
        <div className="grid gap-4 lg:grid-cols-[1fr_auto] lg:items-end">
          <label>
            <span className="mb-2 block text-xs font-bold uppercase tracking-[0.18em] text-slate-400">
              Find a current KEH camera model
            </span>
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Sony A7 III, Nikon Z5, Fujifilm X-T…"
              className="min-h-14 w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 text-white outline-none placeholder:text-slate-500 focus:border-cyan-300"
            />
          </label>
          <div className="flex flex-wrap gap-2" role="group" aria-label="Provider coverage">
            {[
              ["all", "All models"],
              ["ebay_keh", "eBay + KEH"],
              ["keh", "KEH only"],
            ].map(([value, label]) => (
              <button
                key={value}
                type="button"
                onClick={() => setScope(value as typeof scope)}
                className={`min-h-11 rounded-xl border px-4 text-sm font-semibold ${
                  scope === value
                    ? "border-cyan-200 bg-cyan-200 text-slate-950"
                    : "border-white/10 bg-white/[0.05] text-slate-200"
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
        <p className="mt-3 text-sm text-slate-400">
          {visibleModels.length} matching models. PriceSift catalog matches can search eBay and KEH; newly discovered models stay KEH-only.
        </p>
      </section>

      {visibleModels.length ? (
        <section className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3" aria-label="Current KEH camera models">
          {visibleModels.map((model) => (
            <Link
              key={model.model_key}
              href={`/cameras/${model.slug}`}
              className="group rounded-3xl border border-white/10 bg-white/[0.04] p-5 transition hover:border-cyan-200/40 hover:bg-white/[0.07]"
            >
              <div className="flex gap-4">
                {model.image_url ? (
                  <img src={model.image_url} alt="" className="h-24 w-24 shrink-0 rounded-2xl bg-white object-contain p-1" />
                ) : (
                  <div className="flex h-24 w-24 shrink-0 items-center justify-center rounded-2xl bg-white/5 text-xs text-slate-500">No image</div>
                )}
                <div className="min-w-0">
                  <p className="text-xs font-bold uppercase tracking-[0.16em] text-slate-500">{model.brand}</p>
                  <h2 className="mt-1 font-bold text-white group-hover:text-cyan-100">{model.model_name}</h2>
                  <p className="mt-2 text-sm font-bold text-emerald-200">from {money(model.lowest_price, model.currency)}</p>
                </div>
              </div>
              <div className="mt-4 flex flex-wrap items-center justify-between gap-2 text-xs">
                <span className="rounded-full bg-white/10 px-3 py-1 text-slate-300">{model.listing_count} at KEH</span>
                <span className={`rounded-full px-3 py-1 font-bold ${model.provider_scope === "ebay_keh" ? "bg-cyan-200/15 text-cyan-100" : "bg-amber-200/15 text-amber-100"}`}>
                  {model.provider_scope === "ebay_keh" ? "eBay + KEH" : "KEH only"}
                </span>
              </div>
            </Link>
          ))}
        </section>
      ) : (
        <div className="mt-6 rounded-3xl border border-amber-300/20 bg-amber-300/10 p-6 text-amber-100">
          No current KEH camera models match those filters.
        </div>
      )}
    </>
  );
}
