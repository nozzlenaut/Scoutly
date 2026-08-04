import type { Metadata } from "next";
import { CategoryStatusPanel } from "@/components/CategoryStatusPanel";
import { SearchForm } from "@/components/SearchForm";
import { SiteFooter } from "@/components/SiteFooter";

export const metadata: Metadata = {
  alternates: { canonical: "/" },
};

export default function HomePage() {
  return (
    <main className="min-h-screen overflow-x-hidden bg-[radial-gradient(circle_at_top,_#164e63,_#050816_45%)] px-6 py-10">
      <section className="mx-auto flex min-h-[80vh] max-w-5xl flex-col items-center justify-center text-center">
        <div className="mb-5 rounded-full border border-emerald-300/30 bg-emerald-300/10 px-4 py-2 text-sm font-medium text-emerald-100">
          Buy used. Keep good products in use.
        </div>
        <h1 className="text-5xl font-black tracking-tight text-white sm:text-7xl">
          PriceSift
        </h1>
        <p className="mt-5 max-w-3xl text-xl font-semibold leading-8 text-white sm:text-2xl">
          Find the exact used item you want—without sorting through bad listings.
        </p>
        <p className="mt-4 max-w-2xl text-base leading-7 text-slate-300 sm:text-lg sm:leading-8">
          PriceSift filters out broken items, empty boxes, accessories,
          parts-only listings, wrong models, and misleading variations, then
          shows up to three cleaner options for the exact product you chose.
          Fewer results on purpose, so choosing secondhand feels easier.
        </p>
        <p className="mt-3 text-sm font-medium text-slate-400">
          Public beta · Free to use · No account required
        </p>

        <a
          href="/reuse"
          className="mt-5 inline-flex rounded-full border border-emerald-300/30 bg-emerald-300/10 px-4 py-2 text-sm font-semibold text-emerald-100 transition hover:bg-emerald-300/15"
        >
          Why reuse is built into PriceSift →
        </a>

        <div className="mt-6 max-w-3xl rounded-3xl border border-white/10 bg-white/[0.06] p-5 text-left text-sm leading-6 text-slate-300">
          <p>
            PriceSift is free to use and supported by affiliate links at no
            extra cost to you. Prefer not to use them? You can still use
            PriceSift to identify the right item, then search for it directly
            on the marketplace.{" "}
            <a
              href="/disclosure"
              className="font-semibold text-cyan-200 underline decoration-cyan-200/40 underline-offset-4 transition hover:text-cyan-100"
            >
              Learn how affiliate links work.
            </a>
          </p>
        </div>

        <div id="search" className="relative z-50 mt-8 w-full scroll-mt-6">
          <SearchForm />
        </div>

        <section className="relative z-0 mt-6 w-full rounded-3xl border border-amber-200/20 bg-amber-200/[0.08] p-5 text-left sm:p-6">
          <p className="text-sm font-bold uppercase tracking-[0.2em] text-amber-200">
            New for Books
          </p>
          <div className="mt-2 flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 className="text-2xl font-black text-white">
                Price your Goodreads list
              </h2>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-300">
                Upload a Goodreads library export and search every exact
                physical ISBN at once. Find the right used edition and keep
                another copy in circulation. PriceSift never silently
                substitutes a different edition.
              </p>
            </div>
            <a
              href="/books/goodreads"
              className="shrink-0 rounded-2xl bg-amber-100 px-5 py-3 text-center font-bold text-slate-950 transition hover:bg-white"
            >
              Import Goodreads CSV →
            </a>
          </div>
        </section>

        <div className="relative z-0 mt-10 grid w-full gap-4 text-left sm:grid-cols-3">
          {[
            "Exact item, fewer wrong matches",
            "Built around secondhand first",
            "Up to three options, on purpose",
          ].map((item) => (
            <div
              key={item}
              className="rounded-2xl border border-white/10 bg-white/[0.06] p-4 text-sm font-medium text-slate-300"
            >
              {item}
            </div>
          ))}
        </div>

        <section className="relative z-0 mt-8 w-full rounded-3xl border border-cyan-200/20 bg-cyan-200/10 p-6 text-left">
          <p className="text-sm font-bold uppercase tracking-[0.2em] text-cyan-200">
            Help make buying used easier
          </p>
          <h2 className="mt-2 text-2xl font-black text-white">
            Test a real product search
          </h2>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-200">
            Search for something you already know, check whether PriceSift found
            complete and usable items, and report anything wrong, incomplete,
            broken, or unrelated. Better filtering means less friction between
            people and the good products already out there.
          </p>
          <div className="mt-5 flex flex-wrap gap-3">
            <a
              href="#search"
              className="rounded-2xl bg-white px-5 py-3 font-bold text-slate-950 transition hover:bg-slate-200"
            >
              Start testing
            </a>
            <a
              href="/feedback"
              className="rounded-2xl border border-white/20 bg-white/[0.06] px-5 py-3 font-bold text-white transition hover:bg-white/[0.1]"
            >
              Send beta feedback
            </a>
          </div>
        </section>

        <div className="relative z-0 mt-6 w-full">
          <CategoryStatusPanel />
        </div>
      </section>
      <SiteFooter />
    </main>
  );
}
