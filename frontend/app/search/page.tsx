import Link from "next/link";
import { AuctionResults } from "@/components/AuctionResults";
import { ResultCard } from "@/components/ResultCard";
import { SearchForm } from "@/components/SearchForm";
import { SiteFooter } from "@/components/SiteFooter";
import { searchDeals } from "@/lib/api";
import { getCategory } from "@/lib/categoryCatalog";

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; category?: string }>
}) {
  const params = await searchParams;
  const category = getCategory(params.category);
  const query = params.q || category.defaultQuery;
  const data = await searchDeals(query, category.id, "ebay", { includeAuctions: false, auctionHours: 24 });
  const resolved = data.resolved_product;

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-white">
      <div className="mx-auto max-w-6xl">
        <div className="flex items-center justify-between gap-4">
          <Link href="/" className="text-2xl font-black tracking-tight text-white">Scoutly</Link>
          <Link href="/" className="text-sm text-cyan-200 hover:text-cyan-100">Home</Link>
        </div>

        <section className="mt-8 rounded-[2rem] border border-white/10 bg-white/[0.04] p-5 sm:p-6">
          <div className="mb-6">
            <p className="text-sm uppercase tracking-[0.25em] text-slate-500">Search again</p>
            <h1 className="mt-2 text-3xl font-black sm:text-4xl">Find another exact item</h1>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-400">
              Pick a category, type the exact item, and Scoutly filters for complete used listings — not boxes, parts, broken items, or weird accessories when we can catch them.
            </p>
          </div>
          <SearchForm initialCategoryId={category.id} initialQuery={query} />
        </section>

        <div className="mt-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
          <div>
            <p className="text-sm uppercase tracking-[0.25em] text-slate-500">Best used results</p>
            <h2 className="mt-2 text-4xl font-black">{resolved?.product.display_name ?? data.query}</h2>
            {resolved ? (
              <p className="mt-3 text-sm text-slate-400">
                Resolved to {resolved.product.display_name} · {Math.round(resolved.confidence * 100)}% confidence
              </p>
            ) : (
              <p className="mt-3 text-sm text-amber-300">No catalog match yet. Showing keyword-based results.</p>
            )}
          </div>
          <p className="text-sm text-slate-400">Live eBay results · Up to 3 Buy It Now options</p>
        </div>

        {data.results.length > 0 ? (
          <section className="mt-8 grid gap-5 xl:grid-cols-3">
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
          <div className="mt-8 rounded-3xl border border-amber-300/20 bg-amber-300/10 p-6 text-amber-100">
            No matching complete used Buy It Now listings found yet. Try a more specific product from autocomplete or check back after marketplace data refreshes.
          </div>
        )}

        <AuctionResults query={data.query} category={category.id} productId={resolved?.product.id} />

        <SiteFooter />
      </div>
    </main>
  );
}
