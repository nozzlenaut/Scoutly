import Link from "next/link";
import { AdminFilterRules } from "@/components/AdminFilterRules";
import { AdminReports } from "@/components/AdminReports";
import { SiteFooter } from "@/components/SiteFooter";
import { getActiveReports, getAnalyticsSummary, getManualFilterRules, getRecentClicks, getRecentFilteredListings } from "@/lib/api";

function formatDate(value?: string | null): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

function joinReasons(reasons?: string[]): string {
  if (!reasons || reasons.length === 0) return "—";
  return reasons.join(", ");
}

function AdminGate({ invalid = false }: { invalid?: boolean }) {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-white">
      <div className="mx-auto max-w-xl">
        <Link href="/" className="text-sm text-cyan-200 hover:text-cyan-100">← PriceSift</Link>
        <section className="mt-10 rounded-3xl border border-white/10 bg-white/[0.05] p-6">
          <p className="text-sm uppercase tracking-[0.25em] text-slate-500">PriceSift admin</p>
          <h1 className="mt-2 text-3xl font-black">Admin token required</h1>
          <p className="mt-3 text-sm text-slate-400">
            {invalid ? "That token was not accepted. Try the private token saved in Railway." : "Enter the private token saved in Railway to open testing analytics and live filter rules."}
          </p>
          <form method="get" action="/admin" className="mt-5 flex flex-col gap-3 sm:flex-row">
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
            <button className="rounded-2xl bg-white px-5 py-3 font-semibold text-slate-950 transition hover:bg-slate-200">Open admin</button>
          </form>
        </section>
      </div>
    </main>
  );
}

