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
    <main className="pricesift-public min-h-screen px-4 py-8 text-ps-text-primary sm:px-6 sm:py-10">
      <div className="mx-auto max-w-[1500px]">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <Link href="/" className="text-2xl font-black tracking-tight text-ps-text-primary">PriceSift</Link>
          <Link href="/#search" className="text-sm font-semibold text-ps-accent-hover hover:text-ps-text-primary hover:underline">All categories</Link>
        </div>

        <div className="mt-8">
          <p className="text-sm uppercase tracking-[0.25em] text-ps-accent-hover">Photography beta</p>
          <h1 className="mt-2 text-4xl font-black sm:text-5xl">Find used lenses currently at KEH</h1>
          <p className="mt-4 max-w-4xl text-base leading-7 text-ps-text-secondary">
            Browse structured KEH inventory by the details that define compatibility. Public lens results are KEH-only for now;
            eBay lens listings remain disabled while PriceSift privately tests their inconsistent titles, mounts, and accessory listings.
          </p>
        </div>

        {initialData ? (
          <PublicKehLensFinder initialData={initialData} />
        ) : (
          <div className="mt-8 rounded-3xl border border-ps-warning/40 bg-amber-50 p-7 text-ps-text-primary" role="status">
            <h2 className="text-2xl font-black">KEH lens inventory is unavailable right now.</h2>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-ps-text-secondary">
              The public KEH feed may be syncing or temporarily disabled. Camera and other PriceSift categories remain available.
            </p>
            <Link href="/#search" className="mt-5 inline-flex rounded-2xl bg-ps-accent-strong px-5 py-3 font-bold text-white hover:bg-ps-accent-hover">Return to search</Link>
          </div>
        )}

        <SiteFooter />
      </div>
    </main>
  );
}
