import Link from "next/link";

const PRICESIFT_VERSION = "0.6.47";

export function SiteFooter() {
  return (
    <footer className="mx-auto mt-12 max-w-5xl border-t border-white/10 px-2 py-6 text-sm text-slate-500">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="max-w-2xl">
          <p>
            PriceSift may earn from qualifying purchases through affiliate
            links. As an Amazon Associate I earn from qualifying purchases.
          </p>
          <p className="mt-1 text-xs text-slate-600">
            PriceSift v{PRICESIFT_VERSION}
          </p>
        </div>

        <div className="flex flex-wrap gap-x-4 gap-y-2">
          <Link href="/cameras" className="text-cyan-200 hover:text-cyan-100">
            Cameras
          </Link>
          <Link href="/lenses" className="text-cyan-200 hover:text-cyan-100">
            Lenses
          </Link>
          <Link href="/used" className="text-cyan-200 hover:text-cyan-100">
            Used price guides
          </Link>
          <Link href="/reuse" className="text-emerald-200 hover:text-emerald-100">
            Why buy used?
          </Link>
          <Link href="/feedback" className="text-cyan-200 hover:text-cyan-100">
            Beta feedback
          </Link>
          <Link href="/disclosure" className="text-cyan-200 hover:text-cyan-100">
            Affiliate disclosure
          </Link>
        </div>
      </div>
    </footer>
  );
}
