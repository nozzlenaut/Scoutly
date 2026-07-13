import type { Metadata } from "next";
import type { ReactNode } from "react";
import Link from "next/link";
import { AuctionResults } from "@/components/AuctionResults";
import { ResultCard } from "@/components/ResultCard";
import { SearchForm } from "@/components/SearchForm";
import { SiteFooter } from "@/components/SiteFooter";
import { searchDeals } from "@/lib/api";
import { getCategoryById, getSearchCategoryById } from "@/lib/categoryCatalog";

function PageShell({ children }: { children: ReactNode }) {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-white">
      <div className="mx-auto max-w-6xl">
        <div className="flex items-center justify-between gap-4">
          <Link href="/" className="text-2xl font-black tracking-tight text-white">Scoutly</Link>
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
      title: "Category unavailable | Scoutly",
      description: "This Scoutly category is unavailable or paused.",
    };
  }

  if (!query) {
    return {
      title: `Search ${category.label} | Scoutly`,
      description: `Search cleaner eBay used-listing results for ${category.label}.`,
    };
  }

  return {
    title: `${query} deals | Scoutly`,
    description: `Cleaner eBay used-listing results for ${query}.`,
  };
}

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; category?: string }>
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
              ? `${knownCategory.label} is paused right now while Scoutly improves filtering for that category.`
              : "That category is not available in Scoutly yet."}
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
          <p className="mt-3 text-sm leading-6">
            Type an exact {category.label.toLowerCase()} item above. Scoutly will not fall back to a default item from an empty URL.
          </p>
        </div>
      </PageShell>
    );
  }

  const data = await searchDeals(rawQuery, category.id, "ebay", { includeAuctions: false, auctionHours: 24 });
  const resolved = data.resolved_product;
  const emptyTarget = resolved ? "this resolved item" : "this query";

  return (
    <PageShell>
      <section className="mt-8 rounded-[2rem] border border-white/10 bg-white/[0.04] p-4 sm:p-5">
        <SearchForm initialCategoryId={category.id} initialQuery={rawQuery} compact />
      </section>

      <div className="mt-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="text-sm uppercase tracking-[0.25em] text-slate-500">Best used results</p>
          <h1 className="mt-2 text-4xl font-black">{resolved?.product.display_name ?? data.query}</h1>
          {resolved ? (
            <p className="mt-3 text-sm text-slate-400">
              Resolved to {resolved.product.display_name} · {Math.round(resolved.confidence * 100)}% confidence
            </p>
          ) : (
            <p className="mt-3 text-sm text-amber-300">No catalog match yet. Showing keyword-based results for this query.</p>
          )}
        </div>
        <p className="text-sm text-slate-400">Live eBay results · Up to 3 Buy It Now options</p>
      </div>

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
          No safe Buy It Now listings right now for {emptyTarget}. Scoutly is checking ending-soon auctions below, or you can try again later as eBay inventory changes.
        </div>
      )}

      <AuctionResults query={data.query} category={category.id} productId={resolved?.product.id} />
    </PageShell>
  );
}
