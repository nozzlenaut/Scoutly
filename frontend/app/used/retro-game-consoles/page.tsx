import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter } from "@/components/SiteFooter";
import { allIndexedProducts } from "@/lib/allIndexedProducts";

export const metadata: Metadata = {
  title: "Used Retro & Previous-Generation Game Consoles",
  description:
    "Browse cleaner used listings and buying checks for older PlayStation, Xbox, and Nintendo consoles. Current-generation systems are kept separate.",
  alternates: { canonical: "/used/retro-game-consoles" },
  robots: { index: true, follow: true },
};

const retroSlugs = [
  "playstation-2",
  "playstation-3",
  "playstation-4",
  "xbox-360",
  "xbox-one-s",
  "xbox-one-x",
  "nintendo-gamecube",
  "nintendo-wii",
  "nintendo-switch",
];

export default function RetroConsoleHubPage() {
  const consoles = retroSlugs
    .map((slug) => allIndexedProducts.find((product) => product.slug === slug))
    .filter((product) => product !== undefined);

  return (
    <main className="pricesift-public min-h-screen px-6 py-10 text-ps-text-primary">
      <div className="mx-auto max-w-6xl">
        <nav className="text-sm text-ps-text-secondary" aria-label="Breadcrumb">
          <Link href="/" className="hover:underline">Home</Link> /{" "}
          <Link href="/used" className="hover:underline">Used price guides</Link> / Retro consoles
        </nav>

        <section className="mt-8 rounded-[2rem] border border-ps-border bg-ps-surface p-7 sm:p-10">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-ps-accent-hover">
            Older console price guides
          </p>
          <h1 className="mt-3 text-4xl font-black tracking-tight sm:text-5xl">
            Used retro & previous-generation game consoles
          </h1>
          <p className="mt-5 max-w-3xl text-lg leading-8 text-ps-text-secondary">
            Older console searches get messy fast. PriceSift keeps current-generation systems on a separate page and focuses these links on complete, working older hardware instead of games, controllers, empty boxes, repair parts, and obvious wrong-generation listings.
          </p>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-ps-neutral">
            The newly added older systems also use PriceSift&apos;s optional AI listing review after the normal deterministic filters when that feature is enabled.
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
            <Link href="/used/current-game-consoles" className="rounded-xl border border-ps-border px-4 py-2 text-sm font-bold text-ps-accent-hover hover:bg-ps-accent-soft">
              Current-generation consoles →
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
