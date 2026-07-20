"use client";

import { useState, type FormEvent } from "react";
import { runShippingQa, type ShippingQaItem, type ShippingQaResponse } from "@/lib/shippingQa";

const categories = [
  ["cameras", "Cameras"],
  ["consoles", "Consoles"],
  ["gpus", "GPUs"],
  ["cpus", "CPUs"],
  ["ram", "RAM"],
  ["lego", "LEGO"],
  ["books", "Books"],
] as const;

function money(value: number | null, currency = "USD"): string {
  if (value === null) return "Not returned";
  return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(value);
}

function dateLabel(value: string | null | undefined): string | null {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    timeZone: "America/Detroit",
  });
}

function deliveryLabel(item: ShippingQaItem): string {
  const option = item.best_shipping_option;
  const minimum = dateLabel(option?.min_delivery);
  const maximum = dateLabel(option?.max_delivery);
  if (minimum && maximum) return minimum === maximum ? minimum : `${minimum}–${maximum}`;
  return minimum || maximum || "No estimate returned";
}

function methodLabel(item: ShippingQaItem): string {
  const option = item.best_shipping_option;
  const values = [option?.carrier, option?.service, option?.speed].filter(Boolean);
  return Array.from(new Set(values)).join(" · ") || "No method returned";
}

export function ShippingQaLab({ token }: { token: string }) {
  const [query, setQuery] = useState("Sony a6700");
  const [category, setCategory] = useState("cameras");
  const [postalCode, setPostalCode] = useState("48035");
  const [running, setRunning] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [data, setData] = useState<ShippingQaResponse | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setRunning(true);
    setMessage(null);
    setData(null);
    try {
      setData(await runShippingQa(token, { query, category, postalCode, limit: 5 }));
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Shipping QA failed.");
    } finally {
      setRunning(false);
    }
  }

  return (
    <section className="mt-8 rounded-3xl border border-sky-300/20 bg-sky-300/[0.055] p-5 sm:p-6">
      <div className="flex flex-col gap-2 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.22em] text-sky-200/60">Private experiment</p>
          <h2 className="mt-2 text-2xl font-black text-sky-100">Shipping ZIP lab</h2>
          <p className="mt-2 max-w-4xl text-sm text-slate-400">
            Sends a buyer ZIP to eBay, filters to listings eBay says can ship there, then opens each item detail to measure how often cost, method, and delivery dates are returned. This diagnostic reruns the query; the public lookup checks only the already-visible listings and does not change ranking.
          </p>
        </div>
      </div>

      <form onSubmit={submit} className="mt-5 grid gap-3 lg:grid-cols-[minmax(240px,1fr)_180px_150px_auto]">
        <label>
          <span className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Search</span>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            required
            minLength={2}
            className="w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none focus:border-sky-300/60"
          />
        </label>
        <label>
          <span className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Category</span>
          <select
            value={category}
            onChange={(event) => setCategory(event.target.value)}
            className="w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none focus:border-sky-300/60"
          >
            {categories.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>
        </label>
        <label>
          <span className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Ship to ZIP</span>
          <input
            value={postalCode}
            onChange={(event) => setPostalCode(event.target.value)}
            required
            inputMode="numeric"
            maxLength={10}
            className="w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none focus:border-sky-300/60"
          />
        </label>
        <button
          type="submit"
          disabled={running}
          className="self-end rounded-2xl bg-sky-200 px-5 py-3 font-bold text-slate-950 transition hover:bg-sky-100 disabled:cursor-wait disabled:opacity-60"
        >
          {running ? "Checking…" : "Run ZIP test"}
        </button>
      </form>

      {message ? <p className="mt-4 rounded-2xl border border-rose-300/25 bg-rose-300/10 px-4 py-3 text-sm text-rose-100">{message}</p> : null}

      {data ? (
        <div className="mt-6">
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
            {[
              ["Returned", `${data.returned}`],
              ["Shipping cost", `${data.coverage.shipping_cost}/${data.returned}`],
              ["Delivery window", `${data.coverage.delivery_window}/${data.returned}`],
              ["Method / speed", `${data.coverage.method}/${data.returned}`],
              ["Detail loaded", `${data.coverage.detail_loaded}/${data.returned}`],
            ].map(([label, value]) => (
              <div key={label} className="rounded-2xl border border-white/10 bg-slate-950/35 p-4">
                <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
                <p className="mt-2 text-2xl font-black text-sky-100">{value}</p>
              </div>
            ))}
          </div>

          <p className="mt-4 text-xs text-slate-500">
            Delivery availability filter: active · Destination: {data.country} {data.postal_code} · eBay total matches: {data.search_total ?? "not returned"}
          </p>

          <div className="mt-4 space-y-3">
            {data.items.map((item, index) => (
              <article key={item.item_id || `${item.title}-${index}`} className="rounded-2xl border border-white/10 bg-slate-950/40 p-4">
                <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                  <div className="min-w-0">
                    <p className="text-xs text-slate-500">#{index + 1} · {item.condition} · {item.item_location || "Location not returned"}</p>
                    <h3 className="mt-1 font-bold text-white">{item.title}</h3>
                    <p className="mt-2 text-sm text-slate-300">{methodLabel(item)}</p>
                    <p className="mt-1 text-sm text-slate-400">Estimated delivery: {deliveryLabel(item)}</p>
                    <p className="mt-1 text-xs text-slate-600">
                      Summary options: {item.summary_option_count} · Detailed options: {item.detail_option_count}
                      {item.detail_error ? ` · Detail error: ${item.detail_error}` : ""}
                    </p>
                  </div>
                  <div className="shrink-0 text-left lg:text-right">
                    <p className="text-sm text-slate-400">Item {money(item.price, item.currency || "USD")}</p>
                    <p className="text-sm text-slate-400">Shipping {money(item.shipping_cost, item.currency || "USD")}</p>
                    <p className="mt-1 text-xl font-black text-sky-100">Total {money(item.total_price, item.currency || "USD")}</p>
                    {item.best_shipping_option?.import_charges !== null && item.best_shipping_option?.import_charges !== undefined ? (
                      <p className="mt-1 text-xs text-amber-200">Import charges: {money(item.best_shipping_option.import_charges, item.best_shipping_option.import_currency || item.currency || "USD")}</p>
                    ) : null}
                    {item.url ? <a href={item.url} target="_blank" rel="noreferrer" className="mt-2 inline-block text-sm font-semibold text-sky-200 hover:text-sky-100">Open listing ↗</a> : null}
                  </div>
                </div>
              </article>
            ))}
            {data.items.length === 0 ? <p className="rounded-2xl border border-white/10 p-4 text-sm text-slate-400">No used Buy It Now listings were returned as deliverable to that ZIP.</p> : null}
          </div>
        </div>
      ) : null}
    </section>
  );
}
