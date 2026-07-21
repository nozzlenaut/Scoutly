import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="mx-auto mt-12 max-w-5xl border-t border-white/10 px-2 py-6 text-sm text-slate-500">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <p>
          PriceSift may earn from qualifying purchases through affiliate links. As an Amazon Associate I earn from qualifying purchases.
        </p>
        <div className="flex gap-4">
          <Link href="/cameras" className="text-cyan-200 hover:text-cyan-100">Cameras</Link>
          <Link href="/lenses" className="text-cyan-200 hover:text-cyan-100">Lenses</Link>
          <Link href="/feedback" className="text-cyan-200 hover:text-cyan-100">Beta feedback</Link>
          <Link href="/disclosure" className="text-cyan-200 hover:text-cyan-100">Affiliate disclosure</Link>
        </div>
      </div>
    </footer>
  );
}
