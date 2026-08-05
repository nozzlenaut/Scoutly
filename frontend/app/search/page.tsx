import type { Metadata } from "next";
import type { ReactNode } from "react";
import Link from "next/link";
import { redirect } from "next/navigation";
import { AmazonFallbackCard } from "@/components/AmazonFallbackCard";
import { AuctionResults } from "@/components/AuctionResults";
import { PriceContextPanel } from "@/components/PriceContextPanel";
import { PublicBookResults } from "@/components/PublicBookResults";
import { SearchForm } from "@/components/SearchForm";
import { SearchTransitionGuard } from "@/components/SearchTransitionGuard";
import { ShareSearchButton } from "@/components/ShareSearchButton";
import { DeliveryResultsGrid } from "@/components/DeliveryResultsGrid";
import { SiteFooter } from "@/components/SiteFooter";
import { buildEbaySearchUrl, buildOutboundUrl, searchDeals, searchPublicBooksByIsbn } from "@/lib/api";
import { getCategoryById, getSearchCategoryById } from "@/lib/categoryCatalog";
import { lookupOpenLibraryAvailability } from "@/lib/openLibrary";

function PageShell({ children }: { children: ReactNode }) {
  return (
    <main className="pricesift-results min-h-screen bg-ps-canvas px-6 py-10 text-ps-text-primary">
      <div className="mx-auto max-w-6xl">
        <div className="flex items-center justify-between gap-4">
          <Link
            href="/"
            className="text-2xl font-black tracking-tight text-ps-text-primary"
          >
            PriceSift
          </Link>
          <Link href="/" className="text-sm font-semibold text-ps-accent-hover hover:text-ps-text-primary hover:underline">
            Home
          </Link>
        </div>
        {children}
        <SiteFooter />
      </div>
    </main>
  );
}

