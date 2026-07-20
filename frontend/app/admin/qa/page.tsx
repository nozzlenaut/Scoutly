import Link from "next/link";
import { LensQaWorkbench, type LensQaCase } from "@/components/LensQaWorkbench";
import { QaWorkbench } from "@/components/QaWorkbench";
import { ShippingQaLab } from "@/components/ShippingQaLab";
import { SiteFooter } from "@/components/SiteFooter";
import { getQaCases, type QaCase, type QaOutcome, type QaSummary } from "@/lib/api";

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

function summarizeCases(cases: QaCase[]): QaSummary {
  const counts: QaSummary["counts"] = {
    pass: 0,
    top3_only: 0,
    fail: 0,
    no_inventory: 0,
    untested: 0,
  };
  const categoryCounts: QaSummary["category_counts"] = {};

  for (const testCase of cases) {
    categoryCounts[testCase.category] ??= {
      pass: 0,
      top3_only: 0,
      fail: 0,
      no_inventory: 0,
      untested: 0,
    };
    const outcome: QaOutcome | "untested" = testCase.latest_evaluation?.outcome ?? "untested";
    counts[outcome] += 1;
    categoryCounts[testCase.category][outcome] += 1;
  }

  const tested = cases.length - counts.untested;
  const availableInventoryCases = counts.pass + counts.top3_only + counts.fail;
  const quality = counts.pass + counts.top3_only;

  return {
    total_cases: cases.length,
    tested_cases: tested,
    available_inventory_cases: availableInventoryCases,
    counts,
    category_counts: categoryCounts,
    quality_rate: availableInventoryCases
      ? Math.round((quality / availableInventoryCases) * 1000) / 10
      : null,
    overall_rate: tested ? Math.round((quality / tested) * 1000) / 10 : null,
  };
}

function isLensCase(testCase: QaCase): testCase is LensQaCase {
  const candidate = testCase as Partial<LensQaCase>;
  return (
    candidate.category === "lenses" &&
    candidate.runner === "keh_lens" &&
    Boolean(candidate.lens_filters?.mount) &&
    Boolean(candidate.lens_filters?.lens_type) &&
    Boolean(candidate.lens_filters?.focal_group)
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

  const lensCases = data.cases.filter(isLensCase);
  const searchCases = data.cases.filter((testCase) => !isLensCase(testCase));

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-white">
      <div className="mx-auto max-w-[1500px]">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <Link href={`/admin?token=${encodeURIComponent(token)}`} className="text-sm text-cyan-200 hover:text-cyan-100">
            ← Testing dashboard
          </Link>
          <div className="flex flex-wrap gap-4">
            <Link href={`/admin/keh/lenses?token=${encodeURIComponent(token)}`} className="text-sm text-emerald-200 hover:text-emerald-100">Lens Lab</Link>
            <Link href={`/admin/prices?token=${encodeURIComponent(token)}`} className="text-sm text-slate-400 hover:text-slate-200">Price history</Link>
            <Link href="/" className="text-sm text-slate-500 hover:text-slate-300">PriceSift home</Link>
          </div>
        </div>

        <div className="mt-8">
          <p className="text-sm uppercase tracking-[0.25em] text-slate-500">PriceSift admin</p>
          <h1 className="mt-2 text-4xl font-black">Search QA workbench</h1>
          <p className="mt-3 max-w-4xl text-slate-400">
            Test exact-item matching, the KEH Lens Lab, and ZIP-specific eBay shipping coverage before any behavior reaches the public search. Saved search attempts remain attached to their original case IDs.
          </p>
        </div>

        <ShippingQaLab token={token} />

        <QaWorkbench
          initialCases={searchCases}
          initialSummary={summarizeCases(searchCases)}
          token={token}
        />

        {lensCases.length ? <LensQaWorkbench initialCases={lensCases} token={token} /> : null}

        <SiteFooter />
      </div>
    </main>
  );
}
