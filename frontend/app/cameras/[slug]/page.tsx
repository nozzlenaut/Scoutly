import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { AmazonFallbackCard } from "@/components/AmazonFallbackCard";
import { ShareSearchButton } from "@/components/ShareSearchButton";
import { SiteFooter } from "@/components/SiteFooter";
import { buildOutboundUrl, getPublicKehCameraModel, type KehCameraModel } from "@/lib/api";
import { findIndexedCameraProduct } from "@/lib/indexedProducts";

export const dynamic = "force-dynamic";

function money(value?: number | null, currency = "USD"): string {
  if (value === null || value === undefined) return "Price unavailable";
  return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(value);
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  try {
    const model = await getPublicKehCameraModel(slug);
    const indexedProduct = findIndexedCameraProduct(model.catalog_product_label, model.model_name);
    const providerText = model.provider_scope === "ebay_keh" ? "eBay and KEH" : "KEH";
    const canonical = indexedProduct ? `/used/${indexedProduct.slug}` : `/cameras/${model.slug}`;
    return {
      title: `Used ${model.model_name} inventory at KEH`,
      description: `See current used ${model.model_name} inventory and prices from ${providerText} through PriceSift.`,
      alternates: { canonical },
      robots: { index: false, follow: true },
      openGraph: {
        title: `Used ${model.model_name} inventory | PriceSift`,
        description: `${model.listing_count} current KEH listings from ${money(model.lowest_price, model.currency)}.`,
        url: canonical,
        images: model.image_url ? [{ url: model.image_url }] : undefined,
      },
    };
  } catch {
    return {
      title: "Used camera model",
      robots: { index: false, follow: true },
    };
  }
}

