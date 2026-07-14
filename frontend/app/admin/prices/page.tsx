import Link from "next/link";
import { PriceCollector } from "@/components/PriceCollector";
import { SiteFooter } from "@/components/SiteFooter";
import { getPriceOverview } from "@/lib/api";

function PriceGate({ invalid = false }: { invalid?: boolean }) {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-white">
      <div className="mx-auto max-w-xl">
        <Link href="/" className="text-sm text-cyan-200 hover:text-cyan-100">← PriceSift</Link>
        <section className="mt-10 rounded-3xl border border-white/10 bg-white/[0.05] p-6">
          <p className="text-sm uppercase tracking-[0.25em] text-slate-500">PriceSift prices</p>
          <h1 className="mt-2 text-3xl font-black">Admin token required</h1>
          <p className="mt-3 text-sm text-slate-400">{invalid ? "That token was not accepted." : "Use the same private token as the QA workbench."}</p>
          <form method="get" action="/admin/prices" className="mt-5 flex flex-col gap-3 sm:flex-row">
            <input name="token" type="password" required placeholder="Admin token" className="flex-1 rounded-2xl border border-white/10 bg-white/[0.06] px-4 py-3 text-white" />
            <button className="rounded-2xl bg-white px-5 py-3 font-semibold text-slate-950">Open prices</button>
          </form>
        </section>
      </div>
    </main>
  );
}

function money(value?: number | null): string {
  return value === null || value === undefined ? "—" : `$${value.toFixed(2)}`;
}

function dateLabel(value?: string | null): string {
  if (!value) return "—";
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
}

export default async function PriceHistoryPage({ searchParams }: { searchParams: Promise<{ token?: string }> }) {
  const params = await searchParams;
  const token = params.token?.trim();
  if (!token) return <PriceGate />;

  let overview;
  try {
    overview = await getPriceOverview(token, 30);
  } catch {
    return <PriceGate invalid />;
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-white">
      <div className="mx-auto max-w-[1500px]">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <Link href={`/admin?token=${encodeURIComponent(token)}`} className="text-sm text-cyan-200 hover:text-cyan-100">← Testing dashboard</Link>
          <Link href={`/admin/qa?token=${encodeURIComponent(token)}`} className="text-sm text-slate-400 hover:text-slate-200">Search QA</Link>
        </div>

        <div className="mt-8">
          <p className="text-sm uppercase tracking-[0.25em] text-slate-500">PriceSift admin</p>
          <h1 className="mt-2 text-4xl font-black">Price history</h1>
          <p className="mt-3 max-w-4xl text-slate-400">Six-hour snapshots from clean, eligible Buy It Now listings. Empty snapshots are retained too, so availability history does not get rewritten into fake optimism.</p>
        </div>

        <section className="mt-8 grid gap-4 md:grid-cols-4">
          <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5"><p className="text-sm text-slate-400">Snapshots</p><p className="mt-2 text-3xl font-black">{overview.snapshot_count}</p></div>
          <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5"><p className="text-sm text-slate-400">Products observed</p><p className="mt-2 text-3xl font-black">{overview.product_count}</p></div>
          <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5"><p className="text-sm text-slate-400">Typical range ready</p><p className="mt-2 text-3xl font-black">{overview.history_ready_count}</p></div>
          <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5"><p className="text-sm text-slate-400">Inventory in latest sample</p><p className="mt-2 text-3xl font-black">{overview.available_latest_count}</p></div>
        </section>

        <div className="mt-8"><PriceCollector token={token} /></div>

        <section className="mt-8 rounded-3xl border border-white/10 bg-white/[0.04] p-5">
          <h2 className="text-2xl font-bold">Observed products</h2>
          <div className="mt-5 overflow-x-auto">
            <table className="w-full min-w-[1050px] text-left text-sm">
              <thead className="text-slate-500"><tr><th className="py-2 pr-4">Product</th><th className="py-2 pr-4">Category</th><th className="py-2 pr-4">Latest best</th><th className="py-2 pr-4">Eligible</th><th className="py-2 pr-4">Typical range</th><th className="py-2 pr-4">Availability</th><th className="py-2 pr-4">Snapshots</th><th className="py-2 pr-4">Last observed</th></tr></thead>
              <tbody className="divide-y divide-white/10 text-slate-300">
                {overview.products.map((product) => (
                  <tr key={product.product_id}>
                    <td className="py-3 pr-4 font-semibold text-white">{product.product_label}</td>
                    <td className="py-3 pr-4">{product.category}</td>
                    <td className="py-3 pr-4">{money(product.latest_best_price)}</td>
                    <td className="py-3 pr-4">{product.latest_eligible_count}</td>
                    <td className="py-3 pr-4">{product.history_ready ? `${money(product.typical_low_price)}–${money(product.typical_high_price)}` : "Building"}</td>
                    <td className="py-3 pr-4">{product.availability_rate == null ? "—" : `${product.availability_rate.toFixed(1)}%`}</td>
                    <td className="py-3 pr-4">{product.snapshot_count}</td>
                    <td className="py-3 pr-4 text-slate-400">{dateLabel(product.last_observed_at)}</td>
                  </tr>
                ))}
                {overview.products.length === 0 ? <tr><td colSpan={8} className="py-5 text-slate-500">No snapshots yet. Running QA searches after deployment will begin filling this table automatically.</td></tr> : null}
              </tbody>
            </table>
          </div>
        </section>
        <SiteFooter />
      </div>
    </main>
  );
}
