import Link from "next/link";
import { AdminPriceDashboard } from "@/components/AdminPriceDashboard";
import { SiteFooter } from "@/components/SiteFooter";
import { getPriceOverview } from "@/lib/api";

function PriceGate({ invalid = false, detail }: { invalid?: boolean; detail?: string }) {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-white">
      <div className="mx-auto max-w-xl">
        <Link href="/" className="text-sm text-cyan-200 hover:text-cyan-100">← PriceSift</Link>
        <section className="mt-10 rounded-3xl border border-white/10 bg-white/[0.05] p-6">
          <p className="text-sm uppercase tracking-[0.25em] text-slate-500">PriceSift prices</p>
          <h1 className="mt-2 text-3xl font-black">Admin token required</h1>
          <p className="mt-3 text-sm text-slate-400">{invalid ? "PriceSift could not open the price overview with that token." : "Use the same private token as the QA workbench."}</p>
          {detail ? <p className="mt-3 break-words rounded-2xl bg-slate-950/50 p-3 font-mono text-xs text-amber-100/80">{detail}</p> : null}
          <form method="get" action="/admin/prices" className="mt-5 flex flex-col gap-3 sm:flex-row">
            <input name="token" type="password" required autoComplete="current-password" placeholder="Admin token" className="flex-1 rounded-2xl border border-white/10 bg-white/[0.06] px-4 py-3 text-white" />
            <button className="rounded-2xl bg-white px-5 py-3 font-semibold text-slate-950">Open prices</button>
          </form>
        </section>
      </div>
    </main>
  );
}

export default async function PriceHistoryPage({ searchParams }: { searchParams: Promise<{ token?: string }> }) {
  const params = await searchParams;
  const token = params.token?.trim();
  if (!token) return <PriceGate />;

  let overview;
  try {
    overview = await getPriceOverview(token, 30);
  } catch (error) {
    return <PriceGate invalid detail={error instanceof Error ? error.message : "Unknown price-history error"} />;
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
        <AdminPriceDashboard initialOverview={overview} token={token} />
        <SiteFooter />
      </div>
    </main>
  );
}
