import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter } from "@/components/SiteFooter";

export const metadata: Metadata = {
  title: "Why buy used?",
  description:
    "PriceSift makes secondhand shopping easier by filtering out broken, incomplete, and misleading listings.",
  alternates: { canonical: "/reuse" },
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
    <main className="min-h-screen overflow-x-hidden bg-[radial-gradient(circle_at_top,_#14532d,_#050a08_45%)] px-6 py-10 text-white">
      <section className="mx-auto max-w-4xl">
        <Link href="/" className="text-sm text-cyan-200 hover:text-cyan-100">
          ← Back to PriceSift
        </Link>

        <div className="mt-8 rounded-3xl border border-white/10 bg-white/[0.05] p-8 shadow-2xl shadow-black/20 sm:p-10">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-emerald-300">
            Reduce. Reuse. Search better.
          </p>
          <h1 className="mt-4 max-w-3xl text-4xl font-black tracking-tight sm:text-6xl">
            Buying used should be the easy choice.
          </h1>
          <p className="mt-6 max-w-3xl text-lg leading-8 text-slate-300">
            Plenty of useful products are already out there, ready for another
            owner. The hard part is finding the right one without sorting through
            broken items, incomplete listings, accessories, empty boxes, and
            misleading matches.
          </p>
          <p className="mt-5 max-w-3xl text-lg leading-8 text-slate-300">
            PriceSift is a free search tool built to make that process simpler.
            Tell it what you already want, and it filters marketplace results to
            surface a few cleaner secondhand options.
          </p>

          <div className="mt-10 grid gap-4 md:grid-cols-3">
            {problems.map((problem) => (
              <article
                key={problem.title}
                className="rounded-2xl border border-white/10 bg-slate-950/35 p-5"
              >
                <h2 className="font-bold text-white">{problem.title}</h2>
                <p className="mt-2 text-sm leading-6 text-slate-400">
                  {problem.description}
                </p>
              </article>
            ))}
          </div>

          <div className="mt-10 rounded-2xl border border-emerald-300/20 bg-emerald-300/[0.07] p-6">
            <h2 className="text-2xl font-bold">Keep good products in use longer</h2>
            <p className="mt-3 leading-7 text-slate-300">
              Buying less is still the simplest way to reduce waste. But when you
              do need something, choosing a solid used item can extend the useful
              life of a product that already exists—and make a new purchase
              unnecessary.
            </p>
            <p className="mt-3 leading-7 text-slate-300">
              PriceSift does not claim to calculate the environmental impact of
              each purchase. It simply tries to remove some of the friction that
              pushes people away from buying secondhand in the first place.
            </p>
          </div>

          <div className="mt-10 flex flex-col gap-3 sm:flex-row sm:items-center">
            <Link
              href="/"
              className="inline-flex justify-center rounded-xl bg-cyan-300 px-5 py-3 font-bold text-slate-950 transition hover:bg-cyan-200"
            >
              Search PriceSift
            </Link>
            <Link
              href="/disclosure"
              className="inline-flex justify-center rounded-xl border border-white/10 px-5 py-3 font-medium text-cyan-200 transition hover:border-white/20 hover:text-cyan-100"
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
