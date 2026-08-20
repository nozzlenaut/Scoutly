import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter } from "@/components/SiteFooter";
import { allIndexedProducts } from "@/lib/allIndexedProducts";

export const metadata: Metadata = {
  title: "Used Current-Generation Game Consoles",
  description:
    "Browse cleaner used listings and buying checks for current-generation PlayStation, Xbox, and Nintendo consoles.",
  alternates: { canonical: "/used/current-game-consoles" },
  robots: { index: true, follow: true },
};

const currentSlugs = [
  "playstation-5",
  "playstation-5-slim",
  "playstation-5-pro",
  "xbox-series-x",
  "xbox-series-s",
  "nintendo-switch-2",
];

export default function CurrentConsoleHubPage() {
  const consoles = currentSlugs
    .map((slug) => allIndexedProducts.find((product) => product.slug === slug))
    .filter((product) => product !== undefined);

  return (
    <main className="pricesift-public min-h-screen px-6 py-10 text-ps-text-primary">
      <div className="mx-auto max-w-6xl">
        <nav className="text-sm text-ps-text-secondary" aria-label="Breadcrumb">
          <Link href="/" className="hover:underline">Home</Link> /{" "}
          <Link href="/used" className="hover:underline">Used price guides</Link> / Current consoles
        </nav>

        <section className="mt-8 rounded-[2rem] border border-ps-border bg-ps-surface p-7 sm:p-10">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-ps-accent-hover">
            Current console price guides
          </p>
          <h1 className="mt-3 text-4xl font-black tracking-tight sm:text-5xl">
            Used current-generation game consoles
          </h1>
          <p className="mt-5 max-w-3xl text-lg leading-8 text-ps-text-secondary">
            Compare current used-console listings without mixing older generations, accessories, empty boxes, or obvious repair-only hardware into the same result set.
          </p>

          <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {consoles.map((console) => (
              <Link
                key={console.slug}
                href={`/used/${console.slug}`}
                className="rounded-2xl border border-ps-border bg-ps-control p-5 transition hover:border-ps-border-strong hover:bg-ps-accent-soft"
              >
                <p className="text-xs uppercase tracking-[0.18em] text-ps-neutral">{console.brand}</p>
                <h2 className="mt-2 text-xl font-bold">{console.title}</h2>
                <p className="mt-3 text-sm leading-6 text-ps-text-secondary">{console.description}</p>
              </Link>
            ))}
          </div>

          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/used/retro-game-consoles" className="rounded-xl border border-ps-border px-4 py-2 text-sm font-bold text-ps-accent-hover hover:bg-ps-accent-soft">
              Retro & previous-generation consoles →
            </Link>
            <Link href="/buying-guides/used-game-consoles" className="rounded-xl border border-ps-border px-4 py-2 text-sm font-bold text-ps-accent-hover hover:bg-ps-accent-soft">
              Used console buying guide →
            </Link>
          </div>
        </section>
        <SiteFooter />
      </div>
    </main>
  );
}