export default async function AdminPage({
  searchParams,
}: {
  searchParams: Promise<{ token?: string }>
}) {
  const params = await searchParams;
  const token = params.token?.trim();
  if (!token) return <AdminGate />;

  let data;
  try {
    data = await Promise.all([
      getAnalyticsSummary(token),
      getRecentClicks(token),
      getActiveReports(token),
      getRecentFilteredListings(token),
      getManualFilterRules(token),
    ]);
  } catch {
    return <AdminGate invalid />;
  }
  const [summary, clicks, reports, filtered, manualRules] = data;

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-white">
      <div className="mx-auto max-w-7xl">
        <Link href="/" className="text-sm text-cyan-200 hover:text-cyan-100">← PriceSift</Link>

        <div className="mt-8 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.25em] text-slate-500">PriceSift admin</p>
            <h1 className="mt-2 text-4xl font-black">Testing dashboard</h1>
            <p className="mt-3 max-w-3xl text-slate-400">
              PriceSift logs outbound clicks before redirecting to eBay, bad-result reports, and filtered listings that were rejected before ranking. eBay Partner reporting can still lag behind this.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link
              href={`/admin/prices?token=${encodeURIComponent(token)}`}
              className="w-fit rounded-2xl border border-cyan-200/25 bg-cyan-200/10 px-5 py-3 font-bold text-cyan-100 transition hover:bg-cyan-200/15"
            >
              Price history →
            </Link>
            <Link
              href={`/admin/qa?token=${encodeURIComponent(token)}`}
              className="w-fit rounded-2xl bg-cyan-200 px-5 py-3 font-bold text-slate-950 transition hover:bg-cyan-100"
            >
              Open search QA →
            </Link>
          </div>
        </div>

        <section className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-6">
          <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5">
            <p className="text-sm text-slate-400">Total outbound clicks</p>
            <p className="mt-2 text-3xl font-black">{summary.total_clicks}</p>
          </div>
          <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5">
            <p className="text-sm text-slate-400">Affiliate-tagged clicks</p>
            <p className="mt-2 text-3xl font-black">{summary.affiliate_clicks}</p>
          </div>
          <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5">
            <p className="text-sm text-slate-400">Active reports</p>
            <p className="mt-2 text-3xl font-black">{summary.active_bad_result_reports}</p>
          </div>
          <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5">
            <p className="text-sm text-slate-400">Filtered listings logged</p>
            <p className="mt-2 text-3xl font-black">{summary.filtered_listing_count ?? filtered.length}</p>
          </div>
          <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5">
            <p className="text-sm text-slate-400">Manual rules</p>
            <p className="mt-2 text-3xl font-black">{summary.manual_filter_rule_count ?? manualRules.length}</p>
          </div>
          <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5">
            <p className="text-sm text-slate-400">Persistent storage</p>
            <p className={`mt-2 text-lg font-black ${summary.storage?.connected ? "text-emerald-300" : "text-amber-300"}`}>
              {summary.storage?.connected ? "PostgreSQL connected" : summary.storage?.configured ? "Database degraded" : "Local file fallback"}
            </p>
          </div>
        </section>

        <AdminFilterRules initialRules={manualRules} token={token} />

        <section className="mt-10 rounded-3xl border border-white/10 bg-white/[0.04] p-5">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 className="text-2xl font-bold">Recent clicks</h2>
              <p className="mt-1 text-sm text-slate-500">What users actually clicked before PriceSift redirected to eBay.</p>
            </div>
          </div>
          <div className="mt-5 overflow-x-auto">
            <table className="w-full min-w-[900px] text-left text-sm">
              <thead className="text-slate-500">
                <tr>
                  <th className="py-2 pr-4">Time</th>
                  <th className="py-2 pr-4">Category</th>
                  <th className="py-2 pr-4">Query</th>
                  <th className="py-2 pr-4">Title</th>
                  <th className="py-2 pr-4">Affiliate</th>
                  <th className="py-2 pr-4">Item ID</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/10 text-slate-300">
                {clicks.map((click, index) => (
                  <tr key={`${click.clicked_at}-${click.ebay_item_id}-${index}`}>
                    <td className="py-3 pr-4 text-slate-400">{formatDate(click.clicked_at)}</td>
                    <td className="py-3 pr-4">{click.category || "—"}</td>
                    <td className="py-3 pr-4">{click.query || "—"}</td>
                    <td className="py-3 pr-4">{click.title || "—"}</td>
                    <td className="py-3 pr-4">{click.affiliate_campaign_present ? "Yes" : "No"}</td>
                    <td className="py-3 pr-4">{click.ebay_item_id || "—"}</td>
                  </tr>
                ))}
                {clicks.length === 0 ? (
                  <tr><td className="py-4 text-slate-500" colSpan={6}>No clicks logged yet.</td></tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </section>

        <section className="mt-10 rounded-3xl border border-white/10 bg-white/[0.04] p-5">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 className="text-2xl font-bold">Recently filtered listings</h2>
              <p className="mt-1 text-sm text-slate-500">Useful for debugging false positives. These were seen from eBay but rejected before ranking.</p>
            </div>
          </div>
          <div className="mt-5 overflow-x-auto">
            <table className="w-full min-w-[1000px] text-left text-sm">
              <thead className="text-slate-500">
                <tr>
                  <th className="py-2 pr-4">Time</th>
                  <th className="py-2 pr-4">Category</th>
                  <th className="py-2 pr-4">Type</th>
                  <th className="py-2 pr-4">Query</th>
                  <th className="py-2 pr-4">Title</th>
                  <th className="py-2 pr-4">Reason</th>
                  <th className="py-2 pr-4">Item ID</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/10 text-slate-300">
                {filtered.map((item, index) => (
                  <tr key={`${item.filtered_at}-${item.ebay_item_id}-${index}`}>
                    <td className="py-3 pr-4 text-slate-400">{formatDate(item.filtered_at)}</td>
                    <td className="py-3 pr-4">{item.category || "—"}</td>
                    <td className="py-3 pr-4">{item.listing_type || "—"}</td>
                    <td className="py-3 pr-4">{item.query || "—"}</td>
                    <td className="py-3 pr-4">{item.title || "—"}</td>
                    <td className="py-3 pr-4 text-amber-200">{joinReasons(item.reasons)}</td>
                    <td className="py-3 pr-4">{item.ebay_item_id || "—"}</td>
                  </tr>
                ))}
                {filtered.length === 0 ? (
                  <tr><td className="py-4 text-slate-500" colSpan={7}>No filtered listings logged yet.</td></tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </section>

        <AdminReports initialReports={reports} token={token} />

        <SiteFooter />
      </div>
    </main>
  );
}
