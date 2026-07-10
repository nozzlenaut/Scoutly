import Link from "next/link";
import { ResultCard } from "@/components/ResultCard";
import { searchDeals } from "@/lib/api";

export default async function SearchPage({ searchParams }: { searchParams: { q?: string } }) {
  const query = searchParams.q || "RTX 3060 12GB";
  const data = await searchDeals(query);
  const resolved = data.resolved_product;

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-white">
      <div className="mx-auto max-w-5xl">
        <Link href="/" className="text-sm text-cyan-200 hover:text-cyan-100">← New search</Link>
        <div className="mt-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
          <div>
            <p className="text-sm uppercase tracking-[0.25em] text-slate-500">Best used results</p>
            <h1 className="mt-2 text-4xl font-black">{resolved?.product.model ?? data.query}</h1>
            {resolved ? (
              <p className="mt-3 text-sm text-slate-400">
                Resolved to {resolved.product.display_name} · {Math.round(resolved.confidence * 100)}% confidence
              </p>
            ) : (
              <p className="mt-3 text-sm text-amber-300">No catalog match yet. Showing keyword-based results.</p>
            )}
          </div>
          <p className="text-sm text-slate-400">Mock providers with catalog filtering</p>
        </div>
        <section className="mt-8 grid gap-5 md:grid-cols-2">
          {data.results.map((result) => (
            <ResultCard key={`${result.provider}-${result.title}`} result={result} />
          ))}
        </section>
      </div>
    </main>
  );
}
