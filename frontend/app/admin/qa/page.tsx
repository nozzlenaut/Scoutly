import Link from "next/link";
import { QaWorkbench } from "@/components/QaWorkbench";
import { SiteFooter } from "@/components/SiteFooter";
import { getQaCases } from "@/lib/api";

function QaGate({ invalid = false }: { invalid?: boolean }) {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-white">
      <div className="mx-auto max-w-xl">
        <Link href="/" className="text-sm text-cyan-200 hover:text-cyan-100">← PriceSift</Link>
        <section className="mt-10 rounded-3xl border border-white/10 bg-white/[0.05] p-6">
          <p className="text-sm uppercase tracking-[0.25em] text-slate-500">PriceSift QA</p>
          <h1 className="mt-2 text-3xl font-black">Admin token required</h1>
          <p className="mt-3 text-sm text-slate-400">
            {invalid ? "That token was not accepted." : "Use the same private admin token as the testing dashboard."}
          </p>
          <form method="get" action="/admin/qa" className="mt-5 flex flex-col gap-3 sm:flex-row">
            <label className="flex-1">
              <span className="sr-only">Admin token</span>
              <input
                name="token"
                type="password"
                required
                autoComplete="current-password"
                placeholder="Admin token"
                className="w-full rounded-2xl border border-white/10 bg-white/[0.06] px-4 py-3 text-white outline-none placeholder:text-slate-600 focus:border-cyan-300/60"
              />
            </label>
            <button className="rounded-2xl bg-white px-5 py-3 font-semibold text-slate-950 transition hover:bg-slate-200">Open QA</button>
          </form>
        </section>
      </div>
    </main>
  );
}

export default async function QaPage({
  searchParams,
}: {
  searchParams: Promise<{ token?: string }>;
}) {
  const params = await searchParams;
  const token = params.token?.trim();
  if (!token) return <QaGate />;

  let data;
  try {
    data = await getQaCases(token);
  } catch {
    return <QaGate invalid />;
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-white">
      <div className="mx-auto max-w-[1500px]">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <Link href={`/admin?token=${encodeURIComponent(token)}`} className="text-sm text-cyan-200 hover:text-cyan-100">
            ← Testing dashboard
          </Link>
          <Link href="/" className="text-sm text-slate-500 hover:text-slate-300">PriceSift home</Link>
        </div>

        <div className="mt-8">
          <p className="text-sm uppercase tracking-[0.25em] text-slate-500">PriceSift admin</p>
          <h1 className="mt-2 text-4xl font-black">Search QA workbench</h1>
          <p className="mt-3 max-w-4xl text-slate-400">
            Run repeatable searches for every active category against the live marketplace, inspect the top three results, and save exactly what worked or failed. Each new evaluation becomes the latest status while preserving the attempt count.
          </p>
        </div>

        <QaWorkbench initialCases={data.cases} initialSummary={data.summary} token={token} />
        <SiteFooter />
      </div>
    </main>
  );
}
