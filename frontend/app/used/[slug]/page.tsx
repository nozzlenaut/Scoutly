import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { DeliveryResultsGrid } from "@/components/DeliveryResultsGrid";
import { FilterTransparencyPanel } from "@/components/FilterTransparencyPanel";
import { ManualResourcesPanel } from "@/components/ManualResourcesPanel";
import { PopularBookSeoPage } from "@/components/PopularBookSeoPage";
import { PriceContextPanel } from "@/components/PriceContextPanel";
import { SiteFooter } from "@/components/SiteFooter";
import {
  allIndexedProducts,
  getAllIndexedProduct,
} from "@/lib/allIndexedProducts";
import { getBuyingGuideHref } from "@/lib/indexedProducts";
import { getIndexedSearchResults } from "@/lib/indexedSearch";
import { getPopularBook, popularBooks } from "@/lib/popularBooks";

export const revalidate = 1800;
export const dynamicParams = false;

const targetedUsedTitles: Record<string, string> = {
  "canon-eos-r10": "Used Canon EOS R10 Price: Median & Filtered Listings",
  "canon-eos-m50-mark-ii": "Used Canon EOS M50 Mark II Price: Median & Filtered Listings",
};

const targetedUsedDescriptions: Record<string, string> = {
  "canon-eos-r10": "See the current median used Canon EOS R10 price, filtered marketplace listings, price history, and model-specific buying checks from PriceSift.",
  "canon-eos-m50-mark-ii": "See the current median used Canon EOS M50 Mark II price, filtered marketplace listings, price history, and model-specific buying checks from PriceSift.",
};

const cameraInventoryHrefs: Record<string, string> = {
  "canon-eos-r10": "/cameras/canon-eos-r10-body",
  "canon-eos-m50-mark-ii": "/cameras/canon-eos-m50-mark-ii-body",
};

export function generateStaticParams() {
  return [
    ...allIndexedProducts.map((product) => ({ slug: product.slug })),
    ...popularBooks.map((book) => ({ slug: book.slug })),
  ];
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const book = getPopularBook(slug);
  if (book) {
    return {
      title: `Used ${book.title}: Prices & Exact Edition`,
      description: book.description,
      alternates: { canonical: `/used/${book.slug}` },
      robots: { index: true, follow: true },
      openGraph: {
        title: `Used ${book.title}: Prices & Exact Edition | PriceSift`,
        description: book.description,
        url: `/used/${book.slug}`,
        type: "website",
      },
      twitter: {
        card: "summary",
        title: `Used ${book.title}: Prices & Exact Edition | PriceSift`,
        description: book.description,
      },
    };
  }

  const product = getAllIndexedProduct(slug);
  if (!product) return {};

  const title = targetedUsedTitles[product.slug] || `Used ${product.title}: Filtered Listings & Prices`;
  const description = targetedUsedDescriptions[product.slug]
    || `${product.description} PriceSift checks current marketplace candidates, filters bad matches when detectable, and shows cleaner used options with price context and rejection counts.`;

  return {
    title,
    description,
    alternates: { canonical: `/used/${product.slug}` },
    robots: { index: true, follow: true },
    openGraph: {
      title: `${title} | PriceSift`,
      description,
      url: `/used/${product.slug}`,
      type: "website",
    },
    twitter: {
      card: "summary",
      title: `${title} | PriceSift`,
      description,
    },
  };
}

