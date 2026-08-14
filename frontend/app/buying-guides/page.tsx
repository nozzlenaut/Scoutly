import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter } from "@/components/SiteFooter";
import { buyingGuides } from "@/lib/buyingGuides";

export const metadata: Metadata = {
  title: "Used Buying Guides & Listing Red Flags",
  description:
    "Practical PriceSift buying guides for cameras, lenses, GPUs, RAM, CPUs, game consoles, books, LEGO, and common used-listing red flags.",
  alternates: { canonical: "/buying-guides" },
  robots: { index: true, follow: true },
  openGraph: {
    title: "Used buying guides | PriceSift",
    description:
      "Practical checks for buying used cameras, lenses, PC parts, consoles, books, and LEGO without guessing what matters.",
    url: "/buying-guides",
  },
  twitter: {
    card: "summary",
    title: "Used buying guides | PriceSift",
    description:
      "Practical checks for buying used cameras, lenses, PC parts, consoles, books, and LEGO.",
  },
};

export default function BuyingGuidesPage() {
  return (
    <main className="pricesift-public min-h-screen bg-ps-canvas px-4 py-7 text-ps-text-primary sm:px-6 sm:py-10">
      <div className="mx-auto max-w-5xl">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <Link href="/" className="text-2xl font-black tracking-tight text-ps-text-primary">
            PriceSift
          </Link>
          <Link
            href="/#search"
            className="text-sm font-semibold text-ps-accent-hover hover:text-ps-text-primary hover:underline"
          >
            Search PriceSift
          </Link>
        </div>

        <div className="mx-auto max-w-3xl">
          <header className="mt-10 sm:mt-14">
            <p className="text-sm font-bold uppercase tracking-[0.18em] text-ps-accent-hover">
              Buying guides
            </p>
            <h1 className="mt-3 text-4xl font-black leading-tight tracking-tight sm:text-5xl">
              What actually matters when you buy used
            </h1>
            <p className="mt-5 text-lg leading-8 text-ps-text-secondary">
              A scratch is not the same thing as a broken part. A model name is not always specific enough. And “untested” still means untested. These guides focus on the checks that are actually useful before you buy.
            </p>
          </header>

          <Link
            href="/buying-guides/used-listing-red-flags"
            className="mt-9 block rounded-3xl border border-ps-border bg-ps-accent-soft p-6 transition hover:border-ps-border-strong"
          >
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-ps-accent-hover">Marketplace language decoder</p>
            <h2 className="mt-2 text-2xl font-black tracking-tight">Used listing red flags</h2>
            <p className="mt-3 text-base leading-7 text-ps-text-secondary">
              What “untested,” “powers on,” “as-is,” “for parts,” box-only, accessory-only, incomplete, stock-photo, and vague-model listings really tell you.
            </p>
            <span className="mt-4 inline-block text-sm font-bold text-ps-accent-hover underline decoration-ps-border-strong underline-offset-4">
              Read the red-flags guide →
            </span>
          </Link>

          <section className="mt-10 border-t border-ps-border">
            {buyingGuides.map((guide) => (
              <article key={guide.slug} className="border-b border-ps-border py-7 sm:py-8">
                <p className="text-xs font-bold uppercase tracking-[0.14em] text-ps-accent-hover">
                  {guide.categoryLabel}
                </p>
                <h2 className="mt-2 text-2xl font-black tracking-tight text-ps-text-primary">
                  <Link
                    href={`/buying-guides/${guide.slug}`}
                    className="hover:text-ps-accent-hover hover:underline"
                  >
                    {guide.title}
                  </Link>
                </h2>
                <p className="mt-3 text-base leading-7 text-ps-text-secondary">
                  {guide.description}
                </p>
                <Link
                  href={`/buying-guides/${guide.slug}`}
                  className="mt-3 inline-block text-sm font-bold text-ps-accent-hover underline decoration-ps-border-strong underline-offset-4 hover:text-ps-text-primary"
                >
                  Read the guide →
                </Link>
              </article>
            ))}
          </section>

          <section className="mt-12 grid gap-4 sm:grid-cols-2">
            <Link href="/used" className="rounded-2xl border border-ps-border bg-ps-surface p-5 hover:border-ps-border-strong hover:bg-ps-accent-soft">
              <p className="text-xs font-bold uppercase tracking-[0.14em] text-ps-accent-hover">Exact models</p>
              <h2 className="mt-2 text-xl font-black">Curated used price guides</h2>
              <p className="mt-2 text-sm leading-6 text-ps-text-secondary">Current filtered listings, price context, and model-specific checks for manually approved products.</p>
            </Link>
            <Link href="/used/market" className="rounded-2xl border border-ps-border bg-ps-surface p-5 hover:border-ps-border-strong hover:bg-ps-accent-soft">
              <p className="text-xs font-bold uppercase tracking-[0.14em] text-ps-success">PriceSift data</p>
              <h2 className="mt-2 text-xl font-black">Used market snapshot</h2>
              <p className="mt-2 text-sm leading-6 text-ps-text-secondary">A small data-driven view of current prices and recent PriceSift price history.</p>
            </Link>
          </section>

          <section className="mt-12 border-t border-emerald-200 pt-8">
            <p className="text-sm font-bold uppercase tracking-[0.16em] text-emerald-800">
              Before you replace it
            </p>
            <h2 className="mt-2 text-2xl font-black tracking-tight">Repair &amp; Reuse</h2>
            <p className="mt-3 text-base leading-7 text-ps-text-secondary">
              Sometimes the best used purchase is no purchase. If the thing you already own might be repairable, start with the model, the manual, good repair information, and a realistic safety check.
            </p>
            <Link
              href="/reuse"
              className="mt-4 inline-block font-bold text-emerald-900 underline decoration-emerald-300 underline-offset-4 hover:text-emerald-700"
            >
              Repair before you replace →
            </Link>
          </section>
        </div>

        <SiteFooter />
      </div>
    </main>
  );
}
