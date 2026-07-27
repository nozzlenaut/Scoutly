
import Link from "next/link";
import { AdminLoginForm } from "@/components/AdminLoginForm";
import { getAdminToken } from "@/lib/adminSession";
import { formatAdminDate } from "@/lib/formatAdminDate";
import { getGoodreadsAnalyticsDigest } from "@/lib/goodreadsApi";

function pct(value: number | null): string {
  return value === null ? "—" : `${value.toFixed(1)}%`;
}

export default async function GoodreadsAdminPage({
  searchParams,
}: {
  searchParams: Promise<{ days?: string }>;
}) {
  const params = await searchParams;
  const requestedDays = Number.parseInt(params.days || "30", 10);
  const days = [7, 30, 90].includes(requestedDays) ? requestedDays : 30;
  const token = await getAdminToken();

  if (!token) {
    return (
      <main className="px-6 py-10 text-white">
        <div className="mx-auto max-w-xl">
          <section className="rounded-3xl border border-white/10 bg-white/[0.05] p-6">
            <p className="text-sm uppercase tracking-[0.25em] text-slate-500">
              Goodreads analytics
            </p>
            <h1 className="mt-2 text-3xl font-black">
              Admin token required
            </h1>
            <AdminLoginForm next="/admin/goodreads" />
          </section>
        </div>
      </main>
    );
  }

  let digest;
  try {
    digest = await getGoodreadsAnalyticsDigest(token, days);
  } catch {
    return (
      <main className="px-6 py-10 text-white">
        <div className="mx-auto max-w-3xl">
          <h1 className="text-3xl font-black">
            Goodreads analytics unavailable
          </h1>
          <p className="mt-3 text-slate-400">
            The dedicated analytics endpoint could not be reached.
          </p>
        </div>
      </main>
    );
  }

  const cards = [
    ["Imports started", digest.import_count],
    ["Completed imports", digest.completed_import_count],
    ["Exact ISBN searches", digest.search_count],
    ["Exact editions found", digest.found_count],
    ["Exact-edition misses", digest.no_result_count],
    ["Exact success rate", pct(digest.exact_success_rate)],
    ["Exact listing clicks", digest.exact_listing_click_count],
    ["Other-edition clicks", digest.other_editions_click_count],
  ];

  return (
    <main className="px-6 py-10 text-white">
      <div className="mx-auto max-w-7xl">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.25em] text-cyan-300/70">
              Books beta
            </p>
            <h1 className="mt-2 text-4xl font-black">
              Goodreads import analytics
            </h1>
            <p className="mt-3 max-w-3xl text-slate-400">
              Separate from ordinary Books searches. One import remains one
              batch here even when it runs a hundred exact ISBN searches.
            </p>
          </div>
          <Link
            href="/books/goodreads"
            className="w-fit rounded-2xl border border-cyan-200/25 bg-cyan-200/10 px-5 py-3 font-bold text-cyan-100 transition hover:bg-cyan-200/15"
          >
            Open public Goodreads tool ↗
          </Link>
        </div>

        <div className="mt-8 flex flex-wrap gap-2">
          {[7, 30, 90].map((period) => (
            <Link
              key={period}
              href={`/admin/goodreads?days=${period}`}
              className={`rounded-full border px-4 py-2 text-sm font-semibold ${
                days === period
                  ? "border-cyan-200 bg-cyan-200 text-slate-950"
                  : "border-white/10 text-slate-300 hover:bg-white/[0.08]"
              }`}
            >
              {period} days
            </Link>
          ))}
        </div>

        <section className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {cards.map(([label, value]) => (
            <div
              key={String(label)}
              className="rounded-3xl border border-white/10 bg-white/[0.05] p-5"
            >
              <p className="text-sm text-slate-400">{label}</p>
              <p className="mt-2 text-3xl font-black">{value}</p>
            </div>
          ))}
        </section>

        <section className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div className="rounded-3xl border border-white/10 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">Rows imported</p>
            <p className="mt-2 text-2xl font-black">
              {digest.imported_row_count}
            </p>
          </div>
          <div className="rounded-3xl border border-white/10 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">Physical ISBNs ready</p>
            <p className="mt-2 text-2xl font-black">
              {digest.searchable_row_count}
            </p>
          </div>
          <div className="rounded-3xl border border-white/10 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">Digital/audio skipped</p>
            <p className="mt-2 text-2xl font-black">
              {digest.digital_skipped_count}
            </p>
          </div>
          <div className="rounded-3xl border border-white/10 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">Missing ISBNs</p>
            <p className="mt-2 text-2xl font-black">
              {digest.missing_isbn_count}
            </p>
          </div>
        </section>

        <section className="mt-8 overflow-hidden rounded-3xl border border-white/10 bg-white/[0.04]">
          <div className="border-b border-white/10 p-6">
            <h2 className="text-2xl font-black">Recent import batches</h2>
            <p className="mt-2 text-sm text-slate-400">
              Random batch IDs only; no Goodreads account, title, author,
              rating, review, or note data is stored.
            </p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[1050px] text-left text-sm">
              <thead className="text-slate-500">
                <tr>
                  <th className="px-6 py-3">Completed (ET)</th>
                  <th className="px-4 py-3">Shelf</th>
                  <th className="px-4 py-3">Imported</th>
                  <th className="px-4 py-3">Searchable</th>
                  <th className="px-4 py-3">Searched</th>
                  <th className="px-4 py-3">Found</th>
                  <th className="px-4 py-3">Exact misses</th>
                  <th className="px-4 py-3">Candidates</th>
                  <th className="px-4 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/10 text-slate-300">
                {digest.recent_batches.map((batch) => (
                  <tr key={batch.batch_id}>
                    <td className="px-6 py-4 text-slate-400">
                      {batch.completed_at
                        ? formatAdminDate(batch.completed_at)
                        : "—"}
                    </td>
                    <td className="px-4 py-4">{batch.shelf || "all"}</td>
                    <td className="px-4 py-4">{batch.imported_count}</td>
                    <td className="px-4 py-4">{batch.searchable_count}</td>
                    <td className="px-4 py-4">{batch.searched_count}</td>
                    <td className="px-4 py-4 text-emerald-200">
                      {batch.found_count}
                    </td>
                    <td className="px-4 py-4 text-amber-200">
                      {batch.no_result_count}
                    </td>
                    <td className="px-4 py-4">{batch.candidate_count}</td>
                    <td className="px-4 py-4">
                      {batch.complete ? "Complete" : "Partial"}
                    </td>
                  </tr>
                ))}
                {digest.recent_batches.length === 0 ? (
                  <tr>
                    <td
                      className="px-6 py-6 text-slate-500"
                      colSpan={9}
                    >
                      No Goodreads imports have been recorded yet.
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </section>

        <p className="mt-6 text-xs leading-5 text-slate-500">
          {digest.privacy_note}
        </p>
      </div>
    </main>
  );
}
