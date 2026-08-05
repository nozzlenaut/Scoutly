import type { Metadata } from "next";
import { SearchForm } from "@/components/SearchForm";
import { SiteFooter } from "@/components/SiteFooter";

export const metadata: Metadata = {
  alternates: { canonical: "/" },
};

export default function HomePage() {
  return (
    <main className="pricesift-home min-h-screen overflow-x-hidden bg-ps-canvas px-5 py-8 text-ps-text-primary sm:px-6 sm:py-10">
      <section className="mx-auto flex min-h-[78vh] max-w-5xl flex-col items-center justify-center text-center">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-ps-success">
          Buy used. Keep good products in use.
        </p>

        <h1 className="mt-4 text-5xl font-black tracking-tight sm:text-7xl">
          PriceSift
        </h1>

        <p className="mt-5 max-w-3xl text-xl font-semibold leading-8 text-ps-text-primary sm:text-2xl">
          Find the exact used item you want without sorting through bad listings.
        </p>

        <p className="mt-3 max-w-2xl text-sm leading-6 text-ps-text-secondary sm:text-base">
          Choose a category and search a supported product. PriceSift filters
          common wrong models, broken items, empty boxes, accessories, and
          misleading listings, then shows up to three cleaner options.
        </p>

        <div
          id="search"
          className="relative z-50 mt-9 w-full scroll-mt-6"
        >
          <SearchForm bare theme="light" />
        </div>

        <p className="mt-5 text-sm text-ps-neutral">
          Free to use · No account required · Fewer results on purpose
        </p>
      </section>

      <SiteFooter />
    </main>
  );
}