export default async function CameraModelPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  let model: KehCameraModel;
  try {
    model = await getPublicKehCameraModel(slug);
  } catch {
    notFound();
  }

  const indexedProduct = findIndexedCameraProduct(model.catalog_product_label, model.model_name);
  const searchQuery = model.catalog_product_label || model.model_name;
  const searchUrl = `/search?category=cameras&q=${encodeURIComponent(searchQuery)}`;
  const isCatalogModel = model.provider_scope === "ebay_keh";

  return (
    <main className="pricesift-public min-h-screen px-4 py-8 text-ps-text-primary sm:px-6 sm:py-10">
      <div className="mx-auto max-w-6xl">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <Link href="/" className="text-2xl font-black tracking-tight text-ps-text-primary">PriceSift</Link>
          <Link href="/cameras" className="text-sm font-semibold text-ps-accent-hover hover:text-ps-text-primary hover:underline">All current KEH cameras</Link>
        </div>

        <section className="mt-10 grid gap-7 rounded-3xl border border-ps-border bg-ps-surface p-6 md:grid-cols-[220px_1fr] md:p-8">
          <div>
            {model.image_url ? (
              <img src={model.image_url} alt={model.model_name} className="h-52 w-full rounded-3xl bg-white object-contain p-3" />
            ) : (
              <div className="flex h-52 items-center justify-center rounded-3xl bg-ps-control text-ps-neutral">No image</div>
            )}
          </div>
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.22em] text-ps-accent-hover">{model.brand} used camera</p>
            <h1 className="mt-2 text-4xl font-black sm:text-5xl">{model.model_name}</h1>
            <p className="mt-4 max-w-3xl text-base leading-7 text-ps-text-secondary">
              {isCatalogModel
                ? "This camera confidently matches PriceSift’s tuned catalog, so its full search can compare filtered eBay listings with current KEH inventory."
                : "This model comes directly from KEH’s standardized current inventory. It remains KEH-only until PriceSift has a confident catalog identity and safe eBay matching rules."}
            </p>
            {indexedProduct ? (
              <div className="mt-5 rounded-2xl border border-ps-border bg-ps-accent-soft p-4">
                <p className="font-bold text-ps-text-primary">PriceSift has a curated buying page for this exact model.</p>
                <p className="mt-1 text-sm leading-6 text-ps-text-secondary">
                  It combines current filtered listings, price context, common marketplace traps, and model-specific used-buying checks.
                </p>
                <Link
                  href={`/used/${indexedProduct.slug}`}
                  className="mt-3 inline-flex font-bold text-ps-accent-hover hover:text-ps-text-primary hover:underline"
                >
                  Open the used {indexedProduct.title} guide →
                </Link>
              </div>
            ) : null}
            <div className="mt-5 flex flex-wrap gap-3 text-sm">
              <span className="rounded-full bg-ps-accent-soft px-4 py-2 text-ps-text-secondary">{model.listing_count} current KEH listings</span>
              <span className="rounded-full bg-emerald-50 px-4 py-2 font-bold text-ps-success">from {money(model.lowest_price, model.currency)}</span>
              <span className={`rounded-full px-4 py-2 font-bold ${isCatalogModel ? "bg-ps-accent-soft text-ps-accent-hover" : "bg-amber-50 text-ps-warning"}`}>
                {isCatalogModel ? "eBay + KEH search" : "KEH-only search"}
              </span>
            </div>
            <div className="mt-6 flex flex-wrap gap-3">
              <Link href={indexedProduct ? `/used/${indexedProduct.slug}` : searchUrl} className="rounded-2xl bg-ps-accent-strong px-5 py-3 font-bold text-white hover:bg-ps-accent-hover">
                {indexedProduct ? "Open curated used guide" : isCatalogModel ? "Compare eBay + KEH" : "Open PriceSift results"}
              </Link>
              <ShareSearchButton label={model.model_name} bestPrice={model.lowest_price} theme="light" />
            </div>
          </div>
        </section>

        <section className="mt-9">
          <p className="text-sm uppercase tracking-[0.22em] text-ps-neutral">Current specialty-retailer inventory</p>
          <h2 className="mt-2 text-2xl font-black">Lowest-priced copies currently at KEH</h2>
          <div className="mt-5 grid gap-5 lg:grid-cols-3">
            {model.listings.map((listing, index) => {
              const outboundUrl = buildOutboundUrl(listing.affiliate_url, {
                query: model.model_name,
                category: "cameras",
                productId: model.catalog_product_id || undefined,
                provider: "KEH",
                title: listing.title,
              });
              return (
                <article key={listing.aw_product_id} className="rounded-3xl border border-ps-border bg-ps-surface p-5">
                  <div className="flex gap-3">
                    {listing.image_url ? <img src={listing.image_url} alt="" className="h-24 w-24 rounded-2xl bg-white object-contain p-1" /> : null}
                    <div className="min-w-0">
                      <p className="text-xs font-bold uppercase tracking-[0.18em] text-ps-neutral">KEH option {index + 1}</p>
                      <h3 className="mt-1 line-clamp-3 text-sm font-semibold text-ps-text-primary">{listing.title}</h3>
                    </div>
                  </div>
                  <div className="mt-5 flex items-end justify-between gap-3">
                    <div>
                      <p className="text-2xl font-black">{money(listing.price, listing.currency)}</p>
                      <p className="mt-1 text-xs text-ps-text-secondary">
                        {listing.condition_grade_code || "Used"}{listing.condition_grade_label ? ` · ${listing.condition_grade_label}` : ""}
                      </p>
                    </div>
                    <a href={outboundUrl} target="_blank" rel="sponsored noreferrer" className="rounded-xl bg-ps-success px-4 py-2 text-sm font-bold text-white hover:opacity-90">
                      View at KEH
                    </a>
                  </div>
                </article>
              );
            })}
          </div>
          <p className="mt-4 text-xs leading-5 text-ps-neutral">
            Availability and prices come from PriceSift’s latest six-hour KEH feed sync and may change before checkout. KEH links are affiliate links.
          </p>
        </section>

        <AmazonFallbackCard
          query={model.model_name}
          category="cameras"
          productId={model.catalog_product_id || undefined}
          theme="light"
        />

        <SiteFooter />
      </div>
    </main>
  );
}
