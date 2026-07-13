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
          Now testing consoles
        </div>
        <h1 className="text-5xl font-black tracking-tight text-white sm:text-7xl">PriceSift</h1>
        <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300">
          Find the best price for what you already want. Pick an active category, choose the exact item, and PriceSift checks eBay for cleaner used listings — complete items first, not broken listings, boxes-only, parts-only junk, or sketchy matches when we can catch them.
        </p>

        <div className="mt-6 max-w-3xl rounded-3xl border border-white/10 bg-white/[0.06] p-5 text-left text-sm leading-6 text-slate-300">
          <p>
            PriceSift is supported by affiliate links. If you do not want to use those, that is totally fine: use PriceSift to find the right item, then open eBay separately or in a private/incognito window and search normally.
          </p>
        </div>

        <div className="relative z-50 mt-8 w-full">
          <SearchForm />
        </div>

        <div className="relative z-0 mt-10 grid w-full gap-4 text-left sm:grid-cols-3">
          {["Exact-item autocomplete", "Built for used prices", "Multiple safe options while testing"].map((item) => (
            <div key={item} className="rounded-2xl border border-white/10 bg-white/[0.06] p-4 text-sm text-slate-300">
              {item}
            </div>
          ))}
        </div>

        <div className="relative z-0 mt-6 w-full">
          <CategoryStatusPanel />
        </div>
      </section>
      <SiteFooter />
    </main>
  );
}
