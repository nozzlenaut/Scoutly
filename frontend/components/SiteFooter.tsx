import Link from "next/link";

const PRICESIFT_VERSION = "0.6.47";

export function SiteFooter() {
  return (
    <footer className="mx-auto mt-12 max-w-5xl border-t border-white/10 px-2 py-6 text-sm text-slate-500 [.pricesift-home_&]:text-ps-text-secondary [.pricesift-results_&]:border-ps-border [.pricesift-results_&]:text-ps-text-secondary [.pricesift-public_&]:border-ps-border [.pricesift-public_&]:text-ps-text-secondary">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="max-w-2xl">
          <p>
            PriceSift may earn from qualifying purchases through affiliate
            links. As an Amazon Associate I earn from qualifying purchases.
          </p>
          <p className="mt-1 text-xs text-slate-600 [.pricesift-home_&]:text-ps-neutral [.pricesift-results_&]:text-ps-neutral [.pricesift-public_&]:text-ps-neutral">
            PriceSift v{PRICESIFT_VERSION}
          </p>
        </div>

        <div className="flex flex-wrap gap-x-4 gap-y-2">
          <Link href="/cameras" className="text-cyan-200 hover:text-cyan-100 [.pricesift-home_&]:text-ps-accent-hover [.pricesift-home_&]:hover:text-ps-text-primary [.pricesift-home_&]:hover:underline [.pricesift-results_&]:text-ps-accent-hover [.pricesift-results_&]:hover:text-ps-text-primary [.pricesift-results_&]:hover:underline">
            Cameras
          </Link>
          <Link href="/lenses" className="text-cyan-200 hover:text-cyan-100 [.pricesift-home_&]:text-ps-accent-hover [.pricesift-home_&]:hover:text-ps-text-primary [.pricesift-home_&]:hover:underline [.pricesift-results_&]:text-ps-accent-hover [.pricesift-results_&]:hover:text-ps-text-primary [.pricesift-results_&]:hover:underline">
            Lenses
          </Link>
          <Link href="/used" className="text-cyan-200 hover:text-cyan-100 [.pricesift-home_&]:text-ps-accent-hover [.pricesift-home_&]:hover:text-ps-text-primary [.pricesift-home_&]:hover:underline [.pricesift-results_&]:text-ps-accent-hover [.pricesift-results_&]:hover:text-ps-text-primary [.pricesift-results_&]:hover:underline">
            Used price guides
          </Link>
          <Link href="/reuse" className="text-emerald-200 hover:text-emerald-100 [.pricesift-home_&]:text-ps-success [.pricesift-home_&]:hover:text-ps-text-primary [.pricesift-home_&]:hover:underline [.pricesift-results_&]:text-ps-success [.pricesift-results_&]:hover:text-ps-text-primary [.pricesift-results_&]:hover:underline">
            Why buy used?
          </Link>
          <Link href="/feedback" className="text-cyan-200 hover:text-cyan-100 [.pricesift-home_&]:text-ps-accent-hover [.pricesift-home_&]:hover:text-ps-text-primary [.pricesift-home_&]:hover:underline [.pricesift-results_&]:text-ps-accent-hover [.pricesift-results_&]:hover:text-ps-text-primary [.pricesift-results_&]:hover:underline">
            Beta feedback
          </Link>
          <Link href="/disclosure" className="text-cyan-200 hover:text-cyan-100 [.pricesift-home_&]:text-ps-accent-hover [.pricesift-home_&]:hover:text-ps-text-primary [.pricesift-home_&]:hover:underline [.pricesift-results_&]:text-ps-accent-hover [.pricesift-results_&]:hover:text-ps-text-primary [.pricesift-results_&]:hover:underline">
            Affiliate disclosure
          </Link>
        </div>
      </div>
    </footer>
  );
}
