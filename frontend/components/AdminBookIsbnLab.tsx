"use client";

import { FormEvent, useMemo, useState } from "react";
import {
  buildOutboundUrl,
  searchBooksByIsbn,
  type BookLabResponse,
  type SearchResult,
} from "@/lib/api";

function money(value: number): string {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(value);
}

function ResultCard({ result, isbn, rank }: { result: SearchResult; isbn: string; rank?: number }) {
  const outbound = buildOutboundUrl(result.url, {
    query: isbn,
    category: "books",
    provider: result.provider,
    title: result.title,
  });

  return (
    <article className="rounded-3xl border border-white/10 bg-slate-950/60 p-4 sm:p-5">
      <div className="flex items-start gap-4">
        {result.image_url ? (
          <img src={result.image_url} alt="" className="h-24 w-20 shrink-0 rounded-xl bg-white object-contain p-1" />
        ) : (
          <div className="flex h-24 w-20 shrink-0 items-center justify-center rounded-xl bg-white/5 text-xs text-slate-600">No image</div>
        )}
        <div className="min-w-0">
          {rank ? <p className="text-xs font-bold uppercase tracking-[0.18em] text-cyan-200">Option {rank}</p> : null}
          <a href={outbound} target="_blank" rel="noreferrer" className="mt-1 block font-semibold text-white hover:text-cyan-100">
            {result.title}
          </a>
          <p className="mt-2 text-sm text-slate-400">{result.condition}</p>
          {result.warning_labels.length ? (
            <p className="mt-2 text-xs text-amber-200">{result.warning_labels.join(" · ")}</p>
          ) : null}
        </div>
      </div>
      <div className="mt-4 flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-2xl font-black text-white">{money(result.total_price)}</p>
          <p className="text-xs text-slate-500">
            {money(result.price)} item{result.shipping > 0 ? ` + ${money(result.shipping)} shipping` : " · free shipping shown"}
          </p>
        </div>
        <a href={outbound} target="_blank" rel="noreferrer" className="rounded-xl bg-cyan-200 px-4 py-2 text-sm font-bold text-slate-950 hover:bg-cyan-100">
          View on eBay
        </a>
      </div>
    </article>
  );
}

