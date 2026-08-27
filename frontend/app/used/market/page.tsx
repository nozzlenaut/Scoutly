import type { Metadata } from "next";
import Link from "next/link";
import { MarketIndexTable } from "@/components/MarketIndexTable";
import { SiteFooter } from "@/components/SiteFooter";
import { indexedProducts } from "@/lib/indexedProducts";
import { getMarketIndex, type MarketIndexCategory, type MarketIndexModel } from "@/lib/marketIndex";

export const revalidate = 21600;

export const metadata: Metadata = {
  title: "Used Market Index: Cameras, Consoles, GPUs & More",
  description:
    "Track median percentage movement across PriceSift's used-market price history, then sort and open individual camera, console, GPU, CPU, and other model histories.",
  alternates: { canonical: "/used/market" },
  robots: { index: true, follow: true },
  openGraph: {
    title: "PriceSift Used Market Index",
    description:
      "See whether tracked used prices are heating up or cooling down, then drill into individual model price history and current filtered listings.",
    url: "/used/market",
    type: "website",
  },
};

const categoryLabels: Record<string, string> = {
  cameras: "Camera Market Index",
  consoles: "Console Market Index",
  gpus: "GPU Market Index",
  cpus: "CPU Market Index",
  lego: "LEGO Market Index",
};

function signedPercent(value: number): string {
  if (Math.abs(value) < 0.05) return "0.0%";
  return `${value > 0 ? "+" : ""}${value.toFixed(1)}%`;
}

function changeClasses(value: number): string {
  if (value > 0.05) return "text-rose-700";
  if (value < -0.05) return "text-emerald-700";
  return "text-ps-text-secondary";
}

function normalize(value: string): string {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}

function modelHref(row: MarketIndexModel): string {
  const label = normalize(row.product_label);
  const query = normalize(row.query);
  const indexed = indexedProducts.find((product) => {
    if (product.category !== row.category) return false;
    const title = normalize(product.title);
    const productQuery = normalize(product.query);
    return title === label || title === query || productQuery === label || productQuery === query;
  });

  if (indexed) return `/used/${indexed.slug}`;
  return `/search?category=${encodeURIComponent(row.category)}&q=${encodeURIComponent(row.query || row.product_label)}`;
}

function IndexCard({ category }: { category: MarketIndexCategory }) {
  const ready = category.index_value !== null && category.median_percent_change !== null;
  return (
    <article className="rounded-3xl border border-ps-border bg-ps-surface p-6">
      <p className="text-xs font-bold uppercase tracking-[0.18em] text-ps-neutral">
        {categoryLabels[category.category] || `${category.category} market index`}
      </p>
      {ready ? (
        <>
          <p className="mt-3 text-4xl font-black text-ps-text-primary">{category.index_value!.toFixed(1)}</p>
          <p className={`mt-2 font-bold ${changeClasses(category.median_percent_change!)}`}>
            {signedPercent(category.median_percent_change!)} median model move
          </p>
        </>
      ) : (
        <>
          <p className="mt-3 text-3xl font-black text-ps-text-primary">Building</p>
          <p className="mt-2 text-sm font-semibold text-ps-text-secondary">
            Needs {category.minimum_models_required} comparable models before PriceSift publishes an index value.
          </p>
        </>
      )}
      <p className="mt-4 text-sm text-ps-text-secondary">
        {category.model_count} comparable of {category.tracked_model_count} tracked model{category.tracked_model_count === 1 ? "" : "s"}
      </p>
    </article>
  );
}

