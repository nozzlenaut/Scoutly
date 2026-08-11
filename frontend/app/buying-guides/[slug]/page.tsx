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
    <section className="mt-10 sm:mt-12">
      <h2 className="text-2xl font-black tracking-tight text-ps-text-primary sm:text-3xl">
        {section.title}
      </h2>

      {section.paragraphs?.map((paragraph) => (
        <p
          key={paragraph}
          className="mt-4 text-base leading-7 text-ps-text-secondary sm:text-[17px] sm:leading-8"
        >
          {paragraph}
        </p>
      ))}

      {section.bullets ? (
        <ul className="mt-5 list-disc space-y-2 pl-6 text-base leading-7 text-ps-text-secondary sm:text-[17px] sm:leading-8">
          {section.bullets.map((bullet) => (
            <li key={bullet}>{bullet}</li>
          ))}
        </ul>
      ) : null}

      {section.table ? (
        <div className="-mx-4 mt-6 overflow-x-auto px-4 sm:mx-0 sm:px-0">
          <table className="w-full min-w-[520px] border-collapse text-left text-sm">
            <thead>
              <tr className="border-b-2 border-ps-border-strong text-ps-text-primary">
                {section.table.headers.map((header) => (
                  <th key={header} scope="col" className="px-3 py-3 font-bold sm:px-4">
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {section.table.rows.map((row) => (
                <tr key={row.join(":")} className="border-b border-ps-border">
                  {row.map((cell, index) =>
                    index === 0 ? (
                      <th key={cell} scope="row" className="px-3 py-3 font-semibold text-ps-text-primary sm:px-4">
                        {cell}
                      </th>
                    ) : (
                      <td key={cell} className="px-3 py-3 text-ps-text-secondary sm:px-4">
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
        <p className="mt-5 border-l-2 border-ps-accent-strong pl-4 text-sm leading-6 text-ps-text-secondary">
          {section.note}
        </p>
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
    <main className="pricesift-public min-h-screen bg-ps-canvas px-4 py-7 text-ps-text-primary sm:px-6 sm:py-10">
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
              <li>
                <Link href="/" className="hover:text-ps-text-primary hover:underline">
                  Home
                </Link>
              </li>
              <li aria-hidden="true">/</li>
              <li>
                <Link href="/buying-guides" className="hover:text-ps-text-primary hover:underline">
                  Buying guides
                </Link>
              </li>
              <li aria-hidden="true">/</li>
              <li aria-current="page" className="font-semibold text-ps-text-primary">
                {guide.categoryLabel}
              </li>
            </ol>
          </nav>

          <header className="mt-7 sm:mt-9">
            <p className="text-sm font-bold uppercase tracking-[0.18em] text-ps-accent-hover">
              {guide.eyebrow}
            </p>
            <h1 className="mt-3 text-4xl font-black leading-tight tracking-tight sm:text-5xl">
              {guide.title}
            </h1>
            <div className="mt-5 space-y-4">
              {guide.intro.map((paragraph) => (
                <p key={paragraph} className="text-lg leading-8 text-ps-text-secondary">
                  {paragraph}
                </p>
              ))}
            </div>
            <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center">
              <Link
                href={guide.categoryHref}
                className="inline-flex min-h-11 items-center justify-center rounded-xl bg-ps-accent-strong px-5 py-3 font-bold text-white transition hover:bg-ps-accent-hover focus:outline-none focus:ring-2 focus:ring-ps-accent-strong focus:ring-offset-2"
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

          {guide.sections.map((section) => (
            <GuideSectionContent key={section.title} section={section} />
          ))}

          <section className="mt-12 border-t border-ps-border pt-8">
            <h2 className="text-2xl font-black tracking-tight">How PriceSift fits in</h2>
            <p className="mt-4 text-base leading-7 text-ps-text-secondary sm:text-[17px] sm:leading-8">
              PriceSift tries to keep searches focused on the exact product you asked for and filter out obvious wrong-model, broken, accessory-only, box-only, or otherwise poor matches where the category supports those checks.
            </p>
            <p className="mt-3 text-base leading-7 text-ps-text-secondary sm:text-[17px] sm:leading-8">
              You still make the final call on condition and value. The goal is simply to give you fewer bad listings to inspect first.
            </p>
          </section>

          <section className="mt-12 border-t border-ps-border pt-8">
            <h2 className="text-2xl font-black tracking-tight">Sources and further reading</h2>
            <p className="mt-3 text-sm leading-6 text-ps-text-secondary">
              We favor manufacturer documentation, standards bodies, and established specialist references. Where the answer depends on the exact model or condition, the guide says so instead of pretending there is one universal rule.
            </p>
            <ul className="mt-5 space-y-5">
              {guide.sources.map((source) => (
                <li key={source.url}>
                  <a
                    href={source.url}
                    target="_blank"
                    rel="noreferrer"
                    className="font-bold text-ps-text-primary underline decoration-ps-border-strong underline-offset-4 hover:text-ps-accent-hover"
                  >
                    {source.organization}: {source.label}
                  </a>
                  <p className="mt-1 text-sm leading-6 text-ps-text-secondary">{source.note}</p>
                </li>
              ))}
            </ul>
          </section>

          {related.length ? (
            <section className="mt-12 border-t border-ps-border pt-8">
              <h2 className="text-2xl font-black tracking-tight">Related buying guides</h2>
              <ul className="mt-4 space-y-3">
                {related.map((item) => (
                  <li key={item.slug}>
                    <Link
                      href={`/buying-guides/${item.slug}`}
                      className="font-bold text-ps-accent-hover underline decoration-ps-border-strong underline-offset-4 hover:text-ps-text-primary"
                    >
                      {item.title}
                    </Link>
                  </li>
                ))}
              </ul>
            </section>
          ) : null}
        </article>

        <SiteFooter />
      </div>
    </main>
  );
}
