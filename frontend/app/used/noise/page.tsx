import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter } from "@/components/SiteFooter";
import { allIndexedProducts } from "@/lib/allIndexedProducts";
import { getNoiseIndex, type NoiseIndexModel, type NoiseReason } from "@/lib/noiseIndex";

export const revalidate = 1800;

export const metadata: Metadata = {
  title: "Used Marketplace Noise Index: How Many Listings Get Filtered",
  description:
    "PriceSift measures how many marketplace candidates are removed as wrong models, broken items, accessories, risky listings, and other low-confidence matches before used-price calculations.",
  alternates: { canonical: "/used/noise" },
  robots: { index: true, follow: true },
  openGraph: {
    title: "Used Marketplace Noise Index | PriceSift",
    description:
      "See how many current marketplace candidates PriceSift filters before calculating useful used prices.",
    url: "/used/noise",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Used Marketplace Noise Index | PriceSift",
    description:
      "See how many current marketplace candidates PriceSift filters before calculating useful used prices.",
  },
};

const categoryLabels: Record<string, string> = {
  cameras: "Cameras",
  consoles: "Consoles",
  gpus: "GPUs",
  cpus: "CPUs",
  ram: "RAM",
  lego: "LEGO",
};

function normalize(value: string): string {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}

function modelDestination(row: NoiseIndexModel): { href: string; exactPage: boolean } {
  const label = normalize(row.product_label);
  const query = normalize(row.query);
  const indexed = allIndexedProducts.find((product) => {
    if (product.category !== row.category) return false;
    const title = normalize(product.title);
    const productQuery = normalize(product.query);
    return title === label || title === query || productQuery === label || productQuery === query;
  });
  if (indexed) return { href: `/used/${indexed.slug}`, exactPage: true };
  return {
    href: `/search?category=${encodeURIComponent(row.category)}&q=${encodeURIComponent(row.query || row.product_label)}`,
    exactPage: false,
  };
}

function rate(value: number | null): string {
  return value === null ? "Not enough candidates" : `${value.toFixed(1)}%`;
}

function reasonBucket(reason: string): string {
  const value = reason.toLowerCase();
  if (
    value.includes("bad condition") || value.includes("hardware defect") ||
    value.includes("bad title term") || value.includes("cpu unsafe") ||
    value.includes("damage") ||
    value.includes("for parts") || value.includes("repair") ||
    value.includes("defective") || value.includes("not working") ||
    value.includes("untested") || value.includes("as-is") ||
    value.includes("as is") || value.includes("no power")
  ) return "Broken, parts, or risky condition";
  if (
    value.includes("accessory") || value.includes("controller listing") ||
    value.includes("without console")
  ) return "Accessory or incomplete listing";
  if (
    value.includes("bundle") || value.includes("lot") ||
    value.includes("full system")
  ) return "Bundle, lot, or full system";
  if (
    value.includes("catalog/product match rejected") ||
    value.includes("model") || value.includes("required term") ||
    value.includes("form factor") || value.includes("conflict")
  ) return "Wrong model or variant";
  if (value.includes("seller-defined variation")) return "Ambiguous variation listing";
  if (value.includes("feedback")) return "Seller quality check";
  if (value.includes("manual filter")) return "Known bad match";
  if (value.includes("reported listing")) return "Previously reported listing";
  return "Other low-confidence match";
}

function summarizeReasons(reasons: NoiseReason[]): Array<{ label: string; count: number }> {
  const buckets = new Map<string, number>();
  for (const reason of reasons) {
    if (!Number.isFinite(reason.count) || reason.count <= 0) continue;
    const label = reasonBucket(reason.reason);
    buckets.set(label, (buckets.get(label) || 0) + reason.count);
  }
  return Array.from(buckets.entries())
    .map(([label, count]) => ({ label, count }))
    .sort((left, right) => right.count - left.count);
}

