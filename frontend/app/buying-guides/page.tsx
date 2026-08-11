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
    <main className="pricesift-public min-h-screen bg-ps-canvas px-4 py-8 text-ps-text-primary sm:px-6 sm:py-10">
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

        <header className="mt-8 rounded-[2rem] border border-ps-border bg-ps-surface p-7 shadow-xl shadow-slate-900/5 sm:p-10">
          <p className="text-sm font-bold uppercase tracking-[0.22em] text-ps-accent-hover">
            Buying guides
          </p>
          <h1 className="mt-4 max-w-4xl text-4xl font-black tracking-tight sm:text-6xl">
            What actually matters when you buy used
          </h1>
          <p className="mt-6 max-w-3xl text-lg leading-8 text-ps-text-secondary">
            A scratch is not the same thing as a broken part. A model name is not always specific enough. And “untested” still means untested. These guides focus on the checks that are actually useful before you buy.
          </p>
        </header>

        <section className="mt-8 grid gap-5 md:grid-cols-2">
          {buyingGuides.map((guide) => (
            <Link
              key={guide.slug}
              href={`/buying-guides/${guide.slug}`}
              className="rounded-3xl border border-ps-border bg-ps-surface p-6 shadow-sm shadow-slate-900/5 transition hover:border-ps-border-strong hover:bg-ps-accent-soft"
            >
              <p className="text-xs font-bold uppercase tracking-[0.16em] text-ps-accent-hover">
                {guide.categoryLabel}
              </p>
              <h2 className="mt-2 text-2xl font-black tracking-tight text-ps-text-primary">
                {guide.title}
              </h2>
              <p className="mt-3 text-sm leading-6 text-ps-text-secondary">
                {guide.description}
              </p>
              <p className="mt-5 text-sm font-bold text-ps-accent-hover">Read the guide →</p>
            </Link>
          ))}
        </section>

        <section className="mt-8 rounded-3xl border border-emerald-200 bg-emerald-50 p-6 sm:p-8">
          <p className="text-sm font-bold uppercase tracking-[0.18em] text-emerald-800">
            Before you replace it
          </p>
          <h2 className="mt-2 text-2xl font-black tracking-tight">Repair &amp; Reuse</h2>
          <p className="mt-3 max-w-3xl leading-7 text-ps-text-secondary">
            Sometimes the best used purchase is no purchase. If the thing you already own might be repairable, start with the model, the manual, good repair information, and a realistic safety check.
          </p>
          <Link
            href="/reuse"
            className="mt-5 inline-flex min-h-11 items-center rounded-2xl border border-emerald-300 bg-white px-5 py-3 font-bold text-emerald-900 transition hover:bg-emerald-100"
          >
            Repair before you replace
          </Link>
        </section>

        <SiteFooter />
      </div>
    </main>
  );
}
