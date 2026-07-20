import { DeliveryResultsGrid } from "@/components/DeliveryResultsGrid";
import { ResultCard } from "@/components/ResultCard";
import { ShareSearchButton } from "@/components/ShareSearchButton";
import type { BookLabResponse } from "@/lib/api";

export function PublicBookResults({
  data,
  query,
  deliveryEnabled = false,
}: {
  data: BookLabResponse;
  query: string;
  deliveryEnabled?: boolean;
}) {
  const identity = data.isbn;
  const bestPrice = data.top_results[0]?.total_price ?? null;

  if (!identity.valid) {
    return (
      <div className="mt-8 rounded-3xl border border-amber-300/20 bg-amber-300/10 p-6 text-amber-50" role="status">
        <p className="text-sm uppercase tracking-[0.22em] text-amber-100/70">Invalid ISBN</p>
        <h1 className="mt-2 text-2xl font-black">That does not appear to be a valid ISBN-10 or ISBN-13.</h1>
        <p className="mt-3 text-sm leading-6 text-amber-100/90">
          Check the digits and try again. PriceSift validates the ISBN before sending anything to eBay.
        </p>
      </div>
    );
  }

  return (
    <>
      <div className="mt-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="text-sm uppercase tracking-[0.25em] text-slate-400">Exact used-book edition</p>
          <h1 className="mt-2 text-3xl font-black sm:text-4xl">ISBN {identity.normalized}</h1>
          <p className="mt-3 text-sm leading-6 text-slate-300">
            {identity.isbn13 ? `ISBN-13 ${identity.isbn13}` : ""}
            {identity.isbn13 && identity.isbn10 ? " · " : ""}
            {identity.isbn10 ? `ISBN-10 ${identity.isbn10}` : ""}
          </p>
          <p className="mt-1 text-sm text-slate-500">
            Exact ISBN matching · Used Buy It Now copies · Study guides and companion products removed
          </p>
        </div>
        <div className="flex flex-col items-start gap-3 sm:items-end">
          <p className="text-sm text-slate-300">Live eBay results · Up to 3 standard used copies</p>
          <ShareSearchButton label={`Book ISBN ${identity.normalized}`} bestPrice={bestPrice} />
        </div>
      </div>

      <section className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-3xl border border-white/10 bg-white/[0.05] p-5">
          <p className="text-sm text-slate-400">eBay candidates</p>
          <p className="mt-2 text-3xl font-black">{data.candidate_count}</p>
        </div>
        <div className="rounded-3xl border border-white/10 bg-white/[0.05] p-5">
          <p className="text-sm text-slate-400">Standard used copies</p>
          <p className="mt-2 text-3xl font-black">{data.standard_count}</p>
        </div>
        <div className="rounded-3xl border border-white/10 bg-white/[0.05] p-5">
          <p className="text-sm text-slate-400">Collectible copies separated</p>
          <p className="mt-2 text-3xl font-black">{data.collectible_count}</p>
        </div>
        <div className="rounded-3xl border border-white/10 bg-white/[0.05] p-5">
          <p className="text-sm text-slate-400">Book bundles separated</p>
          <p className="mt-2 text-3xl font-black">{data.bundle_count}</p>
        </div>
      </section>

      {data.top_results.length ? (
        <DeliveryResultsGrid
          results={data.top_results}
          query={identity.normalized}
          category="books"
          productId={`isbn-${identity.normalized}`}
          ariaLabel="Used book results"
          deliveryEnabled={deliveryEnabled}
        />
      ) : (
        <div className="mt-8 rounded-3xl border border-amber-300/20 bg-amber-300/10 p-6 text-amber-50" role="status">
          <h2 className="text-xl font-bold">
            {data.collectible_results.length || data.bundle_results.length
              ? "No standard single-copy results were found, but separated alternatives are available below."
              : data.candidate_count > 0
                ? `eBay returned ${data.candidate_count} candidates, but none passed the exact-title and used-copy checks.`
                : "No active used Buy It Now copies were returned for this exact ISBN."}
          </h2>
          <p className="mt-3 text-sm leading-6 text-amber-100/90">
            PriceSift would rather show nothing than fill the page with a different edition, study guide, or unrelated catalog match.
          </p>
        </div>
      )}

      {data.collectible_results.length ? (
        <section className="mt-10 rounded-3xl border border-purple-300/20 bg-purple-300/[0.06] p-5 sm:p-6">
          <p className="text-sm uppercase tracking-[0.2em] text-purple-200">Collectible alternatives</p>
          <h2 className="mt-1 text-2xl font-bold">Signed, deluxe, or special copies</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
            These match the ISBN but are separated because collectible pricing can distort a normal used-book comparison.
          </p>
          <div className="mt-5 grid gap-5 xl:grid-cols-3">
            {data.collectible_results.slice(0, 3).map((result, index) => (
              <ResultCard
                key={`collectible-book-${result.url}-${index}`}
                result={result}
                query={identity.normalized}
                category="books"
                productId={`isbn-${identity.normalized}`}
                variant="buy_now"
              />
            ))}
          </div>
        </section>
      ) : null}

      {data.bundle_results.length ? (
        <section className="mt-10 rounded-3xl border border-amber-300/20 bg-amber-300/[0.06] p-5 sm:p-6">
          <p className="text-sm uppercase tracking-[0.2em] text-amber-200">Multi-book alternatives</p>
          <h2 className="mt-1 text-2xl font-bold">Lots and bundles containing this book</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
            These appear to include the requested ISBN, but they are separated because their prices cannot be compared fairly with one used copy.
          </p>
          <div className="mt-5 grid gap-5 xl:grid-cols-3">
            {data.bundle_results.slice(0, 3).map((result, index) => (
              <ResultCard
                key={`bundle-book-${result.url}-${index}`}
                result={result}
                query={identity.normalized}
                category="books"
                productId={`isbn-${identity.normalized}`}
                variant="buy_now"
              />
            ))}
          </div>
        </section>
      ) : null}

      {Object.keys(data.rejection_reasons).length ? (
        <details className="mt-8 rounded-3xl border border-white/10 bg-white/[0.04]">
          <summary className="cursor-pointer list-none p-5 text-sm font-bold text-cyan-100">Why listings were removed ↓</summary>
          <div className="border-t border-white/10 p-5 text-sm text-slate-300">
            {Object.entries(data.rejection_reasons).map(([reason, count]) => `${reason}: ${count}`).join(" · ")}
          </div>
        </details>
      ) : null}
    </>
  );
}
