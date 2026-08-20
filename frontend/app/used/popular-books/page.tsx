import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter } from "@/components/SiteFooter";
import { popularBooks } from "@/lib/popularBooks";

export const metadata: Metadata = {
  title: "Popular Used Books: Exact-Edition Price Pages",
  description:
    "Browse a small rotating set of popular books with exact-edition used-price pages. Each featured title keeps its permanent URL when the list changes.",
  alternates: { canonical: "/used/popular-books" },
  robots: { index: true, follow: true },
};

export default function PopularBooksHubPage() {
  return (
    <main className="pricesift-public min-h-screen px-6 py-10 text-ps-text-primary">
      <div className="mx-auto max-w-6xl">
        <nav className="text-sm text-ps-text-secondary" aria-label="Breadcrumb">
          <Link href="/" className="hover:underline">Home</Link> /{" "}
          <Link href="/used" className="hover:underline">Used price guides</Link> / Popular books
        </nav>

        <section className="mt-8 rounded-[2rem] border border-ps-border bg-ps-surface p-7 sm:p-10">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-ps-accent-hover">
            Rotating featured titles
          </p>
          <h1 className="mt-3 text-4xl font-black tracking-tight sm:text-5xl">Popular used books</h1>
          <p className="mt-5 max-w-3xl text-lg leading-8 text-ps-text-secondary">
            This page can rotate as different books get attention. The individual book pages do not rotate: each one stays tied to a specific physical ISBN so PriceSift can compare the correct edition instead of mixing paperbacks, hardcovers, audiobooks, summaries, and special editions together.
          </p>

          <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {popularBooks.map((book) => (
              <Link
                key={book.slug}
                href={`/used/${book.slug}`}
                className="rounded-2xl border border-ps-border bg-ps-control p-5 transition hover:border-ps-border-strong hover:bg-ps-accent-soft"
              >
                <p className="text-xs uppercase tracking-[0.18em] text-ps-neutral">{book.author}</p>
                <h2 className="mt-2 text-xl font-bold">{book.title}</h2>
                <p className="mt-3 text-sm leading-6 text-ps-text-secondary">{book.editionLabel}</p>
                <p className="mt-1 text-xs text-ps-neutral">ISBN {book.isbn}</p>
              </Link>
            ))}
          </div>

          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/buying-guides/used-books" className="rounded-xl border border-ps-border px-4 py-2 text-sm font-bold text-ps-accent-hover hover:bg-ps-accent-soft">
              Used book buying guide →
            </Link>
            <Link href="/books/goodreads" className="rounded-xl border border-ps-border px-4 py-2 text-sm font-bold text-ps-accent-hover hover:bg-ps-accent-soft">
              Price a Goodreads list →
            </Link>
          </div>
        </section>
        <SiteFooter />
      </div>
    </main>
  );
}
