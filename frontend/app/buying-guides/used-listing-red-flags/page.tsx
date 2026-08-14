import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter } from "@/components/SiteFooter";

export const metadata: Metadata = {
  title: "Used Listing Red Flags: Untested, As-Is, Parts Only & More",
  description:
    "A practical guide to used-listing phrases and traps including untested, powers on, as-is, for parts, box only, incomplete items, stock photos, and vague condition notes.",
  alternates: { canonical: "/buying-guides/used-listing-red-flags" },
  robots: { index: true, follow: true },
  openGraph: {
    title: "Used Listing Red Flags | PriceSift",
    description:
      "How to interpret untested, powers on, as-is, for parts, box only, incomplete, and other risky used-marketplace listings.",
    url: "/buying-guides/used-listing-red-flags",
    type: "article",
  },
};

const redFlags = [
  {
    phrase: "Untested",
    meaning:
      "Treat it as unknown condition, not as a working item that the seller simply forgot to test. The uncertainty belongs in the price.",
  },
  {
    phrase: "Powers on",
    meaning:
      "It proves the item receives power. It does not prove the display, ports, storage, controls, autofocus, disc drive, GPU load stability, or other important functions work.",
  },
  {
    phrase: "As-is",
    meaning:
      "Slow down and read the full description. The phrase usually means you should assume you are accepting whatever uncertainty or disclosed faults are present.",
  },
  {
    phrase: "READ / see description",
    meaning:
      "Not automatically bad, but never skip the description. Important defects are often disclosed after a normal-looking title and photo.",
  },
  {
    phrase: "For parts / repair",
    meaning:
      "Price it as a repair project or donor, not as a discounted working item. A vague symptom can have several possible causes and repair costs.",
  },
  {
    phrase: "Box only / packaging only",
    meaning:
      "Marketplace titles can contain the full product name even when the actual sale is just the box, manual, packaging, or display insert.",
  },
  {
    phrase: "Accessory-only listings",
    meaning:
      "Controllers, battery grips, docks, cages, chargers, coolers, water blocks, stands, and replacement parts can look like the main product in a broad search.",
  },
  {
    phrase: "99% complete",
    meaning:
      "For LEGO, bundles, kits, or anything with many pieces, translate this to ‘incomplete’ until you know exactly what is missing and what replacement will cost.",
  },
  {
    phrase: "Stock photos only",
    meaning:
      "A stock image tells you what the product looks like when new, not the condition of the actual item. For a meaningful used purchase, real photos are much more useful.",
  },
  {
    phrase: "Wrong or vague model name",
    meaning:
      "Similar product names are one of the easiest ways to buy the wrong thing. Confirm model numbers, generation, suffix, storage, VRAM, mount, edition, or set number where they matter.",
  },
];

