
import type { Metadata } from "next";
import Link from "next/link";
import { GoodreadsImportTool } from "@/components/GoodreadsImportTool";
import { SiteFooter } from "@/components/SiteFooter";

export const metadata: Metadata = {
  title: "Goodreads List Price Search",
  description:
    "Upload a Goodreads library export and find clean used prices for every exact physical ISBN.",
  alternates: { canonical: "/books/goodreads" },
  openGraph: {
    title: "Price your Goodreads list | PriceSift",
    description:
      "Upload a Goodreads export and search every exact physical edition at once.",
    url: "/books/goodreads",
  },
};

export default function GoodreadsImportPage() {
  return (
    <main className="min-h-screen bg-slate-950 px-4 py-8 text-white sm:px-6 sm:py-10">
      <div className="mx-auto max-w-7xl">
        <div className="flex items-center justify-between gap-4">
          <Link href="/" className="text-2xl font-black tracking-tight text-white">
            PriceSift
          </Link>
          <div className="flex items-center gap-4 text-sm">
            <Link
              href="/search?category=books"
              className="text-cyan-200 hover:text-cyan-100"
            >
              Search one ISBN
            </Link>
            <Link href="/" className="text-slate-400 hover:text-white">
              Home
            </Link>
          </div>
        </div>

        <GoodreadsImportTool />
        <SiteFooter />
      </div>
    </main>
  );
}