function SnapshotCard({ row }: { row: NoiseIndexModel }) {
  const destination = modelDestination(row);
  const reasons = summarizeReasons(row.rejection_reasons).slice(0, 4);
  return (
    <article className="rounded-3xl border border-ps-border bg-ps-surface p-5 sm:p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-ps-neutral">
            {categoryLabels[row.category] || row.category}
          </p>
          <h3 className="mt-2 text-xl font-black text-ps-text-primary">
            <Link href={destination.href} className="hover:text-ps-accent-hover hover:underline">
              {row.product_label}
            </Link>
          </h3>
          <p className="mt-1 text-xs text-ps-neutral">
            Snapshot {new Date(row.observed_at).toLocaleString("en-US", { timeZone: "America/Detroit" })} ET
          </p>
        </div>
        <div className="rounded-2xl bg-ps-accent-soft px-4 py-3 text-right">
          <p className="text-xs uppercase tracking-[0.14em] text-ps-neutral">Noise rate</p>
          <p className="mt-1 text-2xl font-black text-ps-text-primary">{rate(row.noise_rate)}</p>
        </div>
      </div>

      <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div className="rounded-2xl bg-ps-control p-3">
          <p className="text-xs text-ps-neutral">Candidates checked</p>
          <p className="mt-1 text-xl font-black">{row.candidate_count}</p>
        </div>
        <div className="rounded-2xl bg-ps-control p-3">
          <p className="text-xs text-ps-neutral">Filtered out</p>
          <p className="mt-1 text-xl font-black">{row.filtered_count}</p>
        </div>
        <div className="rounded-2xl bg-ps-control p-3">
          <p className="text-xs text-ps-neutral">Eligible listings</p>
          <p className="mt-1 text-xl font-black">
            {row.eligible_count_exact ? row.eligible_count : `${row.eligible_count}+`}
          </p>
        </div>
        <div className="rounded-2xl bg-ps-control p-3">
          <p className="text-xs text-ps-neutral">Duplicates removed</p>
          <p className="mt-1 text-xl font-black">
            {row.duplicates_removed === null ? "Not recorded" : row.duplicates_removed}
          </p>
        </div>
      </div>

      <div className="mt-5">
        <div className="flex flex-wrap items-end justify-between gap-2">
          <h4 className="font-bold text-ps-text-primary">Top detected rejection reasons</h4>
          <p className="text-xs text-ps-neutral">One listing can trigger more than one reason.</p>
        </div>
        {reasons.length > 0 ? (
          <div className="mt-3 flex flex-wrap gap-2">
            {reasons.map((reason) => (
              <span key={reason.label} className="rounded-full border border-ps-border bg-ps-accent-soft px-3 py-2 text-sm text-ps-text-secondary">
                <strong className="text-ps-text-primary">{reason.count}</strong> {reason.label}
              </span>
            ))}
          </div>
        ) : (
          <p className="mt-3 text-sm leading-6 text-ps-text-secondary">
            {row.filtered_count === 0
              ? "No rejected listings were recorded for this snapshot."
              : "A reliable reason breakdown was not stored for this snapshot, so PriceSift does not backfill one."}
          </p>
        )}
      </div>

      <Link href={destination.href} className="mt-5 inline-flex text-sm font-bold text-ps-accent-hover hover:text-ps-text-primary hover:underline">
        {destination.exactPage ? "Open exact PriceSift model page →" : "Open exact filtered PriceSift search →"}
      </Link>
    </article>
  );
}