export default function UsedListingRedFlagsPage() {
  const pageUrl = "https://www.pricesift.app/buying-guides/used-listing-red-flags";
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
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
        name: "Buying guides",
        item: "https://www.pricesift.app/buying-guides",
      },
      {
        "@type": "ListItem",
        position: 3,
        name: "Used listing red flags",
        item: pageUrl,
      },
    ],
  };

  return (
    <main className="pricesift-public min-h-screen bg-ps-canvas px-4 py-7 text-ps-text-primary sm:px-6 sm:py-10">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(structuredData).replace(/</g, "\\u003c"),
        }}
      />
      <div className="mx-auto max-w-5xl">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <Link href="/" className="text-2xl font-black tracking-tight text-ps-text-primary">
            PriceSift
          </Link>
          <Link
            href="/buying-guides"
            className="text-sm font-semibold text-ps-accent-hover hover:text-ps-text-primary hover:underline"
          >
            All buying guides
          </Link>
        </div>

        <article className="mx-auto mt-8 max-w-3xl sm:mt-10">
          <nav aria-label="Breadcrumb" className="text-sm text-ps-text-secondary">
            <ol className="flex flex-wrap items-center gap-2">
              <li><Link href="/" className="hover:underline">Home</Link></li>
              <li aria-hidden="true">/</li>
              <li><Link href="/buying-guides" className="hover:underline">Buying guides</Link></li>
              <li aria-hidden="true">/</li>
              <li aria-current="page" className="font-semibold text-ps-text-primary">Used listing red flags</li>
            </ol>
          </nav>

          <header className="mt-7 sm:mt-9">
            <p className="text-sm font-bold uppercase tracking-[0.18em] text-ps-accent-hover">
              Marketplace language decoder
            </p>
            <h1 className="mt-3 text-4xl font-black leading-tight tracking-tight sm:text-5xl">
              Used listing red flags: what those vague phrases actually tell you
            </h1>
            <p className="mt-5 text-lg leading-8 text-ps-text-secondary">
              A cheap used listing can be excellent. The problem is when the headline sounds normal while the actual item is broken, incomplete, the wrong model, or not the product at all. These phrases are signals to inspect more closely, not automatic reasons to walk away.
            </p>
          </header>

          <section className="mt-10">
            <h2 className="text-2xl font-black tracking-tight">The phrases worth slowing down for</h2>
            <div className="mt-5 space-y-4">
              {redFlags.map((flag) => (
                <div key={flag.phrase} className="rounded-2xl border border-ps-border bg-ps-surface p-5">
                  <h3 className="text-lg font-bold">“{flag.phrase}”</h3>
                  <p className="mt-2 text-sm leading-6 text-ps-text-secondary sm:text-base sm:leading-7">
                    {flag.meaning}
                  </p>
                </div>
              ))}
            </div>
          </section>

          <section className="mt-12 border-t border-ps-border pt-8">
            <h2 className="text-2xl font-black tracking-tight">A better way to read a used listing</h2>
            <ol className="mt-5 list-decimal space-y-3 pl-6 text-base leading-7 text-ps-text-secondary">
              <li>Confirm the exact model or identifier before judging the price.</li>
              <li>Read the full title, condition field, description, and included-items list.</li>
              <li>Use the photos to verify the actual item, not just the product family.</li>
              <li>Separate cosmetic wear from functional uncertainty or physical damage.</li>
              <li>Price missing accessories, missing pieces, and unknown condition as part of the purchase.</li>
              <li>For expensive items, look for evidence that the important functions were actually tested.</li>
            </ol>
          </section>

          <section className="mt-12 rounded-3xl border border-ps-border bg-ps-accent-soft p-6">
            <h2 className="text-2xl font-black tracking-tight">This is the problem PriceSift tries to filter first</h2>
            <p className="mt-3 text-base leading-7 text-ps-text-secondary">
              PriceSift searches for the exact supported product and removes obvious wrong-model, broken, parts-only, box-only, accessory-only, incomplete, and misleading candidates when those signals can be detected. It then shows no more than three cleaner current options.
            </p>
            <Link
              href="/used"
              className="mt-5 inline-flex rounded-xl bg-ps-accent-strong px-5 py-3 font-bold text-white hover:bg-ps-accent-hover"
            >
              Browse curated used price guides
            </Link>
          </section>

          <section className="mt-12 border-t border-ps-border pt-8">
            <h2 className="text-2xl font-black tracking-tight">More specific buying guides</h2>
            <div className="mt-4 flex flex-wrap gap-2">
              <Link href="/buying-guides/used-cameras" className="rounded-full border border-ps-border px-4 py-2 text-sm font-semibold text-ps-accent-hover hover:bg-ps-accent-soft">Used cameras</Link>
              <Link href="/buying-guides/used-lenses" className="rounded-full border border-ps-border px-4 py-2 text-sm font-semibold text-ps-accent-hover hover:bg-ps-accent-soft">Used lenses</Link>
              <Link href="/buying-guides/used-gpus" className="rounded-full border border-ps-border px-4 py-2 text-sm font-semibold text-ps-accent-hover hover:bg-ps-accent-soft">Used GPUs</Link>
              <Link href="/buying-guides/used-game-consoles" className="rounded-full border border-ps-border px-4 py-2 text-sm font-semibold text-ps-accent-hover hover:bg-ps-accent-soft">Used consoles</Link>
              <Link href="/buying-guides/used-lego" className="rounded-full border border-ps-border px-4 py-2 text-sm font-semibold text-ps-accent-hover hover:bg-ps-accent-soft">Used LEGO</Link>
            </div>
          </section>
        </article>

        <SiteFooter />
      </div>
    </main>
  );
}
