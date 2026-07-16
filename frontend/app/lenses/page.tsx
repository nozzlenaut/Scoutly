import type { Metadata } from "next";
import Link from "next/link";
import { PublicKehLensFinder } from "@/components/PublicKehLensFinder";
import { SiteFooter } from "@/components/SiteFooter";
import { getPublicKehLensBuilder, type KehLensBuilderResponse } from "@/lib/api";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Used camera lenses at KEH",
  description: "Find currently available used KEH lenses by mount, prime or zoom type, focal range, and optional brand.",
  alternates: { canonical: "/lenses" },
};

export default async function PublicLensesPage() {
  let initialData: KehLensBuilderResponse | null = null;
  try {
    initialData = await getPublicKehLensBuilder({ limit: 1 });
  } catch {
    initialData = null;
  }

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-8 text-white sm:px-6 sm:py-10">
      <div className="mx-auto max-w-[1500px]">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <Link href="/" className="text-2xl font-black tracking-tight text-white">PriceSift</Link>
          <Link href="/#search" className="text-sm font-semibold text-cyan-200 hover:text-cyan-100">All categories</Link>
        </div>

        <div className="mt-8">
          <p className="text-sm uppercase tracking-[0.25em] text-cyan-200">Photography beta</p>
          <h1 className="mt-2 text-4xl font-black sm:text-5xl">Find used lenses currently at KEH</h1>
          <p className="mt-4 max-w-4xl text-base leading-7 text-slate-300">
            Browse structured KEH inventory by the details that define compatibility. Public lens results are KEH-only for now;
            eBay lens listings remain disabled while PriceSift privately tests their inconsistent titles, mounts, and accessory listings.
          </p>
        </div>

        {initialData ? (
          <PublicKehLensFinder initialData={initialData} />
        ) : (
          <div className="mt-8 rounded-3xl border border-amber-300/20 bg-amber-300/10 p-7 text-amber-50" role="status">
            <h2 className="text-2xl font-black">KEH lens inventory is unavailable right now.</h2>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-amber-100/90">
              The public KEH feed may be syncing or temporarily disabled. Camera and other PriceSift categories remain available.
            </p>
            <Link href="/#search" className="mt-5 inline-flex rounded-2xl bg-white px-5 py-3 font-bold text-slate-950">Return to search</Link>
          </div>
        )}

        <SiteFooter />
      </div>
    </main>
  );
}
