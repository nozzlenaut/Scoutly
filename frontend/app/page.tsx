import type { Metadata } from "next";
import { SearchForm } from "@/components/SearchForm";
import { SiteFooter } from "@/components/SiteFooter";

export const metadata: Metadata = {
  alternates: { canonical: "/" },
};

export default function HomePage() {
  return (
    <main className="min-h-screen overflow-x-hidden bg-[radial-gradient(circle_at_top,_#164e63,_#050816_45%)] px-5 py-8 text-white sm:px-6 sm:py-10">
      <section className="mx-auto flex min-h-[78vh] max-w-5xl flex-col items-center justify-center text-center">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-200">
          Buy used. Keep good products in use.
        </p>

        <h1 className="mt-4 text-5xl font-black tracking-tight sm:text-7xl">
          PriceSift
        </h1>

        <p className="mt-5 max-w-3xl text-xl font-semibold leading-8 text-white sm:text-2xl">
          Find the exact used item you want without sorting through bad listings.
        </p>

        <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300 sm:text-base">
          Choose a category and search a supported product. PriceSift filters
          common wrong models, broken items, empty boxes, accessories, and
          misleading listings, then shows up to three cleaner options.
        </p>

        <div
          id="search"
          className="relative z-50 mt-9 w-full scroll-mt-6 [&>div]:!max-w-4xl [&>div]:!rounded-none [&>div]:!border-0 [&>div]:!bg-transparent [&>div]:!p-0 [&>div]:!shadow-none [&>div]:!backdrop-blur-none"
        >
          <SearchForm />
        </div>

        <p className="mt-5 text-sm text-slate-400">
          Free to use · No account required · Fewer results on purpose
        </p>
      </section>

      <SiteFooter />
    </main>
  );
}
