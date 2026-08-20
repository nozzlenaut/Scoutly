import Link from "next/link";
import { AmazonFallbackCard } from "@/components/AmazonFallbackCard";
import { DeliveryResultsGrid } from "@/components/DeliveryResultsGrid";
import { SiteFooter } from "@/components/SiteFooter";
import { searchPublicBooksByIsbn } from "@/lib/api";
import type { PopularBook } from "@/lib/popularBooks";

export const popularBookRevalidate = 1800;

export async function PopularBookSeoPage({ book }: { book: PopularBook }) {
  const data = await searchPublicBooksByIsbn(book.isbn, 35, {
    trackAnalytics: false,
  }).catch(() => null);
  const results = data?.top_results ?? [];

  return (
    <main className="pricesift-public min-h-screen px-6 py-10 text-ps-text-primary">
      <div className="mx-auto max-w-6xl">
        <nav aria-label="Breadcrumb" className="text-sm text-ps-text-secondary">
          <Link href="/" className="hover:underline">Home</Link> /{" "}
          <Link href="/used" className="hover:underline">Used price guides</Link> /{" "}
          <Link href="/used/popular-books" className="hover:underline">Popular books</Link> / {book.title}
        </nav>

        <section className="mt-8 rounded-[2rem] border border-ps-border bg-ps-surface p-6 sm:p-9">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-ps-accent-hover">
            Popular used book · exact edition
          </p>
          <h1 className="mt-3 text-4xl font-black tracking-tight sm:text-5xl">
            Used {book.title}
          </h1>
          <p className="mt-3 text-lg font-semibold text-ps-text-secondary">{book.author}</p>
          <p className="mt-5 max-w-3xl text-lg leading-8 text-ps-text-secondary">
            {book.description}
          </p>
          <div className="mt-5 rounded-2xl border border-ps-border bg-ps-accent-soft p-4 text-sm leading-6 text-ps-text-secondary">
            <strong className="text-ps-text-primary">Tracked edition:</strong> {book.editionLabel} · ISBN {book.isbn}. PriceSift keeps book pages edition-specific so a cheaper listing for a different printing does not silently win.
          </div>

          {results.length ? (
            <DeliveryResultsGrid
              results={results}
              query={book.isbn}
              category="books"
              productId={`isbn-${book.isbn}`}
              ariaLabel={`Used ${book.title} listings`}
              deliveryEnabled={false}
              theme="light"
            />
          ) : (
            <div className="mt-8 rounded-2xl border border-ps-warning/40 bg-amber-50 p-5">
              <h2 className="text-xl font-bold">No qualifying used copies are available right now.</h2>
              <p className="mt-2 text-sm leading-6 text-ps-text-secondary">
                The page stays useful as an edition reference, and PriceSift will check the exact ISBN again when this page refreshes.
              </p>
            </div>
          )}

          <AmazonFallbackCard
            query={book.isbn}
            category="books"
            productId={`isbn-${book.isbn}`}
            isbn10={data?.isbn.isbn10 ?? undefined}
            book
            emphasized={!results.length}
            theme="light"
          />

          <div className="mt-8 grid gap-5 lg:grid-cols-2">
            <section className="rounded-2xl border border-ps-border bg-ps-control p-5">
              <h2 className="text-xl font-bold">What to check before buying</h2>
              <ul className="mt-4 space-y-2 text-sm leading-6 text-ps-text-secondary">
                {book.buyingChecks.map((check) => <li key={check}>• {check}</li>)}
              </ul>
            </section>
            <section className="rounded-2xl border border-ps-border bg-ps-control p-5">
              <h2 className="text-xl font-bold">Common listing traps</h2>
              <ul className="mt-4 space-y-2 text-sm leading-6 text-ps-text-secondary">
                {book.commonTraps.map((trap) => <li key={trap}>• {trap}</li>)}
              </ul>
            </section>
          </div>

          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/used/popular-books" className="rounded-xl border border-ps-border px-4 py-2 text-sm font-bold text-ps-accent-hover hover:bg-ps-accent-soft">
              More popular used books →
            </Link>
            <Link href="/buying-guides/used-books" className="rounded-xl border border-ps-border px-4 py-2 text-sm font-bold text-ps-accent-hover hover:bg-ps-accent-soft">
              Used book buying guide →
            </Link>
          </div>
        </section>
        <SiteFooter />
      </div>
    </main>
  );
}
