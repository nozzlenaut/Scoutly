import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter } from "@/components/SiteFooter";
import { getIndexedProduct } from "@/lib/indexedProducts";
import { getIndexedSearchResults } from "@/lib/indexedSearch";

export const revalidate = 21600;

export const metadata: Metadata = {
  title: "Used Market Snapshot: Current Prices & 30-Day Context",
  description:
    "A small PriceSift snapshot of current filtered used prices, 30-day price context, and safe-inventory availability for selected cameras, consoles, GPUs, and LEGO.",
  alternates: { canonical: "/used/market" },
  robots: { index: true, follow: true },
  openGraph: {
    title: "PriceSift Used Market Snapshot",
    description:
      "Current filtered used prices and recent price context from PriceSift’s manually approved product pages.",
    url: "/used/market",
    type: "website",
  },
};

const marketSlugs = [
  "sony-a7-iii",
  "playstation-5",
  "nintendo-switch-2",
  "nvidia-rtx-3070",
  "lego-75192-millennium-falcon",
];

function money(value?: number | null): string {
  if (value === null || value === undefined) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

function comparison(value?: number | null): string {
  if (value === null || value === undefined) return "Not enough history yet";
  if (Math.abs(value) < 0.5) return "About even with the 30-day median";
  return `${Math.abs(value).toFixed(1)}% ${value < 0 ? "below" : "above"} the 30-day median`;
}

export default async function UsedMarketPage() {
  const products = marketSlugs
    .map((slug) => getIndexedProduct(slug))
    .filter((product) => product !== undefined);
  const snapshots = await Promise.all(
    products.map(async (product) => ({
      product,
      data: await getIndexedSearchResults(product.query, product.category),
    })),
  );
  const checkedAt = new Date();
  const pageUrl = "https://www.pricesift.app/used/market";
  const structuredData = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "CollectionPage",
        "@id": pageUrl,
        name: "PriceSift Used Market Snapshot",
        description:
          "Current filtered used prices and recent price context for a small set of manually approved PriceSift products.",
        url: pageUrl,
      },
      {
        "@type": "BreadcrumbList",
        itemListElement: [
          { "@type": "ListItem", position: 1, name: "PriceSift", item: "https://www.pricesift.app/" },
          { "@type": "ListItem", position: 2, name: "Used price guides", item: "https://www.pricesift.app/used" },
          { "@type": "ListItem", position: 3, name: "Used market snapshot", item: pageUrl },
        ],
      },
    ],
  };

  return (
    <main className="pricesift-public min-h-screen px-4 py-8 text-ps-text-primary sm:px-6 sm:py-10">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(structuredData).replace(/</g, "\\u003c"),
        }}
      />
      <div className="mx-auto max-w-6xl">
        <nav aria-label="Breadcrumb" className="text-sm text-ps-text-secondary">
          <ol className="flex flex-wrap items-center gap-2">
            <li><Link href="/" className="hover:underline">Home</Link></li>
            <li aria-hidden="true">/</li>
            <li><Link href="/used" className="hover:underline">Used price guides</Link></li>
            <li aria-hidden="true">/</li>
            <li aria-current="page" className="font-semibold text-ps-text-primary">Used market snapshot</li>
          </ol>
        </nav>

        <header className="mt-8 rounded-[2rem] border border-ps-border bg-ps-surface p-7 sm:p-10">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-ps-accent-hover">
            PriceSift data
          </p>
          <h1 className="mt-3 text-4xl font-black tracking-tight sm:text-5xl">
            Used market snapshot
          </h1>
          <p className="mt-5 max-w-3xl text-lg leading-8 text-ps-text-secondary">
            A deliberately small view of products PriceSift already knows how to identify and filter. These numbers come from the same current-search and price-history system behind the curated used pages, not from a giant automatically generated catalog.
          </p>
          <p className="mt-3 text-xs text-ps-neutral">
            Snapshot refreshed periodically. Page checked {checkedAt.toLocaleString("en-US", { timeZone: "America/Detroit" })} ET.
          </p>
        </header>

        <section className="mt-8 grid gap-5 md:grid-cols-2 xl:grid-cols-3" aria-label="Selected used market snapshots">
          {snapshots.map(({ product, data }) => {
            const context = data?.price_context;
            return (
              <article key={product.slug} className="rounded-3xl border border-ps-border bg-ps-surface p-6">
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-ps-neutral">{product.category}</p>
                <h2 className="mt-2 text-2xl font-black">
                  <Link href={`/used/${product.slug}`} className="hover:text-ps-accent-hover hover:underline">
                    {product.title}
                  </Link>
                </h2>
                <dl className="mt-5 space-y-3 text-sm">
                  <div className="flex items-start justify-between gap-4 border-b border-ps-border pb-3">
                    <dt className="text-ps-text-secondary">Current best</dt>
                    <dd className="font-black text-ps-text-primary">{money(context?.current_best_price)}</dd>
                  </div>
                  <div className="flex items-start justify-between gap-4 border-b border-ps-border pb-3">
                    <dt className="text-ps-text-secondary">30-day median</dt>
                    <dd className="font-bold text-ps-text-primary">{money(context?.historical_median_price)}</dd>
                  </div>
                  <div className="border-b border-ps-border pb-3">
                    <dt className="text-ps-text-secondary">Current vs. recent median</dt>
                    <dd className="mt-1 font-semibold text-ps-text-primary">{comparison(context?.current_vs_median_percent)}</dd>
                  </div>
                  <div className="flex items-start justify-between gap-4">
                    <dt className="text-ps-text-secondary">Snapshots with qualifying inventory</dt>
                    <dd className="font-bold text-ps-text-primary">
                      {context?.availability_rate == null ? "—" : `${context.availability_rate.toFixed(1)}%`}
                    </dd>
                  </div>
                </dl>
                <p className="mt-5 text-xs leading-5 text-ps-neutral">
                  {context?.snapshot_count
                    ? `${context.snapshot_count} price-history snapshot${context.snapshot_count === 1 ? "" : "s"} in the current window.`
                    : "Price history is still building for this product."}
                </p>
                <Link
                  href={`/used/${product.slug}`}
                  className="mt-5 inline-flex font-bold text-ps-accent-hover hover:text-ps-text-primary hover:underline"
                >
                  See current filtered listings and buying checks →
                </Link>
              </article>
            );
          })}
        </section>

        <section className="mt-9 rounded-3xl border border-ps-border bg-ps-accent-soft p-6 sm:p-8">
          <h2 className="text-2xl font-black">What these numbers do and do not mean</h2>
          <p className="mt-3 max-w-4xl text-sm leading-7 text-ps-text-secondary sm:text-base">
            PriceSift only records price context from listings that survive its current exact-product and listing-quality checks. That makes this useful for understanding the cleaner inventory PriceSift actually surfaced, but it is not a complete census of every used item sold on every marketplace. Current listings can also disappear or change before checkout.
          </p>
          <div className="mt-5 flex flex-wrap gap-3">
            <Link href="/used" className="rounded-xl bg-ps-accent-strong px-5 py-3 text-sm font-bold text-white hover:bg-ps-accent-hover">
              Browse all curated used pages
            </Link>
            <Link href="/buying-guides/used-listing-red-flags" className="rounded-xl border border-ps-border bg-ps-surface px-5 py-3 text-sm font-bold text-ps-accent-hover hover:border-ps-border-strong">
              Read the listing red-flags guide
            </Link>
          </div>
        </section>

        <SiteFooter />
      </div>
    </main>
  );
}
