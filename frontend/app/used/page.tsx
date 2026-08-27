import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter } from "@/components/SiteFooter";
import { allIndexedProducts } from "@/lib/allIndexedProducts";

export const metadata: Metadata = {
  title: "Used Product Price Guides & Buying Checks",
  description: "Cleaner current used listings, recent price context, and buying guidance for exact cameras, consoles, graphics cards, LEGO sets, and selected popular books.",
  alternates: { canonical: "/used" },
  robots: { index: true, follow: true },
};

export default function UsedProductGuidesPage() {
  return (
    <main className="pricesift-public min-h-screen px-6 py-10 text-ps-text-primary">
      <div className="mx-auto max-w-6xl">
        <Link href="/" className="text-sm text-ps-accent-hover hover:text-ps-text-primary hover:underline">← PriceSift</Link>
        <section className="mt-8 rounded-[2rem] border border-ps-border bg-ps-surface p-7 sm:p-10">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-ps-accent-hover">Curated exact products</p>
          <h1 className="mt-3 text-4xl font-black tracking-tight sm:text-5xl">Used product price guides</h1>
          <p className="mt-5 max-w-3xl text-lg leading-8 text-ps-text-secondary">
            Each page uses PriceSift’s normal exact-item matching and listing filters, then adds recent price context, common listing traps, and model-specific used-buying checks. These are manually approved products, not thousands of thin pages generated from random searches.
          </p>

          <div className="mt-7 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Link href="/used/retro-game-consoles" className="rounded-2xl border border-ps-border bg-ps-accent-soft p-5 transition hover:border-ps-border-strong">
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-ps-accent-hover">Console hub</p>
              <h2 className="mt-2 text-xl font-black">Retro & previous-generation consoles</h2>
              <p className="mt-2 text-sm leading-6 text-ps-text-secondary">Older PlayStation, Xbox, and Nintendo systems, kept separate from current generation hardware.</p>
            </Link>
            <Link href="/used/current-game-consoles" className="rounded-2xl border border-ps-border bg-ps-accent-soft p-5 transition hover:border-ps-border-strong">
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-ps-accent-hover">Console hub</p>
              <h2 className="mt-2 text-xl font-black">Current-generation consoles</h2>
              <p className="mt-2 text-sm leading-6 text-ps-text-secondary">PS5-family, Xbox Series, and Switch 2 price-guide pages in one place.</p>
            </Link>
            <Link href="/used/popular-books" className="rounded-2xl border border-ps-border bg-ps-accent-soft p-5 transition hover:border-ps-border-strong">
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-ps-accent-hover">Book hub</p>
              <h2 className="mt-2 text-xl font-black">Popular used books</h2>
              <p className="mt-2 text-sm leading-6 text-ps-text-secondary">A rotating set of popular titles with permanent exact-edition pages.</p>
            </Link>
          </div>

          <div className="mt-5 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Link
              href="/used/noise"
              className="rounded-2xl border border-ps-success/40 bg-emerald-50 p-5 transition hover:border-ps-success"
            >
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-ps-success">PriceSift filtering data</p>
              <h2 className="mt-2 text-xl font-black">Used Marketplace Noise Index</h2>
              <p className="mt-2 text-sm leading-6 text-ps-text-secondary">
                See how many marketplace candidates PriceSift filters as wrong models, broken items, accessories, risky listings, and other low-confidence matches.
              </p>
            </Link>
            <Link
              href="/used/market"
              className="rounded-2xl border border-ps-success/40 bg-emerald-50 p-5 transition hover:border-ps-success"
            >
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-ps-success">PriceSift data</p>
              <h2 className="mt-2 text-xl font-black">Used Market Index</h2>
              <p className="mt-2 text-sm leading-6 text-ps-text-secondary">
                Compare smoothed model baselines with current PriceSift price history and see which markets are moving.
              </p>
            </Link>
            <Link
              href="/buying-guides/used-listing-red-flags"
              className="rounded-2xl border border-ps-border bg-ps-accent-soft p-5 transition hover:border-ps-border-strong"
            >
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-ps-accent-hover">Before you click buy</p>
              <h2 className="mt-2 text-xl font-black">Used listing red flags</h2>
              <p className="mt-2 text-sm leading-6 text-ps-text-secondary">
                Decode “untested,” “powers on,” “as-is,” parts-only, box-only, incomplete, and other marketplace traps.
              </p>
            </Link>
          </div>

          <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {allIndexedProducts.map((product) => (
              <Link
                key={product.slug}
                href={`/used/${product.slug}`}
                className="rounded-2xl border border-ps-border bg-ps-control p-5 transition hover:border-ps-border-strong hover:bg-ps-accent-soft"
              >
                <p className="text-xs uppercase tracking-[0.18em] text-ps-neutral">{product.category}</p>
                <h2 className="mt-2 text-xl font-bold">{product.title}</h2>
                <p className="mt-3 text-sm leading-6 text-ps-text-secondary">{product.description}</p>
              </Link>
            ))}
          </div>
          <div className="mt-8 rounded-2xl border border-ps-success/40 bg-emerald-50 p-5">
            <h2 className="text-xl font-bold">Why used?</h2>
            <p className="mt-2 text-sm leading-6 text-ps-text-secondary">Keeping a solid product in use longer can be cheaper and avoid an unnecessary new purchase.</p>
            <Link href="/reuse" className="mt-3 inline-flex text-sm font-semibold text-ps-success hover:text-ps-text-primary hover:underline">Read PriceSift’s reuse mission →</Link>
          </div>
        </section>
        <SiteFooter />
      </div>
    </main>
  );
}
