import type { Metadata } from "next";
import type { ReactNode } from "react";
import Link from "next/link";
import { AuctionResults } from "@/components/AuctionResults";
import { ResultCard } from "@/components/ResultCard";
import { SearchForm } from "@/components/SearchForm";
import { SearchTransitionGuard } from "@/components/SearchTransitionGuard";
import { SiteFooter } from "@/components/SiteFooter";
import { searchDeals } from "@/lib/api";
import { getCategoryById, getSearchCategoryById } from "@/lib/categoryCatalog";

function PageShell({ children }: { children: ReactNode }) {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-white">
      <div className="mx-auto max-w-6xl">
        <div className="flex items-center justify-between gap-4">
          <Link href="/" className="text-2xl font-black tracking-tight text-white">PriceSift</Link>
          <Link href="/" className="text-sm text-cyan-200 hover:text-cyan-100">Home</Link>
        </div>
        {children}
        <SiteFooter />
      </div>
    </main>
  );
}

export async function generateMetadata({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; category?: string }>;
}): Promise<Metadata> {
  const params = await searchParams;
  const category = getSearchCategoryById(params.category);
  const query = (params.q || "").trim();

  if (!category) {
    return {
      title: "Category unavailable",
      description: "This PriceSift category is unavailable or paused.",
      robots: { index: false, follow: true },
    };
  }

  if (!query) {
    return {
      title: `Search ${category.label}`,
      description: `Search cleaner eBay used-listing results for ${category.label}.`,
      robots: { index: false, follow: true },
    };
  }

  return {
    title: `${query} deals`,
    description: `Cleaner eBay used-listing results for ${query}.`,
    robots: { index: false, follow: true },
  };
}

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; category?: string }>;
}) {
  const params = await searchParams;
  const rawCategory = (params.category || "").trim();
  const rawQuery = (params.q || "").trim();
  const knownCategory = getCategoryById(rawCategory);
  const category = getSearchCategoryById(rawCategory);

  if (!category) {
    return (
      <PageShell>
        <section className="mt-8 rounded-[2rem] border border-white/10 bg-white/[0.04] p-5">
          <SearchForm />
        </section>
        <div className="mt-8 rounded-3xl border border-amber-300/20 bg-amber-300/10 p-6 text-amber-100" role="status">
          <h1 className="text-2xl font-black">Category unavailable</h1>
          <p className="mt-3 text-sm leading-6">
            {knownCategory
              ? `${knownCategory.label} is paused right now while PriceSift improves filtering for that category.`
              : "That category is not available in PriceSift yet."}
          </p>
          <p className="mt-3 text-sm leading-6">Pick an active category above to search again.</p>
        </div>
      </PageShell>
    );
  }

  if (!rawQuery) {
    return (
      <PageShell>
        <section className="mt-8 rounded-[2rem] border border-white/10 bg-white/[0.04] p-5">
          <SearchForm initialCategoryId={category.id} initialQuery="" compact />
        </section>
        <div className="mt-8 rounded-3xl border border-white/10 bg-white/[0.05] p-6 text-slate-200" role="status">
          <h1 className="text-2xl font-black">Search needed</h1>
          <p className="mt-3 text-sm leading-6 text-slate-300">
            Type an exact {category.label.toLowerCase()} item above. PriceSift will not fall back to a default item from an empty URL.
          </p>
        </div>
      </PageShell>
    );
  }

  const data = await searchDeals(rawQuery, category.id, "ebay", { includeAuctions: false, auctionHours: 24 });
  const resolved = data.resolved_product;
  const likelyAlternatives = (data.suggested_products || []).filter((match) => match.confidence >= 0.8).slice(0, 4);
  const emptyTarget = resolved ? "this resolved item" : "this query";
  const fixedPriceEmptyMessage =
    data.diagnostics.fixed_price_candidates > 0
      ? `No safe Buy It Now listings right now for ${emptyTarget}. PriceSift found listings, but automated checks filtered them.`
      : `No active Buy It Now listings were found right now for ${emptyTarget}.`;

  return (
    <PageShell>
      <section className="mt-8 rounded-[2rem] border border-white/10 bg-white/[0.04] p-4 sm:p-5">
        <SearchForm key={`${category.id}:${rawQuery}`} initialCategoryId={category.id} initialQuery={rawQuery} compact />
      </section>

      <SearchTransitionGuard>
        <div className="mt-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
          <div>
            <p className="text-sm uppercase tracking-[0.25em] text-slate-400">Best used results</p>
            <h1 className="mt-2 text-4xl font-black">{resolved?.product.display_name ?? data.query}</h1>
            {resolved ? (
              <p className="mt-3 text-sm text-slate-300">
                Catalog item: {resolved.product.display_name} · Product match confidence {Math.round(resolved.confidence * 100)}%
              </p>
            ) : (
              <p className="mt-3 text-sm text-amber-200">
                No single catalog item was selected. Results use the search text as written.
              </p>
            )}
          </div>
          <p className="text-sm text-slate-300">Live eBay results · Up to 3 Buy It Now options</p>
        </div>

        {!resolved && likelyAlternatives.length > 0 ? (
          <div className="mt-5 rounded-3xl border border-cyan-300/20 bg-cyan-300/10 p-5 text-cyan-50">
            <p className="font-semibold">Choose an exact catalog variant for stricter filtering:</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {likelyAlternatives.map((match) => (
                <Link
                  key={match.product.id}
                  href={`/search?category=${encodeURIComponent(category.id)}&q=${encodeURIComponent(match.product.display_name)}`}
                  className="rounded-full border border-cyan-200/25 bg-slate-950/35 px-4 py-2 text-sm font-semibold text-cyan-50 transition hover:bg-slate-950/55"
                >
                  {match.product.display_name}
                </Link>
              ))}
            </div>
          </div>
        ) : null}

        {data.results.length > 0 ? (
          <section className="mt-8 grid gap-5 xl:grid-cols-3" aria-label="Buy It Now results">
            {data.results.map((result) => (
              <ResultCard
                key={`buy-now-${result.provider}-${result.title}`}
                result={result}
                query={data.query}
                category={category.id}
                productId={resolved?.product.id}
                variant="buy_now"
              />
            ))}
          </section>
        ) : (
          <div className="mt-8 rounded-3xl border border-amber-300/20 bg-amber-300/10 p-6 text-amber-100" role="status">
            {fixedPriceEmptyMessage} PriceSift is checking ending-soon auctions below.
          </div>
        )}

        <AuctionResults query={data.query} category={category.id} productId={resolved?.product.id} resolved={Boolean(resolved)} />
      </SearchTransitionGuard>
    </PageShell>
  );
}
