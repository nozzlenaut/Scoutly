import type { Metadata } from "next";
import Link from "next/link";
import { getCodexDiagnostics } from "@/lib/api";

export const metadata: Metadata = {
  title: "PriceSift Codex Diagnostics",
  description: "Sanitized, read-only PriceSift deployment and QA diagnostics.",
  robots: { index: false, follow: false },
};

function formatDate(value: string): string {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

export default async function DiagnosticsPage() {
  let data;
  try {
    data = await getCodexDiagnostics();
  } catch {
    return (
      <main className="min-h-screen bg-slate-950 px-6 py-12 text-white">
        <div className="mx-auto max-w-3xl">
          <Link href="/admin" className="text-sm text-cyan-200 hover:text-cyan-100">← Admin</Link>
          <section className="mt-8 rounded-3xl border border-amber-300/20 bg-amber-300/[0.06] p-6">
            <h1 className="text-3xl font-black">Diagnostics unavailable</h1>
            <p className="mt-3 text-slate-400">The read-only diagnostics endpoint could not be reached.</p>
          </section>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-12 text-white">
      <div className="mx-auto max-w-6xl">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.25em] text-violet-300/70">Public-safe diagnostics</p>
            <h1 className="mt-2 text-4xl font-black">Codex inspection page</h1>
            <p className="mt-3 max-w-3xl text-slate-400">{data.purpose}</p>
            <p className="mt-2 text-xs text-slate-600">Generated {formatDate(data.generated_at)}</p>
          </div>
          <div className="flex gap-3">
            <Link href="/admin" className="rounded-xl border border-white/10 px-4 py-2 text-sm text-slate-300 hover:bg-white/[0.06]">Admin</Link>
            <a href={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/diagnostics/codex`} className="rounded-xl bg-violet-200 px-4 py-2 text-sm font-bold text-slate-950 hover:bg-violet-100">Raw JSON ↗</a>
          </div>
        </div>

        <section className="mt-8 grid gap-4 md:grid-cols-3">
          <div className="rounded-3xl border border-white/10 bg-white/[0.05] p-5">
            <p className="text-sm text-slate-500">Release</p>
            <p className="mt-2 text-2xl font-black">v{data.release.version}</p>
            <p className="mt-1 font-mono text-xs text-slate-500">{data.release.commit || "Commit unavailable"}</p>
          </div>
          <div className="rounded-3xl border border-white/10 bg-white/[0.05] p-5">
            <p className="text-sm text-slate-500">Active catalog products</p>
            <p className="mt-2 text-3xl font-black">{data.catalog.active_products}</p>
          </div>
          <div className="rounded-3xl border border-white/10 bg-white/[0.05] p-5">
            <p className="text-sm text-slate-500">QA quality rate</p>
            <p className="mt-2 text-3xl font-black">{data.qa.summary.quality_rate === null ? "—" : `${data.qa.summary.quality_rate}%`}</p>
          </div>
        </section>

        <section className="mt-8 grid gap-6 lg:grid-cols-2">
          <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-6">
            <h2 className="text-2xl font-bold">Providers</h2>
            <div className="mt-4 space-y-3">
              {data.providers.map((provider) => (
                <div key={provider.id} className="flex items-center justify-between gap-4 rounded-2xl border border-white/10 bg-slate-950/35 p-4">
                  <div>
                    <p className="font-bold uppercase">{provider.id}</p>
                    <p className="text-sm text-slate-500">{provider.role}</p>
                  </div>
                  <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${provider.live ? "border-emerald-300/25 bg-emerald-300/10 text-emerald-100" : "border-slate-300/15 bg-white/[0.04] text-slate-400"}`}>{provider.mode}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-6">
            <h2 className="text-2xl font-bold">Catalog</h2>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              {data.catalog.categories.map((category) => (
                <div key={category.id} className="rounded-2xl border border-white/10 bg-slate-950/35 p-4">
                  <p className="font-semibold">{category.label}</p>
                  <p className="mt-1 text-sm text-slate-500">{category.active_products} active products</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="mt-8 rounded-3xl border border-white/10 bg-white/[0.04] p-6">
          <h2 className="text-2xl font-bold">Recent sanitized QA runs</h2>
          <p className="mt-2 text-sm text-slate-500">No queries, notes, listing titles, user data, or private configuration are included.</p>
          <div className="mt-5 overflow-x-auto">
            <table className="w-full min-w-[850px] text-left text-sm">
              <thead className="text-slate-500"><tr><th className="pb-3 pr-4">Case</th><th className="pb-3 pr-4">Category</th><th className="pb-3 pr-4">Outcome</th><th className="pb-3 pr-4">Candidates</th><th className="pb-3 pr-4">Eligible</th><th className="pb-3 pr-4">Filtered</th><th className="pb-3">Time</th></tr></thead>
              <tbody className="divide-y divide-white/10 text-slate-300">
                {data.qa.recent_runs.map((run, index) => (
                  <tr key={`${run.case_id}-${run.created_at}-${index}`}><td className="py-3 pr-4 font-mono text-xs">{run.case_id}</td><td className="py-3 pr-4">{run.category}</td><td className="py-3 pr-4">{run.outcome}</td><td className="py-3 pr-4">{run.fixed_price_candidates}</td><td className="py-3 pr-4">{run.fixed_price_eligible}</td><td className="py-3 pr-4">{run.fixed_price_filtered}</td><td className="py-3 text-slate-500">{run.created_at ? formatDate(run.created_at) : "—"}</td></tr>
                ))}
                {data.qa.recent_runs.length === 0 ? <tr><td colSpan={7} className="py-5 text-slate-500">No saved QA runs yet.</td></tr> : null}
              </tbody>
            </table>
          </div>
        </section>

        <details className="mt-8 rounded-3xl border border-white/10 bg-white/[0.04] p-6">
          <summary className="cursor-pointer font-bold text-violet-100">Complete sanitized JSON</summary>
          <pre className="mt-5 overflow-x-auto rounded-2xl border border-white/10 bg-black/30 p-5 text-xs leading-6 text-slate-300">{JSON.stringify(data, null, 2)}</pre>
        </details>
      </div>
    </main>
  );
}
