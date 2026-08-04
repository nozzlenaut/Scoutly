import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { DeliveryResultsGrid } from "@/components/DeliveryResultsGrid";
import { ManualResourcesPanel } from "@/components/ManualResourcesPanel";
import { PriceContextPanel } from "@/components/PriceContextPanel";
import { SiteFooter } from "@/components/SiteFooter";
import { getIndexedProduct, indexedProducts } from "@/lib/indexedProducts";
import { getIndexedSearchResults } from "@/lib/indexedSearch";

export const revalidate = 1800;
export const dynamicParams = false;

export function generateStaticParams() {
  return indexedProducts.map((product) => ({ slug: product.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const product = getIndexedProduct(slug);
  if (!product) return {};
  return {
    title: `Used ${product.title} prices`,
    description: product.description,
    alternates: { canonical: `/used/${product.slug}` },
    robots: { index: true, follow: true },
    openGraph: {
      title: `Used ${product.title} prices | PriceSift`,
      description: product.description,
      url: `/used/${product.slug}`,
    },
  };
}

export default async function IndexedProductPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const product = getIndexedProduct(slug);
  if (!product) notFound();

  const data = await getIndexedSearchResults(product.query, product.category);
  const resolved = data?.resolved_product;
  const results = data?.results || [];
  const checkedAt = new Date().toISOString();
  const related = indexedProducts
    .filter(
      (item) =>
        item.category === product.category && item.slug !== product.slug,
    )
    .slice(0, 4);
  const searchParams = new URLSearchParams({
    category: product.category,
    q: product.query,
  });

  const structuredData =
    results.length > 0
      ? {
          "@context": "https://schema.org",
          "@type": "ItemList",
          name: `Used ${product.title} listings`,
          itemListElement: results.map((listing, index) => ({
            "@type": "ListItem",
            position: index + 1,
            item: {
              "@type": "Product",
              name: listing.title,
              url: listing.url,
              image: listing.image_url || undefined,
              offers: {
                "@type": "Offer",
                price: listing.total_price,
                priceCurrency: "USD",
                itemCondition: listing.condition,
                url: listing.url,
              },
            },
          })),
        }
      : null;

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-white">
      {structuredData ? (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(structuredData).replace(/</g, "\\u003c"),
          }}
        />
      ) : null}
      <div className="mx-auto max-w-6xl">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <Link
            href="/used"
            className="text-sm text-cyan-200 hover:text-cyan-100"
          >
            ← Used price guides
          </Link>
          <Link
            href={`/search?${searchParams.toString()}`}
            className="text-sm text-cyan-200 hover:text-cyan-100"
          >
            Run live PriceSift search →
          </Link>
        </div>

        <section className="mt-8 rounded-[2rem] border border-white/10 bg-white/[0.04] p-6 sm:p-9">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200">
            Cleaner current used listings
          </p>
          <h1 className="mt-3 text-4xl font-black tracking-tight sm:text-5xl">
            Used {product.title}
          </h1>
          <p className="mt-5 max-w-3xl text-lg leading-8 text-slate-300">
            {product.description}
          </p>
          <p className="mt-3 text-xs text-slate-500">
            Last checked{" "}
            {new Date(checkedAt).toLocaleString("en-US", {
              timeZone: "America/Detroit",
            })}{" "}
            ET
          </p>

          {data ? <PriceContextPanel context={data.price_context} /> : null}

          {results.length > 0 ? (
            <DeliveryResultsGrid
              results={results}
              query={product.query}
              category={product.category}
              productId={resolved?.product.id}
              ariaLabel={`Used ${product.title} listings`}
              deliveryEnabled={false}
            />
          ) : (
            <div className="mt-8 rounded-2xl border border-amber-300/20 bg-amber-300/10 p-5 text-amber-50">
              <h2 className="text-xl font-bold">
                No qualifying listings are available right now.
              </h2>
              <p className="mt-2 text-sm leading-6 text-amber-100/90">
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
          />

          <div className="mt-8 grid gap-5 lg:grid-cols-2">
            <section className="rounded-2xl border border-white/10 bg-slate-950/50 p-5">
              <h2 className="text-xl font-bold">Common listing traps</h2>
              <ul className="mt-4 space-y-3 text-sm leading-6 text-slate-300">
                {product.commonTraps.map((trap) => (
                  <li key={trap}>• {trap}</li>
                ))}
              </ul>
            </section>
            <section className="rounded-2xl border border-white/10 bg-slate-950/50 p-5">
              <h2 className="text-xl font-bold">How this page works</h2>
              <p className="mt-4 text-sm leading-6 text-slate-300">
                This page is tied to one manually approved exact product.
                PriceSift resolves the catalog identity, checks current
                marketplace candidates, removes obvious wrong-model,
                accessory-only, incomplete, broken, and misleading listings
                when detectable, and shows no more than three cleaner options.
              </p>
              <Link
                href="/reuse"
                className="mt-4 inline-flex text-sm font-semibold text-emerald-200 hover:text-emerald-100"
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
                    className="rounded-full border border-white/10 px-4 py-2 text-sm text-cyan-100 hover:bg-white/10"
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
