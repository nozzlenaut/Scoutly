import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter } from "@/components/SiteFooter";

export const metadata: Metadata = {
  title: "Why buy used?",
  description:
    "PriceSift makes buying secondhand easier and helps people keep useful products working longer.",
  alternates: { canonical: "/reuse" },
  robots: { index: true, follow: true },
  openGraph: {
    title: "Buy used. Keep it working. Keep it in use.",
    description:
      "Make secondhand shopping easier, find the right product, and keep useful things working longer.",
    url: "/reuse",
  },
};

const problems = [
  {
    title: "The wrong item",
    description:
      "Similar models, accessories, empty boxes, and unrelated parts can crowd out the product you actually searched for.",
  },
  {
    title: "The wrong condition",
    description:
      "Broken, for-parts, incomplete, and suspicious listings can make buying used feel riskier than it needs to be.",
  },
  {
    title: "Too much digging",
    description:
      "A good secondhand option may be buried under pages of noise, even when you already know exactly what you want.",
  },
];

export default function ReusePage() {
  return (
    <main className="pricesift-public min-h-screen overflow-x-hidden px-6 py-10 text-ps-text-primary">
      <section className="mx-auto max-w-4xl">
        <Link href="/" className="text-sm text-ps-accent-hover hover:text-ps-text-primary hover:underline">
          ← Back to PriceSift
        </Link>

        <div className="mt-8 rounded-3xl border border-ps-border bg-ps-surface p-8 shadow-xl shadow-ps-border/30 sm:p-10">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-ps-success">
            Reduce. Reuse. Search better.
          </p>
          <h1 className="mt-4 max-w-3xl text-4xl font-black tracking-tight sm:text-6xl">
            Buy used. Keep it working. Keep it in use.
          </h1>
          <p className="mt-6 max-w-3xl text-lg leading-8 text-ps-text-secondary">
            Plenty of useful products are already out there, ready for another
            owner. The hard part is finding the right one without sorting through
            broken items, incomplete listings, accessories, empty boxes, and
            misleading matches.
          </p>
          <p className="mt-5 max-w-3xl text-lg leading-8 text-ps-text-secondary">
            PriceSift is a free search tool built to make that process simpler.
            Tell it what you already want, and it filters marketplace results to
            surface a few cleaner secondhand options.
          </p>

          <div className="mt-10 grid gap-4 md:grid-cols-3">
            {problems.map((problem) => (
              <article
                key={problem.title}
                className="rounded-2xl border border-ps-border bg-ps-control p-5"
              >
                <h2 className="font-bold text-ps-text-primary">{problem.title}</h2>
                <p className="mt-2 text-sm leading-6 text-ps-text-secondary">
                  {problem.description}
                </p>
              </article>
            ))}
          </div>

          <div className="mt-10 rounded-2xl border border-ps-success/40 bg-emerald-50 p-6">
            <h2 className="text-2xl font-bold">Keep good products in use longer</h2>
            <p className="mt-3 leading-7 text-ps-text-secondary">
              Buying less is still the simplest way to reduce waste. But when you
              do need something, choosing a solid used item can extend the useful
              life of a product that already exists—and make a new purchase
              unnecessary.
            </p>
            <p className="mt-3 leading-7 text-ps-text-secondary">
              Buying used is only part of the job. For recognized products,
              PriceSift also points owners toward official manuals or support
              resources, with a ManualsLib search when an exact maintained link is
              not available. A missing instruction booklet should not be the
              reason a working product gets replaced.
            </p>
            <p className="mt-3 leading-7 text-ps-text-secondary">
              PriceSift does not claim to calculate the environmental impact of
              each purchase. It simply tries to remove some of the friction that
              pushes people away from buying secondhand—or from keeping something
              they already own.
            </p>
          </div>

          <div className="mt-10 flex flex-col gap-3 sm:flex-row sm:items-center">
            <Link
              href="/"
              className="inline-flex justify-center rounded-xl bg-ps-accent-strong px-5 py-3 font-bold text-white transition hover:bg-ps-accent-hover"
            >
              Search PriceSift
            </Link>
            <Link
              href="/used"
              className="inline-flex justify-center rounded-xl border border-ps-success/40 px-5 py-3 font-medium text-ps-success transition hover:bg-emerald-50"
            >
              Browse used price guides
            </Link>
            <Link
              href="/disclosure"
              className="inline-flex justify-center rounded-xl border border-ps-border px-5 py-3 font-medium text-ps-accent-hover transition hover:border-ps-border-strong hover:text-ps-text-primary"
            >
              Read the affiliate disclosure
            </Link>
          </div>
        </div>
      </section>

      <SiteFooter />
    </main>
  );
}
