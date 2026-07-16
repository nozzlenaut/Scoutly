"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  buildOutboundUrl,
  getPublicKehLensBuilder,
  type KehLensBuilderResponse,
  type KehLensFacet,
  type KehLensModel,
} from "@/lib/api";

type FacetKind = "mount" | "lens_type" | "focal_group" | "brand";

function money(value?: number | null, currency = "USD"): string {
  if (value === null || value === undefined) return "—";
  try {
    return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(value);
  } catch {
    return `$${value.toFixed(2)}`;
  }
}

function publicFacets(options: KehLensFacet[], kind: FacetKind): KehLensFacet[] {
  return options.filter((option) => {
    const normalized = option.value.trim().toLowerCase();
    if (!normalized || normalized.includes("unknown") || normalized === "other") return false;
    if (kind === "lens_type") return option.value === "Prime" || option.value === "Zoom";
    if (kind === "brand") return normalized !== "unknown";
    return true;
  });
}

function FacetSelect({
  label,
  value,
  options,
  kind,
  disabled,
  placeholder,
  onChange,
}: {
  label: string;
  value: string;
  options: KehLensFacet[];
  kind: FacetKind;
  disabled?: boolean;
  placeholder: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="block">
      <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
        {label}
      </span>
      <select
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
        className="min-h-12 w-full rounded-2xl border border-white/10 bg-slate-900 px-4 text-white outline-none focus:border-cyan-300 disabled:cursor-not-allowed disabled:opacity-40"
      >
        <option value="">{placeholder}</option>
        {publicFacets(options, kind).map((option) => (
          <option key={option.value} value={option.value}>
            {option.label} ({option.count})
          </option>
        ))}
      </select>
    </label>
  );
}

function ConditionSummary({ model }: { model: KehLensModel }) {
  if (!model.condition_grades.length) return <span>Used inventory</span>;
  return <span>Grades: {model.condition_grades.join(" · ")}</span>;
}

function FocalRangeHelp({ lensType }: { lensType: string }) {
  if (lensType === "Prime") {
    return (
      <p className="mt-3 text-xs leading-5 text-slate-500">
        Prime groups use the lens focal length: under 20mm, 20–35mm, 36–60mm,
        61–105mm, 106–200mm, and over 200mm.
      </p>
    );
  }
  if (lensType === "Zoom") {
    return (
      <p className="mt-3 text-xs leading-5 text-slate-500">
        Zoom groups use the starting focal length: under 16mm ultra-wide,
        16–23mm wide, 24–49mm standard, 50–99mm telephoto, and 100mm+ super-telephoto.
        A 5× or greater range beginning at 35mm or wider is grouped as a travel zoom.
      </p>
    );
  }
  return null;
}

