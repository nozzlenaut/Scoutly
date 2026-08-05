
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
    <main className="pricesift-public min-h-screen px-4 py-8 text-ps-text-primary sm:px-6 sm:py-10">
      <div className="mx-auto max-w-7xl">
        <div className="flex items-center justify-between gap-4">
          <Link href="/" className="text-2xl font-black tracking-tight text-ps-text-primary">
            PriceSift
          </Link>
          <div className="flex items-center gap-4 text-sm">
            <Link
              href="/search?category=books"
              className="text-ps-accent-hover hover:text-ps-text-primary hover:underline"
            >
              Search one ISBN
            </Link>
            <Link href="/" className="text-ps-text-secondary hover:text-ps-text-primary hover:underline">
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