export default async function UsedNoisePage() {
  const data = await getNoiseIndex();
  const pageUrl = "https://www.pricesift.app/used/noise";
  const structuredData = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Dataset",
        name: "PriceSift Used Marketplace Noise Index",
        description:
          "Current PriceSift filtering counts showing marketplace candidates checked, rejected listings, eligible listings, and duplicate removals.",
        url: pageUrl,
        creator: { "@type": "Organization", name: "PriceSift", url: "https://www.pricesift.app/" },
        dateModified: data?.latest_observed_at || undefined,
      },
      {
        "@type": "BreadcrumbList",
        itemListElement: [
          { "@type": "ListItem", position: 1, name: "Home", item: "https://www.pricesift.app/" },
          { "@type": "ListItem", position: 2, name: "Used price guides", item: "https://www.pricesift.app/used" },
          { "@type": "ListItem", position: 3, name: "Marketplace Noise Index", item: pageUrl },
        ],
      },
    ],
  };

  return (
    <main className="pricesift-public min-h-screen px-4 py-8 text-ps-text-primary sm:px-6 sm:py-10">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData).replace(/</g, "\\u003c") }} />
      <div className="mx-auto max-w-7xl">
        <nav aria-label="Breadcrumb" className="text-sm text-ps-text-secondary">
          <ol className="flex flex-wrap items-center gap-2">
            <li><Link href="/" className="hover:underline">Home</Link></li>
            <li aria-hidden="true">/</li>
            <li><Link href="/used" className="hover:underline">Used price guides</Link></li>
            <li aria-hidden="true">/</li>
            <li aria-current="page" className="font-semibold text-ps-text-primary">Marketplace Noise Index</li>
          </ol>
        </nav>

        <header className="mt-8 rounded-[2rem] border border-ps-border bg-ps-surface p-7 sm:p-10">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-ps-accent-hover">PriceSift filtering data</p>
          <h1 className="mt-3 max-w-5xl text-4xl font-black tracking-tight sm:text-5xl">Used Marketplace Noise Index</h1>
          <p className="mt-5 max-w-4xl text-lg leading-8 text-ps-text-secondary">
            How much marketplace junk gets removed before PriceSift calculates a useful used price? This page uses stored PriceSift filtering counts from real marketplace searches instead of estimating a number after the fact.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/used/market" className="rounded-xl bg-ps-accent-strong px-5 py-3 text-sm font-bold text-white hover:bg-ps-accent-hover">
              See Used Market Index
            </Link>
            <Link href="/used" className="rounded-xl border border-ps-border px-5 py-3 text-sm font-bold text-ps-accent-hover hover:border-ps-border-strong">
              Browse used price guides
            </Link>
          </div>
          {data ? (
            <p className="mt-5 text-xs leading-5 text-ps-neutral">
              Index generated {new Date(data.generated_at).toLocaleString("en-US", { timeZone: "America/Detroit" })} ET
              {data.oldest_observed_at && data.latest_observed_at
                ? ` from snapshots collected ${new Date(data.oldest_observed_at).toLocaleString("en-US", { timeZone: "America/Detroit" })}–${new Date(data.latest_observed_at).toLocaleString("en-US", { timeZone: "America/Detroit" })} ET.`
                : "."} Models older than {data.stale_after_days} days are excluded from this current view.
            </p>
          ) : null}
        </header>

        {!data ? (
          <section className="mt-8 rounded-3xl border border-ps-border bg-ps-surface p-7">
            <h2 className="text-2xl font-black">Filtering data is temporarily unavailable.</h2>
            <p className="mt-3 text-ps-text-secondary">The regular PriceSift used guides and searches still work normally.</p>
          </section>
        ) : (
          <>
            <section className="mt-8 rounded-3xl border border-amber-300 bg-amber-50 p-6">
              <h2 className="text-xl font-black">Current snapshot, not a made-up historical trend</h2>
              <p className="mt-2 max-w-4xl text-sm leading-6 text-ps-text-secondary">
                PriceSift has historical candidate and filtering totals, but rejection reasons were not historically attached to each price snapshot with enough reliability to claim a 7-day or 30-day reason trend. This first version therefore shows the latest trustworthy marketplace snapshot only.
              </p>
            </section>

            {data.categories.length > 0 ? (
              <section className="mt-10" aria-labelledby="noise-categories">
                <p className="text-sm uppercase tracking-[0.22em] text-ps-neutral">Weighted by candidates checked</p>
                <h2 id="noise-categories" className="mt-2 text-3xl font-black">Category noise</h2>
                <p className="mt-3 max-w-4xl text-sm leading-6 text-ps-text-secondary">
                  Category rates use total filtered listings divided by total candidates checked. PriceSift does not average model percentages, which would let tiny searches distort the category.
                </p>
                <div className="mt-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                  {data.categories.map((category) => (
                    <article key={category.category} className="rounded-3xl border border-ps-border bg-ps-surface p-5">
                      <p className="text-xs font-bold uppercase tracking-[0.18em] text-ps-neutral">{categoryLabels[category.category] || category.category}</p>
                      <p className="mt-3 text-4xl font-black">{rate(category.noise_rate)}</p>
                      <p className="mt-2 text-sm text-ps-text-secondary">
                        {category.filtered_count} filtered from {category.candidate_count} candidates across {category.model_count} current model{category.model_count === 1 ? "" : "s"}.
                      </p>
                      <p className="mt-2 text-xs text-ps-neutral">
                        {category.duplicates_removed === null
                          ? "Duplicate counts were not stored for these snapshots."
                          : category.duplicates_complete
                            ? `${category.duplicates_removed} duplicate candidate matches removed separately.`
                            : `${category.duplicates_removed} duplicates recorded across ${category.duplicates_reported_model_count} of ${category.model_count} models; older snapshots stay unknown.`}
                      </p>
                    </article>
                  ))}
                </div>
              </section>
            ) : null}

            {data.noisiest.length > 0 ? (
              <section className="mt-10" aria-labelledby="noisiest-heading">
                <p className="text-sm uppercase tracking-[0.22em] text-ps-neutral">Minimum {data.minimum_ranking_candidates} candidates</p>
                <h2 id="noisiest-heading" className="mt-2 text-3xl font-black">Noisiest current product searches</h2>
                <div className="mt-5 grid gap-3 lg:grid-cols-2">
                  {data.noisiest.map((row, index) => {
                    const destination = modelDestination(row);
                    return (
                      <Link key={row.product_id} href={destination.href} className="flex items-center justify-between gap-4 rounded-2xl border border-ps-border bg-ps-surface p-5 hover:border-ps-border-strong">
                        <div>
                          <p className="text-xs font-bold uppercase tracking-[0.14em] text-ps-neutral">#{index + 1} · {row.candidate_count} candidates</p>
                          <p className="mt-1 font-black text-ps-text-primary">{row.product_label}</p>
                        </div>
                        <p className="text-2xl font-black">{rate(row.noise_rate)}</p>
                      </Link>
                    );
                  })}
                </div>
              </section>
            ) : null}

            <section className="mt-10" aria-labelledby="model-snapshots-heading">
              <p className="text-sm uppercase tracking-[0.22em] text-ps-neutral">Current filtering snapshots</p>
              <h2 id="model-snapshots-heading" className="mt-2 text-3xl font-black">Tracked product searches</h2>
              <div className="mt-5 grid gap-5 xl:grid-cols-2">
                {data.models.map((row) => <SnapshotCard key={row.product_id} row={row} />)}
              </div>
            </section>

            <section className="mt-10 grid gap-5 lg:grid-cols-2">
              <div className="rounded-3xl border border-ps-border bg-ps-accent-soft p-6 sm:p-8">
                <h2 className="text-2xl font-black">What “noise” means here</h2>
                <ul className="mt-4 space-y-3 text-sm leading-6 text-ps-text-secondary sm:text-base">
                  <li>• This measures listings PriceSift detected and filtered before used-price calculations.</li>
                  <li>• One listing can trigger multiple rejection reasons, so reason counts can add up to more than the number filtered.</li>
                  <li>• It is not a claim that PriceSift detects every bad, misleading, risky, or irrelevant listing.</li>
                  <li>• Marketplace inventory changes constantly, so candidate counts and noise rates move with it.</li>
                </ul>
              </div>
              <div className="rounded-3xl border border-ps-border bg-ps-surface p-6 sm:p-8">
                <h2 className="text-2xl font-black">Duplicates are separate on purpose</h2>
                <p className="mt-3 text-sm leading-7 text-ps-text-secondary sm:text-base">
                  A duplicate candidate is not automatically a bad marketplace listing. PriceSift now stores exact duplicate removals separately at collection time and never puts them in the noise-rate numerator. Older snapshots without that exact count stay marked unavailable instead of being guessed.
                </p>
                <p className="mt-3 text-xs leading-5 text-ps-neutral">{data.methodology}</p>
              </div>
            </section>
          </>
        )}

        <SiteFooter />
      </div>
    </main>
  );
}
