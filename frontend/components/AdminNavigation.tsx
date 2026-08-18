
import Link from "next/link";

const itemClass =
  "block rounded-xl px-3 py-2 text-sm text-slate-300 transition hover:bg-white/[0.08] hover:text-white";

export function AdminNavigation() {
  return (
    <nav className="sticky top-0 z-40 border-b border-white/10 bg-slate-950/95 px-4 py-3 text-white shadow-lg shadow-black/20 backdrop-blur">
      <div className="mx-auto flex max-w-[1500px] flex-wrap items-center gap-3">
        <Link
          href="/admin"
          className="mr-auto font-black tracking-tight text-cyan-100"
        >
          PriceSift admin
        </Link>

        <details className="group relative">
          <summary className="cursor-pointer list-none rounded-xl border border-white/10 bg-white/[0.04] px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-white/[0.08] [&::-webkit-details-marker]:hidden">
            Dashboard & logs{" "}
            <span aria-hidden="true" className="ml-1 text-cyan-200">
              ⌄
            </span>
          </summary>
          <div className="absolute right-0 mt-2 w-64 rounded-2xl border border-white/10 bg-slate-950 p-2 shadow-2xl shadow-black/50">
            <Link href="/admin" className={itemClass}>
              Dashboard overview
            </Link>
            <Link href="/admin#analytics" className={itemClass}>
              Analytics digest
            </Link>
            <Link href="/admin/goodreads" className={itemClass}>
              Goodreads imports
            </Link>
            <Link href="/admin#filter-rules" className={itemClass}>
              Manual filter rules
            </Link>
            <Link href="/admin#recent-clicks" className={itemClass}>
              Recent clicks
            </Link>
            <Link href="/admin#filtered-listings" className={itemClass}>
              Filtered listings
            </Link>
            <Link href="/admin#feedback" className={itemClass}>
              Feedback inbox
            </Link>
            <Link href="/admin#reports" className={itemClass}>
              Bad-result reports
            </Link>
          </div>
        </details>

        <details className="group relative">
          <summary className="cursor-pointer list-none rounded-xl border border-white/10 bg-white/[0.04] px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-white/[0.08] [&::-webkit-details-marker]:hidden">
            QA & labs{" "}
            <span aria-hidden="true" className="ml-1 text-cyan-200">
              ⌄
            </span>
          </summary>
          <div className="absolute right-0 mt-2 w-64 rounded-2xl border border-white/10 bg-slate-950 p-2 shadow-2xl shadow-black/50">
            <Link href="/admin/qa" className={itemClass}>
              Search QA workbench
            </Link>
            <Link href="/admin/books" className={itemClass}>
              Books ISBN lab
            </Link>
            <Link href="/admin/keh" className={itemClass}>
              KEH shadow feed
            </Link>
            <Link href="/admin/keh/lenses" className={itemClass}>
              KEH lens lab
            </Link>
            <Link href="/admin/prices#video-candidates" className={itemClass}>
              Top 5 video candidates
            </Link>
            <Link href="/admin/prices" className={itemClass}>
              Price history
            </Link>
          </div>
        </details>

        <Link
          href="/diagnostics"
          className="rounded-xl border border-violet-200/25 bg-violet-200/10 px-4 py-2 text-sm font-semibold text-violet-100 transition hover:bg-violet-200/15"
        >
          Codex diagnostics
        </Link>

        <Link
          href="/"
          className="rounded-xl px-3 py-2 text-sm text-slate-400 transition hover:text-white"
        >
          Public site ↗
        </Link>
      </div>
    </nav>
  );
}
