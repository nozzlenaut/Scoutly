import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { SharePageButton } from "@/components/SharePageButton";
import { SiteFooter } from "@/components/SiteFooter";
import {
  buyingGuides,
  getBuyingGuide,
  type GuideSection,
} from "@/lib/buyingGuides";

export const dynamicParams = false;

export function generateStaticParams() {
  return buyingGuides.map((guide) => ({ slug: guide.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const guide = getBuyingGuide(slug);
  if (!guide) return {};

  const canonical = `/buying-guides/${guide.slug}`;
  return {
    title: guide.title,
    description: guide.description,
    alternates: { canonical },
    robots: { index: true, follow: true },
    openGraph: {
      title: `${guide.title} | PriceSift`,
      description: guide.description,
      url: canonical,
      type: "article",
    },
    twitter: {
      card: "summary",
      title: `${guide.title} | PriceSift`,
      description: guide.description,
    },
  };
}

function GuideSectionContent({ section }: { section: GuideSection }) {
  return (
    <section className="rounded-3xl border border-ps-border bg-ps-surface p-6 shadow-sm shadow-slate-900/5 sm:p-8">
      <h2 className="text-2xl font-black tracking-tight text-ps-text-primary sm:text-3xl">
        {section.title}
      </h2>

      {section.paragraphs?.map((paragraph) => (
        <p
          key={paragraph}
          className="mt-4 max-w-3xl text-base leading-7 text-ps-text-secondary"
        >
          {paragraph}
        </p>
      ))}

      {section.bullets ? (
        <ul className="mt-5 grid gap-3 text-base leading-7 text-ps-text-secondary">
          {section.bullets.map((bullet) => (
            <li key={bullet} className="flex gap-3">
              <span aria-hidden="true" className="mt-2 h-2 w-2 shrink-0 rounded-full bg-ps-accent-strong" />
              <span>{bullet}</span>
            </li>
          ))}
        </ul>
      ) : null}

      {section.table ? (
        <div className="mt-6 overflow-x-auto rounded-2xl border border-ps-border">
          <table className="w-full min-w-[560px] border-collapse text-left text-sm">
            <thead className="bg-ps-accent-soft text-ps-text-primary">
              <tr>
                {section.table.headers.map((header) => (
                  <th key={header} scope="col" className="px-4 py-3 font-bold">
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {section.table.rows.map((row) => (
                <tr key={row.join(":")} className="border-t border-ps-border">
                  {row.map((cell, index) =>
                    index === 0 ? (
                      <th key={cell} scope="row" className="px-4 py-3 font-semibold text-ps-text-primary">
                        {cell}
                      </th>
                    ) : (
                      <td key={cell} className="px-4 py-3 text-ps-text-secondary">
                        {cell}
                      </td>
                    ),
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}

      {section.note ? (
        <div className="mt-6 rounded-2xl border border-ps-border bg-ps-control p-4 text-sm leading-6 text-ps-text-secondary">
          {section.note}
        </div>
      ) : null}
    </section>
  );
}

export default async function BuyingGuidePage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const guide = getBuyingGuide(slug);
  if (!guide) notFound();

  const related = guide.relatedSlugs
    .map((relatedSlug) => getBuyingGuide(relatedSlug))
    .filter((item) => item !== null);

  return (
    <main className="pricesift-public min-h-screen bg-ps-canvas px-4 py-8 text-ps-text-primary sm:px-6 sm:py-10">
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

        <nav aria-label="Breadcrumb" className="mt-8 text-sm text-ps-text-secondary">
          <ol className="flex flex-wrap items-center gap-2">
            <li><Link href="/" className="hover:text-ps-text-primary hover:underline">Home</Link></li>
            <li aria-hidden="true">/</li>
            <li><Link href="/buying-guides" className="hover:text-ps-text-primary hover:underline">Buying guides</Link></li>
            <li aria-hidden="true">/</li>
            <li aria-current="page" className="font-semibold text-ps-text-primary">{guide.categoryLabel}</li>
          </ol>
        </nav>

        <header className="mt-6 rounded-[2rem] border border-ps-border bg-ps-surface p-7 shadow-xl shadow-slate-900/5 sm:p-10">
          <p className="text-sm font-bold uppercase tracking-[0.22em] text-ps-accent-hover">
            {guide.eyebrow}
          </p>
          <h1 className="mt-4 max-w-4xl text-4xl font-black tracking-tight sm:text-6xl">
            {guide.title}
          </h1>
          <div className="mt-6 max-w-3xl space-y-4">
            {guide.intro.map((paragraph) => (
              <p key={paragraph} className="text-lg leading-8 text-ps-text-secondary">
                {paragraph}
              </p>
            ))}
          </div>
          <div className="mt-7 flex flex-col gap-3 sm:flex-row sm:items-center">
            <Link
              href={guide.categoryHref}
              className="inline-flex min-h-11 items-center justify-center rounded-2xl bg-ps-accent-strong px-5 py-3 font-bold text-white transition hover:bg-ps-accent-hover focus:outline-none focus:ring-2 focus:ring-ps-accent-strong focus:ring-offset-2"
            >
              {guide.categoryLinkLabel}
            </Link>
            <SharePageButton
              title={guide.title}
              text={guide.description}
              path={`/buying-guides/${guide.slug}`}
            />
          </div>
        </header>

        <div className="mt-8 grid gap-6">
          {guide.sections.map((section) => (
            <GuideSectionContent key={section.title} section={section} />
          ))}
        </div>

        <section className="mt-8 rounded-3xl border border-ps-border bg-ps-accent-soft p-6 sm:p-8">
          <p className="text-sm font-bold uppercase tracking-[0.18em] text-ps-accent-hover">How PriceSift fits in</p>
          <h2 className="mt-2 text-2xl font-black tracking-tight">Less time sorting through junk listings</h2>
          <p className="mt-4 max-w-3xl leading-7 text-ps-text-secondary">
            PriceSift tries to keep searches focused on the exact product you asked for and filter out obvious wrong-model, broken, accessory-only, box-only, or otherwise poor matches where the category supports those checks.
          </p>
          <p className="mt-3 max-w-3xl leading-7 text-ps-text-secondary">
            You still make the final call on condition and value. The goal is simply to give you fewer bad listings to inspect first.
          </p>
        </section>

        <section className="mt-8">
          <h2 className="text-2xl font-black tracking-tight">Sources and further reading</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-ps-text-secondary">
            We favor manufacturer documentation, standards bodies, and established specialist references. Where the answer depends on the exact model or condition, the guide says so instead of pretending there is one universal rule.
          </p>
          <div className="mt-5 grid gap-4 md:grid-cols-2">
            {guide.sources.map((source) => (
              <a
                key={source.url}
                href={source.url}
                target="_blank"
                rel="noreferrer"
                className="rounded-2xl border border-ps-border bg-ps-surface p-5 transition hover:border-ps-border-strong hover:bg-ps-accent-soft"
              >
                <p className="text-xs font-bold uppercase tracking-[0.14em] text-ps-neutral">
                  {source.organization}
                </p>
                <h3 className="mt-2 font-bold text-ps-text-primary">{source.label}</h3>
                <p className="mt-2 text-sm leading-6 text-ps-text-secondary">{source.note}</p>
              </a>
            ))}
          </div>
        </section>

        {related.length ? (
          <section className="mt-8">
            <h2 className="text-2xl font-black tracking-tight">Related buying guides</h2>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              {related.map((item) => (
                <Link
                  key={item.slug}
                  href={`/buying-guides/${item.slug}`}
                  className="rounded-2xl border border-ps-border bg-ps-surface p-5 transition hover:border-ps-border-strong hover:bg-ps-accent-soft"
                >
                  <p className="text-xs font-bold uppercase tracking-[0.14em] text-ps-accent-hover">{item.categoryLabel}</p>
                  <p className="mt-2 font-bold text-ps-text-primary">{item.title}</p>
                </Link>
              ))}
            </div>
          </section>
        ) : null}

        <SiteFooter />
      </div>
    </main>
  );
}
