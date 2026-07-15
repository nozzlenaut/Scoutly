"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  getKehLensBuilder,
  type KehLensBuilderResponse,
  type KehLensFacet,
} from "@/lib/api";

function money(value?: number | null, currency = "USD"): string {
  if (value === null || value === undefined) return "—";
  try {
    return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(value);
  } catch {
    return `$${value.toFixed(2)}`;
  }
}

function FacetSelect({
  label,
  value,
  options,
  disabled,
  placeholder,
  onChange,
}: {
  label: string;
  value: string;
  options: KehLensFacet[];
  disabled?: boolean;
  placeholder: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="block">
      <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">{label}</span>
      <select
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
        className="min-h-12 w-full rounded-2xl border border-white/10 bg-slate-900 px-4 text-white outline-none focus:border-cyan-300 disabled:cursor-not-allowed disabled:opacity-40"
      >
        <option value="">{placeholder}</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label} ({option.count})
          </option>
        ))}
      </select>
    </label>
  );
}

export function AdminKehLensLab({
  initialData,
  token,
}: {
  initialData: KehLensBuilderResponse;
  token: string;
}) {
  const [data, setData] = useState(initialData);
  const [mount, setMount] = useState("");
  const [lensType, setLensType] = useState("");
  const [focalGroup, setFocalGroup] = useState("");
  const [brand, setBrand] = useState("");
  const [query, setQuery] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const requestRef = useRef(0);

  const filterSignature = useMemo(
    () => JSON.stringify({ mount, lensType, focalGroup, brand, query }),
    [mount, lensType, focalGroup, brand, query],
  );

  useEffect(() => {
    const requestNumber = requestRef.current + 1;
    requestRef.current = requestNumber;
    const timer = window.setTimeout(async () => {
      setBusy(true);
      setMessage(null);
      try {
        const next = await getKehLensBuilder(token, {
          mount: mount || undefined,
          lensType: lensType || undefined,
          focalGroup: focalGroup || undefined,
          brand: brand || undefined,
          query: query.trim() || undefined,
          limit: 150,
        });
        if (requestNumber === requestRef.current) setData(next);
      } catch (error) {
        if (requestNumber === requestRef.current) {
          setMessage(error instanceof Error ? error.message : "Could not load KEH lens inventory.");
        }
      } finally {
        if (requestNumber === requestRef.current) setBusy(false);
      }
    }, query ? 250 : 40);

    return () => window.clearTimeout(timer);
  }, [filterSignature, token, mount, lensType, focalGroup, brand, query]);

  function reset() {
    setMount("");
    setLensType("");
    setFocalGroup("");
    setBrand("");
    setQuery("");
  }

  const hasLensInventory = data.summary.listing_count > 0;

  return (
    <>
      <section className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5">
          <p className="text-sm text-slate-400">Available KEH lens listings</p>
          <p className="mt-2 text-3xl font-black">{data.summary.listing_count}</p>
        </div>
        <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5">
          <p className="text-sm text-slate-400">Unique model groups</p>
          <p className="mt-2 text-3xl font-black">{data.summary.model_count}</p>
        </div>
        <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5">
          <p className="text-sm text-slate-400">Filtered models</p>
          <p className="mt-2 text-3xl font-black">{data.summary.filtered_model_count}</p>
        </div>
        <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5">
          <p className="text-sm text-slate-400">Filtered listings</p>
          <p className="mt-2 text-3xl font-black">{data.summary.filtered_listing_count}</p>
        </div>
      </section>

      <section className="mt-8 rounded-3xl border border-white/10 bg-white/[0.04] p-5 sm:p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.22em] text-cyan-200">Builder test</p>
            <h2 className="mt-2 text-2xl font-bold">Narrow the current KEH lens feed</h2>
            <p className="mt-2 max-w-3xl text-sm text-slate-400">
              Mount/System → Prime/Zoom → Focal-length group → optional lens brand. The final list groups identical inventory and reveals the best three actual KEH listings.
            </p>
          </div>
          <button type="button" onClick={reset} className="rounded-2xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-white/[0.06]">
            Reset builder
          </button>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <FacetSelect
            label="1. Mount / system"
            value={mount}
            options={data.facets.mounts}
            placeholder="Choose a mount"
            onChange={(value) => {
              setMount(value);
              setLensType("");
              setFocalGroup("");
              setBrand("");
            }}
          />
          <FacetSelect
            label="2. Prime or zoom"
            value={lensType}
            options={data.facets.lens_types}
            disabled={!mount}
            placeholder="Choose a lens type"
            onChange={(value) => {
              setLensType(value);
              setFocalGroup("");
              setBrand("");
            }}
          />
          <FacetSelect
            label="3. Focal-length group"
            value={focalGroup}
            options={data.facets.focal_groups}
            disabled={!mount || !lensType}
            placeholder="Choose a focal group"
            onChange={(value) => {
              setFocalGroup(value);
              setBrand("");
            }}
          />
          <FacetSelect
            label="4. Lens brand (optional)"
            value={brand}
            options={data.facets.brands}
            disabled={!mount || !lensType || !focalGroup}
            placeholder="Any lens brand"
            onChange={setBrand}
          />
        </div>

        <label className="mt-5 block">
          <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Search the narrowed model list</span>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Try 24-70, 85mm, GM II, DG DN…"
            className="min-h-12 w-full rounded-2xl border border-white/10 bg-slate-900 px-4 text-white outline-none placeholder:text-slate-600 focus:border-cyan-300"
          />
        </label>

        {busy ? <p className="mt-4 text-sm text-cyan-200">Updating lens list…</p> : null}
        {message ? <p className="mt-4 rounded-2xl border border-rose-300/20 bg-rose-300/10 p-3 text-sm text-rose-100">{message}</p> : null}
        {!hasLensInventory ? (
          <p className="mt-5 rounded-2xl border border-amber-300/20 bg-amber-300/10 p-4 text-sm text-amber-100">
            No lens inventory is stored yet. Return to the KEH shadow page and run one fresh sync after deploying this update.
          </p>
        ) : null}
      </section>

      <section className="mt-8">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h2 className="text-2xl font-bold">Exact available lenses</h2>
            <p className="mt-1 text-sm text-slate-500">Choose a model to inspect the best three current KEH copies. Nothing here is public yet.</p>
          </div>
          <p className="text-sm text-slate-400">Showing {data.models.length} model groups</p>
        </div>

        <div className="mt-5 grid gap-4">
          {data.models.map((model) => (
            <details key={model.model_key} className="group rounded-3xl border border-white/10 bg-white/[0.04] p-5 open:bg-white/[0.06]">
              <summary className="cursor-pointer list-none">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <h3 className="font-bold text-white group-open:text-cyan-100">{model.model_name}</h3>
                    <p className="mt-1 text-sm text-slate-400">{model.mount} · {model.lens_type} · {model.focal_group} · {model.brand}</p>
                  </div>
                  <div className="flex flex-wrap items-center gap-3 text-sm">
                    <span className="rounded-full bg-white/10 px-3 py-1 text-slate-200">{model.listing_count} available</span>
                    <span className="font-bold text-emerald-200">from {money(model.lowest_price, model.currency)}</span>
                    <span className="text-cyan-200">View top 3 ↓</span>
                  </div>
                </div>
              </summary>

              <div className="mt-5 grid gap-4 lg:grid-cols-3">
                {model.listings.map((listing, index) => (
                  <article key={listing.aw_product_id} className="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
                    <div className="flex items-start gap-3">
                      {listing.image_url ? <img src={listing.image_url} alt="" className="h-20 w-20 rounded-xl object-contain bg-white" /> : null}
                      <div className="min-w-0">
                        <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">KEH option {index + 1}</p>
                        <p className="mt-1 line-clamp-3 text-sm font-semibold text-white">{listing.title}</p>
                      </div>
                    </div>
                    <div className="mt-4 flex items-end justify-between gap-3">
                      <div>
                        <p className="text-xl font-black text-white">{money(listing.price, listing.currency)}</p>
                        <p className="text-xs text-slate-400">{listing.condition_grade_code || "Used"}{listing.condition_grade_label ? ` · ${listing.condition_grade_label}` : ""}</p>
                      </div>
                      <a href={listing.affiliate_url} target="_blank" rel="noreferrer" className="rounded-xl bg-cyan-200 px-4 py-2 text-sm font-bold text-slate-950 hover:bg-cyan-100">
                        Open KEH
                      </a>
                    </div>
                  </article>
                ))}
              </div>
            </details>
          ))}

          {hasLensInventory && data.models.length === 0 ? (
            <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-6 text-slate-400">No current KEH lens models match that combination.</div>
          ) : null}
        </div>
      </section>
    </>
  );
}