export function PublicKehLensFinder({ initialData }: { initialData: KehLensBuilderResponse }) {
  const [data, setData] = useState(initialData);
  const [mount, setMount] = useState("");
  const [lensType, setLensType] = useState("");
  const [focalGroup, setFocalGroup] = useState("");
  const [brand, setBrand] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const requestRef = useRef(0);
  const readyToBrowse = Boolean(mount && lensType && focalGroup);

  const filterSignature = useMemo(
    () => JSON.stringify({ mount, lensType, focalGroup, brand }),
    [mount, lensType, focalGroup, brand],
  );

  useEffect(() => {
    const requestNumber = requestRef.current + 1;
    requestRef.current = requestNumber;
    const timer = window.setTimeout(async () => {
      setBusy(true);
      setMessage(null);
      try {
        const next = await getPublicKehLensBuilder({
          mount: mount || undefined,
          lensType: lensType || undefined,
          focalGroup: focalGroup || undefined,
          brand: brand || undefined,
          limit: readyToBrowse ? 250 : 1,
          trackAnalytics: readyToBrowse,
        });
        if (requestNumber === requestRef.current) setData(next);
      } catch (error) {
        if (requestNumber === requestRef.current) {
          setMessage(error instanceof Error ? error.message : "Could not load KEH lens inventory.");
        }
      } finally {
        if (requestNumber === requestRef.current) setBusy(false);
      }
    }, 60);

    return () => window.clearTimeout(timer);
  }, [filterSignature, mount, lensType, focalGroup, brand, readyToBrowse]);

  function reset() {
    setMount("");
    setLensType("");
    setFocalGroup("");
    setBrand("");
  }

  const hasLensInventory = data.summary.listing_count > 0;

  return (
    <>
      <section className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5">
          <p className="text-sm text-slate-400">Available KEH listings</p>
          <p className="mt-2 text-3xl font-black">{data.summary.listing_count}</p>
        </div>
        <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5">
          <p className="text-sm text-slate-400">Unique lens models</p>
          <p className="mt-2 text-3xl font-black">{data.summary.model_count}</p>
        </div>
        <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5">
          <p className="text-sm text-slate-400">Matching models</p>
          <p className="mt-2 text-3xl font-black">{readyToBrowse ? data.summary.filtered_model_count : "—"}</p>
        </div>
        <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5">
          <p className="text-sm text-slate-400">Matching listings</p>
          <p className="mt-2 text-3xl font-black">{readyToBrowse ? data.summary.filtered_listing_count : "—"}</p>
        </div>
      </section>

      <section className="mt-8 rounded-3xl border border-white/10 bg-white/[0.04] p-5 sm:p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.22em] text-cyan-200">KEH-only lens beta</p>
            <h2 className="mt-2 text-2xl font-bold">Find an in-stock used lens</h2>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              Choose a mount, prime or zoom, and focal range. Brand is optional. PriceSift then shows
              exact lens models currently available from KEH. eBay lens results remain private while
              their listing quality is tested.
            </p>
          </div>
          <button
            type="button"
            onClick={reset}
            disabled={!mount && !lensType && !focalGroup && !brand}
            className="rounded-2xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-white/[0.06] disabled:cursor-not-allowed disabled:opacity-40"
          >
            Start over
          </button>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <FacetSelect
            label="1. Mount / system"
            value={mount}
            options={data.facets.mounts}
            kind="mount"
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
            kind="lens_type"
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
            kind="focal_group"
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
            kind="brand"
            disabled={!readyToBrowse}
            placeholder="Any lens brand"
            onChange={setBrand}
          />
        </div>

        <FocalRangeHelp lensType={lensType} />

        {readyToBrowse ? (
          <div className="mt-5 flex flex-wrap items-center gap-2 text-sm">
            <span className="rounded-full bg-cyan-300/10 px-3 py-1 text-cyan-100">{mount}</span>
            <span className="rounded-full bg-cyan-300/10 px-3 py-1 text-cyan-100">{lensType}</span>
            <span className="rounded-full bg-cyan-300/10 px-3 py-1 text-cyan-100">{focalGroup}</span>
            <span className="rounded-full bg-white/10 px-3 py-1 text-slate-300">{brand || "Any brand"}</span>
          </div>
        ) : null}

        {busy ? <p className="mt-4 text-sm text-cyan-200">Updating available lenses…</p> : null}
        {message ? (
          <p className="mt-4 rounded-2xl border border-rose-300/20 bg-rose-300/10 p-3 text-sm text-rose-100">
            {message}
          </p>
        ) : null}
        {!hasLensInventory ? (
          <p className="mt-5 rounded-2xl border border-amber-300/20 bg-amber-300/10 p-4 text-sm text-amber-100">
            KEH lens inventory is temporarily unavailable. Please check again after the next inventory sync.
          </p>
        ) : null}
      </section>

      <section className="mt-8">
        {!readyToBrowse ? (
          <div className="rounded-3xl border border-dashed border-white/15 bg-white/[0.03] p-8 text-center sm:p-12">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">Available models appear here</p>
            <h2 className="mt-3 text-2xl font-bold">Choose a mount, lens type, and focal group</h2>
            <p className="mx-auto mt-2 max-w-2xl text-sm leading-6 text-slate-400">
              Only combinations present in current KEH inventory appear in the dropdowns, so an unavailable
              focal group cannot lead you into a dead-end search.
            </p>
          </div>
        ) : data.models.length ? (
          <>
            <div className="flex flex-wrap items-end justify-between gap-3">
              <div>
                <p className="text-sm uppercase tracking-[0.2em] text-cyan-200">Choose an exact lens</p>
                <h2 className="mt-1 text-2xl font-bold">Models currently available at KEH</h2>
                <p className="mt-1 text-sm text-slate-500">Open a model to compare its three lowest-priced current listings.</p>
              </div>
              <p className="text-sm text-slate-400">
                {data.models.length} models · {data.summary.filtered_listing_count} listings
              </p>
            </div>

            <div className="mt-5 grid gap-4">
              {data.models.map((model) => (
                <details key={model.model_key} className="group overflow-hidden rounded-3xl border border-white/10 bg-white/[0.04] open:bg-white/[0.06]">
                  <summary className="cursor-pointer list-none p-4 sm:p-5">
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                      <div className="flex min-w-0 items-center gap-4">
                        {model.image_url ? (
                          <img src={model.image_url} alt="" className="h-20 w-20 shrink-0 rounded-2xl bg-white object-contain p-1" />
                        ) : (
                          <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-2xl bg-white/5 text-xs text-slate-500">No image</div>
                        )}
                        <div className="min-w-0">
                          <h3 className="font-bold text-white group-open:text-cyan-100">{model.model_name}</h3>
                          <p className="mt-1 text-sm text-slate-400">{model.brand} · {model.mount} · {model.focal_group}</p>
                          <p className="mt-2 text-xs text-slate-500"><ConditionSummary model={model} /></p>
                        </div>
                      </div>
                      <div className="flex flex-wrap items-center gap-3 text-sm sm:justify-end">
                        <span className="rounded-full bg-white/10 px-3 py-1 text-slate-200">{model.listing_count} available</span>
                        <span className="font-bold text-emerald-200">from {money(model.lowest_price, model.currency)}</span>
                        <span className="font-semibold text-cyan-200 group-open:hidden">View listings ↓</span>
                        <span className="hidden font-semibold text-cyan-200 group-open:inline">Hide listings ↑</span>
                      </div>
                    </div>
                  </summary>

                  <div className="border-t border-white/10 p-4 sm:p-5">
                    <div className="grid gap-4 lg:grid-cols-3">
                      {model.listings.map((listing, index) => {
                        const outboundUrl = buildOutboundUrl(listing.affiliate_url, {
                          query: model.model_name,
                          category: "lenses",
                          provider: "KEH",
                          title: listing.title,
                        });
                        return (
                          <article key={listing.aw_product_id} className="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
                            <div className="flex items-start gap-3">
                              {listing.image_url ? <img src={listing.image_url} alt="" className="h-20 w-20 rounded-xl bg-white object-contain p-1" /> : null}
                              <div className="min-w-0">
                                <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">KEH option {index + 1}</p>
                                <p className="mt-1 line-clamp-3 text-sm font-semibold text-white">{listing.title}</p>
                              </div>
                            </div>
                            <div className="mt-4 flex items-end justify-between gap-3">
                              <div>
                                <p className="text-xl font-black text-white">{money(listing.price, listing.currency)}</p>
                                <p className="text-xs text-slate-400">
                                  {listing.condition_grade_code
                                    ? `${listing.condition_grade_code}${listing.condition_grade_label ? ` · ${listing.condition_grade_label}` : ""}`
                                    : "Used"}
                                </p>
                              </div>
                              <a
                                href={outboundUrl}
                                target="_blank"
                                rel="sponsored noreferrer"
                                className="rounded-xl bg-emerald-300 px-4 py-2 text-sm font-bold text-slate-950 transition hover:bg-emerald-200"
                              >
                                View at KEH
                              </a>
                            </div>
                          </article>
                        );
                      })}
                    </div>
                    <p className="mt-4 text-xs leading-5 text-slate-500">
                      Prices and availability come from the latest KEH feed sync and can change before checkout.
                      Outbound KEH links are affiliate links.
                    </p>
                  </div>
                </details>
              ))}
            </div>
          </>
        ) : (
          <div className="rounded-3xl border border-amber-300/20 bg-amber-300/10 p-7 text-amber-50">
            <h2 className="text-xl font-bold">No current KEH inventory matches this combination.</h2>
            <p className="mt-2 text-sm leading-6 text-amber-100/90">
              Try another focal group or remove the optional brand filter. PriceSift does not substitute a different mount or lens type.
            </p>
          </div>
        )}
      </section>
    </>
  );
}