export default async function UsedMarketPage() {
  const data = await getMarketIndex();
  const rows = (data?.models || []).map((row) => ({ ...row, href: modelHref(row) }));
  const pageUrl = "https://www.pricesift.app/used/market";
  const structuredData = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Dataset",
        name: "PriceSift Used Market Index",
        description:
          "A market-direction dataset derived from median qualifying used-listing prices for individually tracked products.",
        url: pageUrl,
        creator: { "@type": "Organization", name: "PriceSift", url: "https://www.pricesift.app/" },
        dateModified: data?.generated_at || undefined,
      },
      {
        "@type": "BreadcrumbList",
        itemListElement: [
          { "@type": "ListItem", position: 1, name: "PriceSift", item: "https://www.pricesift.app/" },
          { "@type": "ListItem", position: 2, name: "Used price guides", item: "https://www.pricesift.app/used" },
          { "@type": "ListItem", position: 3, name: "Used Market Index", item: pageUrl },
        ],
      },
    ],
  };

  return (
    <main className="pricesift-public min-h-screen px-4 py-8 text-ps-text-primary sm:px-6 sm:py-10">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData).replace(/</g, "\\u003c") }}
      />
      <div className="mx-auto max-w-7xl">
        <nav aria-label="Breadcrumb" className="text-sm text-ps-text-secondary">
          <ol className="flex flex-wrap items-center gap-2">
            <li><Link href="/" className="hover:underline">Home</Link></li>
            <li aria-hidden="true">/</li>
            <li><Link href="/used" className="hover:underline">Used price guides</Link></li>
            <li aria-hidden="true">/</li>
            <li aria-current="page" className="font-semibold text-ps-text-primary">Used Market Index</li>
          </ol>
        </nav>

        <header className="mt-8 rounded-[2rem] border border-ps-border bg-ps-surface p-7 sm:p-10">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-ps-accent-hover">PriceSift price-history data</p>
          <h1 className="mt-3 max-w-4xl text-4xl font-black tracking-tight sm:text-5xl">Used Market Index</h1>
          <p className="mt-5 max-w-4xl text-lg leading-8 text-ps-text-secondary">
            A quick read on whether the used market is getting cheaper or more expensive, built from the percentage movement of individual tracked models instead of averaging their dollar prices together.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/#search" className="rounded-xl bg-ps-accent-strong px-5 py-3 text-sm font-bold text-white hover:bg-ps-accent-hover">
              Search current used listings
            </Link>
            <Link href="/used/noise" className="rounded-xl border border-ps-border bg-ps-surface px-5 py-3 text-sm font-bold text-ps-accent-hover hover:border-ps-border-strong">
              See marketplace noise index
            </Link>
            <Link href="/used" className="rounded-xl border border-ps-border bg-ps-surface px-5 py-3 text-sm font-bold text-ps-accent-hover hover:border-ps-border-strong">
              Browse individual price guides
            </Link>
          </div>
          {data ? (
            <p className="mt-5 text-xs text-ps-neutral">
              {data.comparable_model_count} comparable of {data.tracked_model_count} tracked models from {data.tracked_snapshot_count} stored price snapshots. Updated {new Date(data.generated_at).toLocaleString("en-US", { timeZone: "America/Detroit" })} ET.
            </p>
          ) : null}
        </header>

        {data && data.categories.length > 0 ? (
          <section className="mt-8" aria-labelledby="category-indexes-heading">
            <div className="flex flex-wrap items-end justify-between gap-3">
              <div>
                <p className="text-sm uppercase tracking-[0.22em] text-ps-neutral">The market at a glance</p>
                <h2 id="category-indexes-heading" className="mt-2 text-3xl font-black">Category indexes</h2>
              </div>
              <p className="max-w-xl text-sm leading-6 text-ps-text-secondary">
                100 represents each model’s smoothed starting baseline, built from the median of its first five qualifying snapshot medians rather than one possibly-wonky first observation.
              </p>
            </div>
            <div className="mt-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {data.categories.map((category) => <IndexCard key={category.category} category={category} />)}
            </div>
          </section>
        ) : (
          <section className="mt-8 rounded-3xl border border-ps-border bg-ps-surface p-7">
            <h2 className="text-2xl font-black">The index is still building.</h2>
            <p className="mt-3 text-ps-text-secondary">
              PriceSift needs repeat qualifying observations before it will publish market movement. Individual used searches still work normally.
            </p>
          </section>
        )}

        <section className="mt-10" aria-labelledby="models-heading">
          <p className="text-sm uppercase tracking-[0.22em] text-ps-neutral">Drill into the data</p>
          <h2 id="models-heading" className="mt-2 text-3xl font-black">Tracked models</h2>
          <p className="mt-3 max-w-4xl text-base leading-7 text-ps-text-secondary">
            Models stay visible while history is building, but PriceSift does not publish a percentage move until the sample rules below are satisfied.
          </p>
          <MarketIndexTable rows={rows} />
        </section>

        <section className="mt-10 grid gap-5 lg:grid-cols-2">
          <div className="rounded-3xl border border-ps-border bg-ps-accent-soft p-6 sm:p-8">
            <h2 className="text-2xl font-black">How the index works</h2>
            <p className="mt-3 text-sm leading-7 text-ps-text-secondary sm:text-base">
              {data?.methodology || "PriceSift uses stored qualifying price-history snapshots and waits for enough repeat observations before calculating market movement."}
            </p>
            <p className="mt-3 text-xs leading-5 text-ps-neutral">
              Raw stored history is not rewritten when these reliability rules change. The index is a derived view over the original observations.
            </p>
          </div>
          <div className="rounded-3xl border border-ps-border bg-ps-surface p-6 sm:p-8">
            <h2 className="text-2xl font-black">Using or citing this data?</h2>
            <p className="mt-3 text-sm leading-7 text-ps-text-secondary sm:text-base">
              You are welcome to cite the PriceSift Used Market Index or reference its current figures. Please link back to this page so readers can see the live table and methodology. Figures can change as new marketplace observations arrive.
            </p>
            <Link href="/feedback" className="mt-4 inline-flex font-bold text-ps-accent-hover hover:text-ps-text-primary hover:underline">
              Questions about the data? Contact PriceSift →
            </Link>
          </div>
        </section>

        <SiteFooter />
      </div>
    </main>
  );
}
