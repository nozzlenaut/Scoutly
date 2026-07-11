import Link from "next/link";
import { CategoryTabs } from "@/components/CategoryTabs";
import { ResultCard } from "@/components/ResultCard";
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
      <div className="mx-auto max-w-5xl">
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
          <p className="text-sm text-slate-400">Live eBay results · one best listing per marketplace</p>
        </div>
        {data.results.length > 0 ? (
          <section className="mt-8 grid gap-5 md:grid-cols-2">
            {data.results.map((result) => (
              <ResultCard key={`${result.provider}-${result.title}`} result={result} />
            ))}
          </section>
        ) : (
          <div className="mt-8 rounded-3xl border border-amber-300/20 bg-amber-300/10 p-6 text-amber-100">
            No matching used listings found yet. Try a more specific product from autocomplete or check back after marketplace data refreshes.
          </div>
        )}
      </div>
    </main>
  );
}
