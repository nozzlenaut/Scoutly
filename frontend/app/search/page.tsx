import Link from "next/link";
import { CategoryTabs } from "@/components/CategoryTabs";
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
  const data = await searchDeals(query, category.id);
  const resolved = data.resolved_product;

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-white">
      <div className="mx-auto max-w-6xl">
        <Link href="/" className="text-sm text-cyan-200 hover:text-cyan-100">← New search</Link>

        <div className="mt-8 rounded-3xl border border-white/10 bg-white/[0.04] p-4">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.25em] text-slate-500">Selected category</p>
              <p className="mt-2 font-semibold text-emerald-100">{category.group} · {category.label}</p>
            </div>
            <CategoryTabs selectedId={category.id} />
          </div>
        </div>

        <div className="relative z-50 mt-6">
          <SearchForm initialCategoryId={category.id} initialQuery={query} compact />
        </div>

        <div className="mt-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
          <div>
            <p className="text-sm uppercase tracking-[0.25em] text-slate-500">Best used results</p>
            <h1 className="mt-2 text-4xl font-black">{resolved?.product.display_name ?? data.query}</h1>
            {resolved ? (
              <p className="mt-3 text-sm text-slate-400">
                Resolved to {resolved.product.display_name} · {Math.round(resolved.confidence * 100)}% confidence
              </p>
            ) : (
              <p className="mt-3 text-sm text-amber-300">No catalog match yet. Showing keyword-based results.</p>
            )}
          </div>
          <p className="text-sm text-slate-400">Live eBay results · Up to 3 Buy It Now options plus ending-soon auctions</p>
        </div>

        {data.results.length > 0 ? (
          <section className="mt-8 space-y-5">
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

        <section className="mt-10">
          <div className="flex flex-col justify-between gap-2 sm:flex-row sm:items-end">
            <div>
              <p className="text-sm uppercase tracking-[0.25em] text-slate-500">Auction comparison</p>
              <h2 className="mt-2 text-2xl font-black">Ending soon</h2>
            </div>
            <p className="max-w-xl text-sm text-slate-400">Auctions are shown separately so they can be used for comparison without replacing the best available Buy It Now result. Scoutly shows up to three ending soon.</p>
          </div>

          {data.auction_results.length > 0 ? (
            <div className="mt-5 space-y-5">
              {data.auction_results.map((result) => (
                <ResultCard
                  key={`auction-${result.provider}-${result.title}`}
                  result={result}
                  query={data.query}
                  category={category.id}
                  productId={resolved?.product.id}
                  variant="auction"
                />
              ))}
            </div>
          ) : (
            <div className="mt-5 rounded-3xl border border-white/10 bg-white/[0.04] p-5 text-sm text-slate-400">
              No safe auction ending soon found for this exact item.
            </div>
          )}
        </section>

        <SiteFooter />
      </div>
    </main>
  );
}
