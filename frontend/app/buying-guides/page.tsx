import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter } from "@/components/SiteFooter";
import { buyingGuides } from "@/lib/buyingGuides";

export const metadata: Metadata = {
  title: "Used buying guides",
  description:
    "Practical PriceSift buying guides for cameras, lenses, GPUs, RAM, CPUs, game consoles, books, and LEGO.",
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
