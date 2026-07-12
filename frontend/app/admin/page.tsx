import Link from "next/link";
import { SiteFooter } from "@/components/SiteFooter";
import { getActiveReports, getAnalyticsSummary, getRecentClicks, getRecentFilteredListings } from "@/lib/api";

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

export default async function AdminPage({
  searchParams,
}: {
  searchParams: Promise<{ token?: string }>
}) {
  const params = await searchParams;
  const token = params.token;
  const [summary, clicks, reports, filtered] = await Promise.all([
    getAnalyticsSummary(token),
    getRecentClicks(token),
    getActiveReports(token),
    getRecentFilteredListings(token),
  ]);

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-white">
      <div className="mx-auto max-w-7xl">
        <Link href="/" className="text-sm text-cyan-200 hover:text-cyan-100">← Scoutly</Link>

        <div className="mt-8">
          <p className="text-sm uppercase tracking-[0.25em] text-slate-500">Scoutly admin</p>
          <h1 className="mt-2 text-4xl font-black">Testing dashboard</h1>
          <p className="mt-3 max-w-3xl text-slate-400">
            Scoutly logs outbound clicks before redirecting to eBay, bad-result reports, and filtered listings that were rejected before ranking. eBay Partner reporting can still lag behind this.
          </p>
        </div>

        <section className="mt-8 grid gap-4 md:grid-cols-4">
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
        </section>

        <section className="mt-10 rounded-3xl border border-white/10 bg-white/[0.04] p-5">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 className="text-2xl font-bold">Recent clicks</h2>
              <p className="mt-1 text-sm text-slate-500">What users actually clicked before Scoutly redirected to eBay.</p>
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

        <section className="mt-10 rounded-3xl border border-white/10 bg-white/[0.04] p-5">
          <h2 className="text-2xl font-bold">Active bad-result reports</h2>
          <div className="mt-5 overflow-x-auto">
            <table className="w-full min-w-[900px] text-left text-sm">
              <thead className="text-slate-500">
                <tr>
                  <th className="py-2 pr-4">Reported</th>
                  <th className="py-2 pr-4">Expires</th>
                  <th className="py-2 pr-4">Reason</th>
                  <th className="py-2 pr-4">Category</th>
                  <th className="py-2 pr-4">Title</th>
                  <th className="py-2 pr-4">Item ID</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/10 text-slate-300">
                {reports.map((report, index) => (
                  <tr key={`${report.reported_at}-${report.link_key}-${index}`}>
                    <td className="py-3 pr-4 text-slate-400">{formatDate(report.reported_at)}</td>
                    <td className="py-3 pr-4 text-slate-400">{formatDate(report.expires_at)}</td>
                    <td className="py-3 pr-4">{report.reason || "—"}</td>
                    <td className="py-3 pr-4">{report.category || "—"}</td>
                    <td className="py-3 pr-4">{report.title || "—"}</td>
                    <td className="py-3 pr-4">{report.ebay_item_id || "—"}</td>
                  </tr>
                ))}
                {reports.length === 0 ? (
                  <tr><td className="py-4 text-slate-500" colSpan={6}>No active reports.</td></tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </section>

        <SiteFooter />
      </div>
    </main>
  );
}