export function AdminBookIsbnLab({ token }: { token: string }) {
  const [isbn, setIsbn] = useState("");
  const [data, setData] = useState<BookLabResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const remainingResults = useMemo(() => {
    if (!data) return [];
    const topUrls = new Set(data.top_results.map((item) => item.url));
    return data.results.filter((item) => !topUrls.has(item.url));
  }, [data]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const value = isbn.trim();
    if (!value) return;
    setBusy(true);
    setMessage(null);
    try {
      const response = await searchBooksByIsbn(token, value);
      setData(response);
      if (!response.isbn.valid) setMessage("That does not appear to be a valid ISBN-10 or ISBN-13.");
    } catch (error) {
      setData(null);
      setMessage(error instanceof Error ? error.message : "The ISBN test search failed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <section className="mt-8 rounded-3xl border border-white/10 bg-white/[0.04] p-5 sm:p-6">
        <p className="text-sm uppercase tracking-[0.22em] text-cyan-200">Private Books experiment</p>
        <h2 className="mt-2 text-2xl font-bold">Test exact used-book matching</h2>
        <p className="mt-2 max-w-3xl text-sm text-slate-400">
          Enter an ISBN-10 or ISBN-13. PriceSift tests the equivalent ISBN when one exists, requests only used Buy It Now inventory, merges duplicates, and previews the three results a future Books category would show.
        </p>

        <form onSubmit={submit} className="mt-6 flex flex-col gap-3 sm:flex-row">
          <input
            value={isbn}
            onChange={(event) => setIsbn(event.target.value)}
            inputMode="text"
            autoComplete="off"
            placeholder="Search by ISBN-10 or ISBN-13"
            className="min-w-0 flex-1 rounded-2xl border border-white/10 bg-white/[0.06] px-4 py-3 text-white outline-none placeholder:text-slate-600 focus:border-cyan-300/60"
          />
          <button
            type="submit"
            disabled={busy || !isbn.trim()}
            className="rounded-2xl bg-white px-5 py-3 font-bold text-slate-950 hover:bg-slate-200 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {busy ? "Searching ISBN…" : "Test ISBN"}
          </button>
        </form>

        {message ? <p className="mt-4 rounded-2xl border border-amber-300/20 bg-amber-300/10 p-3 text-sm text-amber-100">{message}</p> : null}
      </section>

      {data?.isbn.valid ? (
        <>
          <section className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-6">
            <div className="rounded-3xl border border-white/10 bg-white/[0.05] p-5">
              <p className="text-sm text-slate-400">Detected format</p>
              <p className="mt-2 text-xl font-black">{data.isbn.input_type}</p>
            </div>
            <div className="rounded-3xl border border-white/10 bg-white/[0.05] p-5">
              <p className="text-sm text-slate-400">ISBN-10</p>
              <p className="mt-2 font-mono text-lg font-bold">{data.isbn.isbn10 || "Not available"}</p>
            </div>
            <div className="rounded-3xl border border-white/10 bg-white/[0.05] p-5">
              <p className="text-sm text-slate-400">ISBN-13</p>
              <p className="mt-2 font-mono text-lg font-bold">{data.isbn.isbn13 || "Not available"}</p>
            </div>
            <div className="rounded-3xl border border-white/10 bg-white/[0.05] p-5">
              <p className="text-sm text-slate-400">eBay candidates</p>
              <p className="mt-2 text-3xl font-black">{data.candidate_count}</p>
            </div>
            <div className="rounded-3xl border border-white/10 bg-white/[0.05] p-5">
              <p className="text-sm text-slate-400">Eligible used copies</p>
              <p className="mt-2 text-3xl font-black">{data.eligible_count}</p>
            </div>
            <div className="rounded-3xl border border-white/10 bg-white/[0.05] p-5">
              <p className="text-sm text-slate-400">Duplicates removed</p>
              <p className="mt-2 text-3xl font-black">{data.duplicates_removed}</p>
            </div>
          </section>

          {Object.keys(data.rejection_reasons).length ? (
            <div className="mt-5 rounded-2xl border border-amber-300/20 bg-amber-300/10 p-4 text-sm text-amber-100">
              {Object.entries(data.rejection_reasons).map(([reason, count]) => `${reason}: ${count}`).join(" · ")}
            </div>
          ) : null}

          <section className="mt-8">
            <div>
              <p className="text-sm uppercase tracking-[0.2em] text-cyan-200">Intended PriceSift results</p>
              <h2 className="mt-1 text-2xl font-bold">Top three used copies</h2>
              <p className="mt-1 text-sm text-slate-500">These are ordered by delivered price after exact ISBN matching and duplicate removal.</p>
            </div>
            {data.top_results.length ? (
              <div className="mt-5 grid gap-4 lg:grid-cols-3">
                {data.top_results.map((result, index) => <ResultCard key={`${result.url}-${index}`} result={result} isbn={data.isbn.normalized} rank={index + 1} />)}
              </div>
            ) : (
              <div className="mt-5 rounded-3xl border border-white/10 bg-white/[0.04] p-6 text-slate-400">
                eBay returned no eligible used Buy It Now copies tied to this ISBN.
              </div>
            )}
          </section>

          {remainingResults.length ? (
            <details className="mt-8 rounded-3xl border border-white/10 bg-white/[0.04]">
              <summary className="cursor-pointer list-none p-5 font-bold text-cyan-100">
                Inspect {remainingResults.length} additional eligible listings ↓
              </summary>
              <div className="grid gap-4 border-t border-white/10 p-5 md:grid-cols-2 xl:grid-cols-3">
                {remainingResults.map((result, index) => <ResultCard key={`${result.url}-extra-${index}`} result={result} isbn={data.isbn.normalized} />)}
              </div>
            </details>
          ) : null}
        </>
      ) : null}
    </>
  );
}