export async function generateMetadata({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; category?: string; us_only?: string }>;
}): Promise<Metadata> {
  const params = await searchParams;
  const category = getSearchCategoryById(params.category);
  const query = (params.q || "").trim();
  const usOnly = params.us_only === "1" || params.us_only === "true";

  if (!category) {
    return {
      title: "Category unavailable",
      description: "This PriceSift category is unavailable or paused.",
      robots: { index: false, follow: true },
    };
  }

  if (!query) {
    return {
      title: `Search ${category.label}`,
      description: `Search cleaner used-listing results for ${category.label}.`,
      robots: { index: false, follow: true },
    };
  }

  const description = `Cleaner used-listing results for ${query}.`;
  const shareParams = new URLSearchParams({ category: category.id, q: query });
  if (usOnly) shareParams.set("us_only", "1");
  const shareUrl = `/search?${shareParams.toString()}`;
  return {
    title: `${query} deals`,
    description,
    robots: { index: false, follow: true },
    openGraph: {
      title: `${query} prices | PriceSift`,
      description,
      url: shareUrl,
    },
    twitter: {
      card: "summary",
      title: `${query} prices | PriceSift`,
      description,
    },
  };
}

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; category?: string; us_only?: string }>;
}) {
  const params = await searchParams;
  const rawCategory = (params.category || "").trim();
  const rawQuery = (params.q || "").trim();
  const usOnly = params.us_only === "1" || params.us_only === "true";
  const knownCategory = getCategoryById(rawCategory);
  const category = getSearchCategoryById(rawCategory);

  if (category?.id === "lenses") {
    redirect("/lenses");
  }

  if (!category) {
    return (
      <PageShell>
        <section className="mt-8 rounded-[2rem] border border-ps-border bg-ps-surface p-5">
          <SearchForm theme="light" />
        </section>
        <div
          className="mt-8 rounded-3xl border border-ps-border bg-ps-surface p-6 text-ps-warning"
          role="status"
        >
          <h1 className="text-2xl font-black">Category unavailable</h1>
          <p className="mt-3 text-sm leading-6">
            {knownCategory
              ? `${knownCategory.label} is paused right now while PriceSift improves filtering for that category.`
              : "That category is not available in PriceSift yet."}
          </p>
          <p className="mt-3 text-sm leading-6">
            Pick an active category above to search again.
          </p>
        </div>
      </PageShell>
    );
  }

  if (!rawQuery) {
    return (
      <PageShell>
        <section className="mt-8 rounded-[2rem] border border-ps-border bg-ps-surface p-5">
          <SearchForm initialCategoryId={category.id} initialQuery="" initialUsOnly={usOnly} compact theme="light" />
        </section>
        <div
          className="mt-8 rounded-3xl border border-ps-border bg-ps-surface p-6 text-ps-text-primary"
          role="status"
        >
          <h1 className="text-2xl font-black">Search needed</h1>
          <p className="mt-3 text-sm leading-6 text-ps-text-secondary">
            {category.id === "ram"
              ? "Complete the first four RAM builder choices above. PriceSift requires a clear DDR type, form factor, capacity, and stick configuration."
              : category.id === "cpus"
                ? "Choose a CPU manufacturer, socket, generation, and exact model above. Suffix variants remain separate products."
                : category.id === "consoles"
                  ? "Choose a console brand, family / generation, and core model above. Storage, color, and edition variants are grouped together."
                  : category.id === "books"
                    ? "Enter a valid ISBN-10 or ISBN-13 above, or scan the barcode. PriceSift searches that exact used-book edition rather than guessing from a title."
                    : `Type an exact ${category.label.toLowerCase()} item above. PriceSift will not fall back to a default item from an empty URL.`}
          </p>
        </div>
      </PageShell>
    );
  }

  if (category.id === "books") {
    const [bookData, openLibrary] = await Promise.all([
      searchPublicBooksByIsbn(rawQuery, 35, { usOnly, trackAnalytics: true }),
      lookupOpenLibraryAvailability(rawQuery),
    ]);
    return (
      <PageShell>
        <section className="mt-8 rounded-[2rem] border border-ps-border bg-ps-surface p-4 sm:p-5">
          <SearchForm
            key={`${category.id}:${rawQuery}`}
            initialCategoryId={category.id}
            initialQuery={rawQuery}
            initialUsOnly={usOnly}
            compact
            theme="light"
          />
        </section>
        <SearchTransitionGuard key={`books:${rawQuery}:${usOnly ? "us" : "all"}`} theme="light">
          <PublicBookResults data={bookData} query={rawQuery} deliveryEnabled={usOnly} openLibrary={openLibrary} theme="light" />
        </SearchTransitionGuard>
      </PageShell>
    );
  }

  const data = await searchDeals(rawQuery, category.id, "ebay", {
    includeAuctions: false,
    auctionHours: 24,
    usOnly,
    trackAnalytics: true,
  });
  const resolved = data.resolved_product;
  const hasKehResults = data.results.some((result) => result.provider.toLowerCase() === "keh");
  const isKehOnly = resolved?.product.metadata?.provider_scope === "keh";
  const providerLabel = isKehOnly
    ? "Live KEH results"
    : hasKehResults
      ? "Live eBay + KEH results"
      : "Live eBay results";
  const likelyAlternatives = (data.suggested_products || [])
    .filter((match) => match.confidence >= 0.8)
    .slice(0, 4);
  const emptyTarget = resolved ? "this resolved item" : "this query";
  const fixedPriceEmptyMessage =
    data.diagnostics.fixed_price_candidates > 0
      ? `No safe Buy It Now listings right now for ${emptyTarget}. PriceSift reviewed ${data.diagnostics.fixed_price_candidates} candidates and removed those that did not pass the current checks.`
      : `No active Buy It Now listings were found right now for ${emptyTarget}.`;
  const broaderEbayUrl = buildOutboundUrl(
    buildEbaySearchUrl(data.query, category.id),
    {
      query: data.query,
      category: category.id,
      productId: resolved?.product.id,
      provider: "eBay",
      title: `Broader eBay search: ${data.query}`,
    },
  );

  if (!resolved) {
    return (
      <PageShell>
        <section className="mt-8 rounded-[2rem] border border-ps-border bg-ps-surface p-4 sm:p-5">
          <SearchForm
            key={`${category.id}:${rawQuery}`}
            initialCategoryId={category.id}
            initialQuery={rawQuery}
            initialUsOnly={usOnly}
            compact
            theme="light"
          />
        </section>

        <div className="mt-8 rounded-3xl border border-ps-border bg-ps-surface p-6 text-ps-text-primary" role="status">
          <p className="text-sm uppercase tracking-[0.22em] text-ps-warning">Not supported yet</p>
          <h1 className="mt-2 text-2xl font-black">PriceSift could not match “{data.query}” to a supported catalog item.</h1>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-ps-text-secondary">
            Public searches only run for products PriceSift knows how to identify and filter safely. Choose one of the suggested catalog items or try a more exact model name.
          </p>
          {likelyAlternatives.length > 0 ? (
            <div className="mt-5">
              <p className="text-sm font-semibold">Closest supported matches:</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {likelyAlternatives.map((match) => (
                  <Link
                    key={match.product.id}
                    href={`/search?category=${encodeURIComponent(category.id)}&q=${encodeURIComponent(match.product.display_name)}${usOnly ? "&us_only=1" : ""}`}
                    className="rounded-full border border-ps-border bg-ps-control px-4 py-2 text-sm font-semibold text-ps-accent-hover transition hover:border-ps-border-strong hover:bg-ps-accent-soft"
                  >
                    {match.product.display_name}
                  </Link>
                ))}
              </div>
            </div>
          ) : null}
          <p className="mt-5 text-xs leading-5 text-ps-neutral">
            No marketplace search was sent for this unsupported query. PriceSift is picky on purpose.
          </p>
        </div>
      </PageShell>
    );
  }

  return (
    <PageShell>
      <section className="mt-8 rounded-[2rem] border border-ps-border bg-ps-surface p-4 sm:p-5">
        <SearchForm
          key={`${category.id}:${rawQuery}`}
          initialCategoryId={category.id}
          initialQuery={rawQuery}
          initialUsOnly={usOnly}
          compact
          theme="light"
        />
      </section>

      <SearchTransitionGuard key={`${category.id}:${rawQuery}:${usOnly ? "us" : "all"}`} theme="light">
        <div className="mt-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
          <div>
            <p className="text-sm uppercase tracking-[0.25em] text-ps-neutral">
              Best used results
            </p>
            <h1 className="mt-2 text-4xl font-black">
              {resolved?.product.display_name ?? data.query}
            </h1>
            <div className="mt-3 space-y-2 text-sm text-ps-text-secondary">
              <p className="flex flex-wrap items-center gap-2">
                <span>{isKehOnly ? "KEH camera model" : "Catalog item"}: {resolved.product.display_name}</span>
                <span className="inline-flex whitespace-nowrap rounded-full bg-ps-accent-strong px-3 py-1 text-sm font-semibold text-white">
                  Product match {Math.round(resolved.confidence * 100)}%
                </span>
              </p>
              {isKehOnly ? (
                <p className="text-ps-neutral">
                  This model comes from KEH’s standardized current inventory and is not mapped to PriceSift’s tuned eBay catalog, so no eBay search was sent.
                </p>
              ) : null}
              {category.id === "consoles" ? (
                <p className="text-ps-neutral">
                  {resolved.product.variant?.includes("Edition")
                    ? `Results are narrowed to the ${resolved.product.variant}.`
                    : `All ${resolved.product.display_name} variants are grouped unless your search names a specific edition.`}
                </p>
              ) : null}
            </div>
          </div>
          <div className="flex flex-col items-start gap-3 sm:items-end">
            <p className="text-sm text-ps-text-secondary">
              {providerLabel} · Up to 3 Buy It Now options
              {usOnly ? " · eBay limited to US-located items" : ""}
            </p>
            <ShareSearchButton
              label={resolved?.product.display_name ?? data.query}
              bestPrice={data.price_context.current_best_price}
              theme="light"
            />
          </div>
        </div>

        <PriceContextPanel context={data.price_context} theme="light" />

        {data.results.length > 0 ? (
          <DeliveryResultsGrid
            results={data.results}
            query={data.query}
            category={category.id}
            productId={resolved?.product.id}
            ariaLabel="Buy It Now results"
            deliveryEnabled={usOnly}
            theme="light"
          />
        ) : (
          <div
            className="mt-8 rounded-3xl border border-ps-border bg-ps-surface p-6 text-ps-text-primary"
            role="status"
          >
            <h2 className="text-xl font-bold">{fixedPriceEmptyMessage}</h2>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-ps-text-secondary">
              PriceSift removes incomplete items, replacement pieces and parts,
              empty boxes or packaging, accessory-only listings, broken items,
              and unclear variation listings when those signals are detected.
            </p>
            {!isKehOnly ? (
              <>
                <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center">
                  <a
                    href={broaderEbayUrl}
                    target="_blank"
                    rel="sponsored noreferrer"
                    className="w-fit rounded-2xl bg-ps-accent-strong px-5 py-3 text-sm font-semibold text-white transition hover:bg-ps-accent-hover"
                  >
                    View broader Buy It Now results on eBay
                  </a>
                  <span className="text-xs leading-5 text-ps-neutral">
                    PriceSift’s listing-quality filters do not apply after you open
                    the broader eBay search.
                  </span>
                </div>
                <p className="mt-4 text-sm text-ps-text-secondary">
                  PriceSift is also checking ending-soon auctions below.
                </p>
              </>
            ) : null}
          </div>
        )}

        <AmazonFallbackCard
          query={resolved.product.display_name}
          category={category.id}
          productId={resolved.product.id}
          emphasized={data.results.length === 0}
          theme="light"
        />

        {!isKehOnly ? (
          <AuctionResults
            query={data.query}
            category={category.id}
            productId={resolved?.product.id}
            resolved={Boolean(resolved)}
            usOnly={usOnly}
            theme="light"
          />
        ) : null}
      </SearchTransitionGuard>
    </PageShell>
  );
}