export default async function IndexedProductPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const book = getPopularBook(slug);
  if (book) return <PopularBookSeoPage book={book} />;

  const product = getAllIndexedProduct(slug);
  if (!product) notFound();

  const data = await getIndexedSearchResults(product.query, product.category);
  const resolved = data?.resolved_product;
  const results = data?.results || [];
  const checkedAt = new Date().toISOString();
  const related = allIndexedProducts
    .filter(
      (item) =>
        item.category === product.category && item.slug !== product.slug,
    )
    .slice(0, 4);
  const searchParams = new URLSearchParams({
    category: product.category,
    q: product.query,
    source: "seo_page",
  });
  const guideHref = getBuyingGuideHref(product.category);
  const pageUrl = `https://www.pricesift.app/used/${product.slug}`;
  const liveInventoryHref = cameraInventoryHrefs[product.slug];
  const prices = results
    .map((listing) => listing.total_price)
    .filter((value) => Number.isFinite(value) && value >= 0);
  const intro = product.slug === "canon-eos-r10"
    ? "See current used Canon EOS R10 prices and cleaner marketplace listings for the exact R10 camera body. PriceSift filters obvious wrong-model, accessory-only, broken, and misleading matches when detectable, then adds price context and a practical used-buying checklist."
    : product.description;

  const productNode = {
    "@type": "Product",
    "@id": `${pageUrl}#product`,
    name: product.title,
    brand: {
      "@type": "Brand",
      name: product.brand,
    },
    description: product.description,
    url: pageUrl,
    mainEntityOfPage: pageUrl,
    ...(prices.length > 0
      ? {
          offers: {
            "@type": "AggregateOffer",
            lowPrice: Math.min(...prices),
            highPrice: Math.max(...prices),
            offerCount: prices.length,
            priceCurrency: "USD",
            itemCondition: "https://schema.org/UsedCondition",
          },
        }
      : {}),
  };
  const structuredData = {
    "@context": "https://schema.org",
    "@graph": [
      productNode,
      {
        "@type": "BreadcrumbList",
        "@id": `${pageUrl}#breadcrumb`,
        itemListElement: [
          {
            "@type": "ListItem",
            position: 1,
            name: "PriceSift",
            item: "https://www.pricesift.app/",
          },
          {
            "@type": "ListItem",
            position: 2,
            name: "Used price guides",
            item: "https://www.pricesift.app/used",
          },
          {
            "@type": "ListItem",
            position: 3,
            name: product.title,
            item: pageUrl,
          },
        ],
      },
    ],
  };

  return (
    <main className="pricesift-public min-h-screen px-6 py-10 text-ps-text-primary">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(structuredData).replace(/</g, "\\u003c"),
        }}
      />
      <div className="mx-auto max-w-6xl">
        <nav aria-label="Breadcrumb" className="text-sm text-ps-text-secondary">
          <ol className="flex flex-wrap items-center gap-2">
            <li>
              <Link href="/" className="hover:text-ps-text-primary hover:underline">
                Home
              </Link>
            </li>
            <li aria-hidden="true">/</li>
            <li>
              <Link href="/used" className="hover:text-ps-text-primary hover:underline">
                Used price guides
              </Link>
            </li>
            <li aria-hidden="true">/</li>
            <li aria-current="page" className="font-semibold text-ps-text-primary">
              {product.title}
            </li>
          </ol>
        </nav>

        <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
          <Link
            href="/used"
            className="text-sm text-ps-accent-hover hover:text-ps-text-primary hover:underline"
          >
            ← All used price guides
          </Link>
          <div className="flex flex-wrap gap-4">
            {liveInventoryHref ? (
              <Link
                href={liveInventoryHref}
                className="text-sm font-semibold text-ps-accent-hover hover:text-ps-text-primary hover:underline"
              >
                Current KEH inventory →
              </Link>
            ) : null}
            <Link
              href={`/search?${searchParams.toString()}`}
              rel="nofollow"
              className="text-sm text-ps-accent-hover hover:text-ps-text-primary hover:underline"
            >
              Run live PriceSift search →
            </Link>
          </div>
        </div>

        <section className="mt-8 rounded-[2rem] border border-ps-border bg-ps-surface p-6 sm:p-9">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-ps-accent-hover">
            Cleaner current used listings
          </p>
          <h1 className="mt-3 text-4xl font-black tracking-tight sm:text-5xl">
            Used {product.title}
          </h1>
          <p className="mt-5 max-w-3xl text-lg leading-8 text-ps-text-secondary">
            {intro}
          </p>
          <p className="mt-3 text-xs text-ps-neutral">
            Last checked{" "}
            {new Date(checkedAt).toLocaleString("en-US", {
              timeZone: "America/Detroit",
            })}{" "}
            ET
          </p>

          {data ? (
            <>
              <PriceContextPanel context={data.price_context} theme="light" />
              <FilterTransparencyPanel
                diagnostics={data.diagnostics}
                resultCount={results.length}
              />
            </>
          ) : null}

          {results.length > 0 ? (
            <DeliveryResultsGrid
              results={results}
              query={product.query}
              category={product.category}
              productId={resolved?.product.id}
              ariaLabel={`Used ${product.title} listings`}
              deliveryEnabled={false}
              theme="light"
            />
          ) : (
            <div className="mt-8 rounded-2xl border border-ps-warning/40 bg-amber-50 p-5 text-ps-text-primary">
              <h2 className="text-xl font-bold">
                No qualifying listings are available right now.
              </h2>
              <p className="mt-2 text-sm leading-6 text-ps-text-secondary">
                {data
                  ? `PriceSift checked ${data.diagnostics.fixed_price_candidates} candidate listings and kept only exact, eligible matches.`
                  : "PriceSift could not refresh marketplace inventory at this moment. The buying guidance below is still available."}
              </p>
            </div>
          )}

          <ManualResourcesPanel
            query={product.query}
            category={product.category}
            productId={resolved?.product.id}
            theme="light"
          />

          <section className="mt-8 rounded-2xl border border-ps-border bg-ps-accent-soft p-5 sm:p-6">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-ps-accent-hover">
              Used-buying check
            </p>
            <h2 className="mt-2 text-2xl font-black">Is a used {product.title} worth considering?</h2>
            <p className="mt-4 max-w-4xl text-sm leading-7 text-ps-text-secondary sm:text-base">
              {product.buyingSummary}
            </p>
            <h3 className="mt-6 text-lg font-bold">What to check before buying</h3>
            <ul className="mt-3 space-y-2 text-sm leading-6 text-ps-text-secondary sm:text-base sm:leading-7">
              {product.buyingChecks.map((check) => (
                <li key={check}>• {check}</li>
              ))}
            </ul>
            <div className="mt-6 flex flex-wrap gap-3">
              <Link
                href={guideHref}
                className="rounded-xl border border-ps-border bg-ps-surface px-4 py-2 text-sm font-bold text-ps-accent-hover hover:border-ps-border-strong hover:text-ps-text-primary"
              >
                Read the full {product.category === "consoles" ? "console" : product.category === "lego" ? "LEGO" : product.category.slice(0, -1)} buying guide
              </Link>
              <Link
                href="/buying-guides/used-listing-red-flags"
                className="rounded-xl border border-ps-border bg-ps-surface px-4 py-2 text-sm font-bold text-ps-accent-hover hover:border-ps-border-strong hover:text-ps-text-primary"
              >
                Used-listing red flags
              </Link>
            </div>
          </section>

          <div className="mt-8 grid gap-5 lg:grid-cols-2">
            <section className="rounded-2xl border border-ps-border bg-ps-control p-5">
              <h2 className="text-xl font-bold">Common listing traps</h2>
              <ul className="mt-4 space-y-3 text-sm leading-6 text-ps-text-secondary">
                {product.commonTraps.map((trap) => (
                  <li key={trap}>• {trap}</li>
                ))}
              </ul>
            </section>
            <section className="rounded-2xl border border-ps-border bg-ps-control p-5">
              <h2 className="text-xl font-bold">How this page works</h2>
              <p className="mt-4 text-sm leading-6 text-ps-text-secondary">
                This page is tied to one manually approved exact product.
                PriceSift resolves the catalog identity, checks current
                marketplace candidates, removes obvious wrong-model,
                accessory-only, incomplete, broken, and misleading listings
                when detectable, and shows no more than three cleaner options.
                The live counts above expose that filtering instead of asking
                you to take the claim on faith.
              </p>
              <Link
                href="/reuse"
                className="mt-4 inline-flex text-sm font-semibold text-ps-success hover:text-ps-text-primary hover:underline"
              >
                Why PriceSift focuses on buying used →
              </Link>
            </section>
          </div>

          {related.length > 0 ? (
            <section className="mt-8">
              <h2 className="text-xl font-bold">Related used guides</h2>
              <div className="mt-4 flex flex-wrap gap-2">
                {related.map((item) => (
                  <Link
                    key={item.slug}
                    href={`/used/${item.slug}`}
                    className="rounded-full border border-ps-border px-4 py-2 text-sm text-ps-accent-hover hover:bg-ps-accent-soft"
                  >
                    {item.title}
                  </Link>
                ))}
              </div>
            </section>
          ) : null}
        </section>
        <SiteFooter />
      </div>
    </main>
  );
}
