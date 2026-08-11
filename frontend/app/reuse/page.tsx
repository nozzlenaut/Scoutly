import type { Metadata } from "next";
import Link from "next/link";
import { SharePageButton } from "@/components/SharePageButton";
import { SiteFooter } from "@/components/SiteFooter";

export const metadata: Metadata = {
  title: "Repair & Reuse",
  description:
    "A practical starting point for checking whether something can be repaired, finding reliable repair information, handling battery safety, and choosing reuse or recycling when repair does not make sense.",
  alternates: { canonical: "/reuse" },
  robots: { index: true, follow: true },
  openGraph: {
    title: "Repair & Reuse | PriceSift",
    description:
      "Before replacing something, identify it, check good repair information, look for parts, and decide whether repair is practical and safe.",
    url: "/reuse",
  },
  twitter: {
    card: "summary",
    title: "Repair & Reuse | PriceSift",
    description:
      "A practical starting point for repair, reuse, parts, safety, and responsible end-of-life options.",
  },
};

type Source = {
  label: string;
  organization: string;
  url: string;
};

function SourcePair({ sources }: { sources: [Source, Source] }) {
  return (
    <p className="mt-4 text-sm leading-6 text-ps-text-secondary">
      <span className="font-bold text-emerald-900">Sources: </span>
      {sources.map((source, index) => (
        <span key={source.url}>
          {index > 0 ? " · " : ""}
          <a
            href={source.url}
            target="_blank"
            rel="noreferrer"
            className="font-semibold text-emerald-900 underline decoration-emerald-300 underline-offset-4 hover:text-emerald-700"
          >
            {source.organization}: {source.label}
          </a>
        </span>
      ))}
    </p>
  );
}

const repairabilitySources: [Source, Source] = [
  {
    organization: "iFixit",
    label: "Repairability Scoring Rubric v2.3",
    url: "https://www.ifixit.com/Wiki/Repairability_Scoring_Rubric_v2.3",
  },
  {
    organization: "Federal Trade Commission",
    label: "Nixing the Fix",
    url: "https://www.ftc.gov/reports/nixing-fix-ftc-report-congress-repair-restrictions",
  },
];

const rightToRepairSources: [Source, Source] = [
  {
    organization: "The Repair Association",
    label: "Know Your Rights",
    url: "https://www.repair.org/know-your-rights",
  },
  {
    organization: "Federal Trade Commission",
    label: "Right to Repair testimony",
    url: "https://www.ftc.gov/news-events/news/press-releases/2023/04/ftc-testifies-california-state-senate-right-repair",
  },
];

const batterySources: [Source, Source] = [
  {
    organization: "U.S. EPA",
    label: "Lithium-ion battery FAQ",
    url: "https://www.epa.gov/recycle/frequent-questions-lithium-ion-batteries",
  },
  {
    organization: "U.S. Consumer Product Safety Commission",
    label: "Consumer battery safety information",
    url: "https://www.cpsc.gov/Regulations-Laws--Standards/Voluntary-Standards/Topics/Batteries",
  },
];

const communitySources: [Source, Source] = [
  {
    organization: "The Restart Project",
    label: "What we do",
    url: "https://therestartproject.org/about/",
  },
  {
    organization: "Repair Café",
    label: "What is a Repair Café?",
    url: "https://www.repaircafe.org/en/about/",
  },
];

const dataSources: [Source, Source] = [
  {
    organization: "Federal Trade Commission",
    label: "Remove personal information before getting rid of a computer",
    url: "https://consumer.ftc.gov/articles/how-remove-your-personal-information-you-get-rid-your-computer",
  },
  {
    organization: "U.S. EPA",
    label: "Electronics donation and recycling",
    url: "https://www.epa.gov/recycle/electronics-donation-and-recycling",
  },
];

const recyclingSources: [Source, Source] = [
  {
    organization: "U.S. EPA",
    label: "Electronics donation and recycling",
    url: "https://www.epa.gov/recycle/electronics-donation-and-recycling",
  },
  {
    organization: "U.S. Consumer Product Safety Commission",
    label: "Consumer battery safety information",
    url: "https://www.cpsc.gov/Regulations-Laws--Standards/Voluntary-Standards/Topics/Batteries",
  },
];

const identificationSources: [Source, Source] = [
  repairabilitySources[0],
  rightToRepairSources[0],
];

const videoSources: [Source, Source] = [
  {
    organization: "TronicsFix",
    label: "DIY electronics repair resource",
    url: "https://tronicsfix.com/",
  },
  {
    organization: "TronicsFix",
    label: "Official repair video channels",
    url: "https://tronicsfix.com/pages/youtube-channels",
  },
];

export default function RepairReusePage() {
  return (
    <main className="pricesift-public min-h-screen bg-ps-canvas px-4 py-7 text-ps-text-primary sm:px-6 sm:py-10">
      <div className="mx-auto max-w-5xl">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <Link href="/" className="text-2xl font-black tracking-tight text-ps-text-primary">
            PriceSift
          </Link>
          <Link
            href="/buying-guides"
            className="text-sm font-semibold text-emerald-800 hover:text-emerald-950 hover:underline"
          >
            Buying guides
          </Link>
        </div>

        <article className="mx-auto mt-10 max-w-3xl sm:mt-14">
          <header>
            <p className="text-sm font-bold uppercase tracking-[0.18em] text-emerald-800">
              Repair &amp; Reuse
            </p>
            <h1 className="mt-3 text-4xl font-black leading-tight tracking-tight sm:text-5xl">
              Before you replace it, see if it is worth fixing
            </h1>
            <p className="mt-5 text-lg leading-8 text-ps-text-secondary">
              Something being broken does not automatically mean you need to buy another one. Sometimes the repair is simple. Sometimes it is absolutely not. The goal here is to help you figure out which situation you are dealing with before you start ordering parts or taking screws out.
            </p>
            <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center">
              <Link
                href="/#search"
                className="inline-flex min-h-11 items-center justify-center rounded-xl bg-emerald-800 px-5 py-3 font-bold text-white transition hover:bg-emerald-900 focus:outline-none focus:ring-2 focus:ring-emerald-700 focus:ring-offset-2"
              >
                Search PriceSift
              </Link>
              <SharePageButton
                title="Repair & Reuse"
                text="A practical starting point for repair, reuse, and responsible replacement."
                path="/reuse"
                variant="green"
              />
            </div>
          </header>

          <section className="mt-12 border-t border-emerald-200 pt-8">
            <p className="text-sm font-bold uppercase tracking-[0.16em] text-emerald-800">
              First, a safety stop
            </p>
            <h2 className="mt-2 text-2xl font-black tracking-tight sm:text-3xl">
              Some repairs are not a good first DIY project
            </h2>
            <p className="mt-4 text-base leading-7 text-ps-text-secondary sm:text-[17px] sm:leading-8">
              Damaged lithium-ion batteries can create a fire hazard. If a battery is swollen, crushed, punctured, leaking, unusually hot, or otherwise damaged, stop using the device and follow manufacturer or local hazardous-waste guidance instead of casually prying the battery out. Lithium-ion batteries also should not go into normal household trash or curbside recycling.
            </p>
            <SourcePair sources={batterySources} />
          </section>

          <section className="mt-10 sm:mt-12">
            <p className="text-sm font-bold uppercase tracking-[0.14em] text-emerald-800">Step 1</p>
            <h2 className="mt-2 text-2xl font-black tracking-tight sm:text-3xl">Figure out exactly what you have</h2>
            <p className="mt-4 text-base leading-7 text-ps-text-secondary sm:text-[17px] sm:leading-8">
              Find the exact model number, service tag, or other product identifier before looking for a guide or ordering a part. Repair documentation and replacement parts can depend on the exact model or revision, and repairability guidance treats clear product identification as part of finding compatible instructions and parts.
            </p>
            <SourcePair sources={identificationSources} />
          </section>

          <section className="mt-10 sm:mt-12">
            <p className="text-sm font-bold uppercase tracking-[0.14em] text-emerald-800">Step 2</p>
            <h2 className="mt-2 text-2xl font-black tracking-tight sm:text-3xl">Check the manual and good repair information</h2>
            <p className="mt-4 text-base leading-7 text-ps-text-secondary sm:text-[17px] sm:leading-8">
              Repairability is more than whether a product can physically come apart. Access to service documentation, replacement parts, tools, diagnostics, and sometimes software can determine whether a repair is realistic. Start with the manufacturer, then use an established repair resource when you need a teardown or step-by-step procedure.
            </p>
            <SourcePair sources={repairabilitySources} />
            <ul className="mt-4 list-disc space-y-2 pl-6 text-base leading-7 text-ps-text-secondary">
              <li>
                <a href="https://www.ifixit.com/" target="_blank" rel="noreferrer" className="font-semibold text-emerald-900 underline underline-offset-4">
                  Browse iFixit repair guides
                </a>
              </li>
              <li>
                <Link href="/buying-guides" className="font-semibold text-emerald-900 underline underline-offset-4">
                  Browse PriceSift buying guides
                </Link>
              </li>
            </ul>
          </section>

          <section className="mt-10 sm:mt-12">
            <p className="text-sm font-bold uppercase tracking-[0.14em] text-emerald-800">Step 3</p>
            <h2 className="mt-2 text-2xl font-black tracking-tight sm:text-3xl">Check whether you can actually get the parts</h2>
            <p className="mt-4 text-base leading-7 text-ps-text-secondary sm:text-[17px] sm:leading-8">
              A repair can be mechanically possible and still be impractical if the needed part, tool, documentation, diagnostic access, or software support is unavailable. Check the exact part number and revision, and be careful with parts that are visually similar but not actually compatible.
            </p>
            <SourcePair sources={repairabilitySources} />
          </section>

          <section className="mt-10 sm:mt-12">
            <p className="text-sm font-bold uppercase tracking-[0.14em] text-emerald-800">Step 4</p>
            <h2 className="mt-2 text-2xl font-black tracking-tight sm:text-3xl">If you are not comfortable doing it, get some help</h2>
            <p className="mt-4 text-base leading-7 text-ps-text-secondary sm:text-[17px] sm:leading-8">
              Community repair groups exist specifically to help people work on broken items with experienced volunteers. The Restart Project runs community electronics repair events, and Repair Café groups cover electronics along with many other household items. Availability and the kinds of repairs supported vary by local event, so check before hauling your broken television across town.
            </p>
            <SourcePair sources={communitySources} />
            <ul className="mt-4 list-disc space-y-2 pl-6 text-base leading-7 text-ps-text-secondary">
              <li>
                <a href="https://therestartproject.org/" target="_blank" rel="noreferrer" className="font-semibold text-emerald-900 underline underline-offset-4">
                  The Restart Project
                </a>
              </li>
              <li>
                <a href="https://www.repaircafe.org/en/visit/" target="_blank" rel="noreferrer" className="font-semibold text-emerald-900 underline underline-offset-4">
                  Find a Repair Café
                </a>
              </li>
            </ul>
          </section>

          <section className="mt-10 sm:mt-12">
            <p className="text-sm font-bold uppercase tracking-[0.14em] text-emerald-800">Step 5</p>
            <h2 className="mt-2 text-2xl font-black tracking-tight sm:text-3xl">Learn from somebody taking the same kind of thing apart</h2>
            <p className="mt-4 text-base leading-7 text-ps-text-secondary sm:text-[17px] sm:leading-8">
              A written guide is not always the easiest way to understand a repair. TronicsFix is one useful place to browse electronics-repair videos and DIY material, especially around game consoles and other consumer electronics. Treat any video as a reference, not proof that your exact failure is identical.
            </p>
            <SourcePair sources={videoSources} />
          </section>

          <section className="mt-12 border-t border-emerald-200 pt-8">
            <p className="text-sm font-bold uppercase tracking-[0.16em] text-emerald-800">
              Right to Repair, very briefly
            </p>
            <h2 className="mt-2 text-2xl font-black tracking-tight sm:text-3xl">What does it mean?</h2>
            <p className="mt-4 text-base leading-7 text-ps-text-secondary sm:text-[17px] sm:leading-8">
              In practical terms, Right to Repair efforts focus on access to things such as replacement parts, repair instructions, diagnostic tools, and software needed to perform repairs. The exact legal rights are not universal. They vary by location, product type, product age, and the law currently in effect.
            </p>
            <p className="mt-3 text-base leading-7 text-ps-text-secondary sm:text-[17px] sm:leading-8">
              PriceSift is not going to maintain a pretend law database that becomes wrong six weeks later. For current U.S. state information, use a live repair-rights tracker and verify the details that apply to your product.
            </p>
            <SourcePair sources={rightToRepairSources} />
            <p className="mt-4">
              <a
                href="https://www.repair.org/know-your-rights"
                target="_blank"
                rel="noreferrer"
                className="font-bold text-emerald-900 underline decoration-emerald-300 underline-offset-4 hover:text-emerald-700"
              >
                Check current repair rights →
              </a>
            </p>
          </section>

          <section className="mt-12 border-t border-emerald-200 pt-8">
            <h2 className="text-2xl font-black tracking-tight sm:text-3xl">If you sell, donate, or recycle electronics</h2>
            <p className="mt-4 text-base leading-7 text-ps-text-secondary sm:text-[17px] sm:leading-8">
              Devices can contain personal information. Before selling, donating, or recycling a computer or phone, back up what you need and follow the device or platform guidance for removing your data and accounts.
            </p>
            <SourcePair sources={dataSources} />
            <p className="mt-6 text-base leading-7 text-ps-text-secondary sm:text-[17px] sm:leading-8">
              If a device cannot be repaired or reused, use an electronics or battery collection option that accepts that type of item. Lithium batteries need separate handling and should not be put in normal household trash or curbside recycling.
            </p>
            <SourcePair sources={recyclingSources} />
          </section>

          <section className="mt-12 border-t border-emerald-200 pt-8">
            <h2 className="text-2xl font-black tracking-tight sm:text-3xl">If repair just does not make sense</h2>
            <p className="mt-4 text-base leading-7 text-ps-text-secondary sm:text-[17px] sm:leading-8">
              Sometimes the part is unavailable. Sometimes the repair costs more than the item is worth to you. Sometimes the damage or safety risk is simply beyond what you want to take on.
            </p>
            <p className="mt-3 text-base leading-7 text-ps-text-secondary sm:text-[17px] sm:leading-8">
              That is where buying used can be the next option. PriceSift does not claim to calculate the environmental impact of a purchase. It just tries to make it easier to find a clean secondhand match when replacement is the practical choice.
            </p>
            <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center">
              <Link
                href="/#search"
                className="inline-flex min-h-11 items-center justify-center rounded-xl bg-emerald-800 px-5 py-3 font-bold text-white transition hover:bg-emerald-900"
              >
                Search used instead
              </Link>
              <Link
                href="/buying-guides"
                className="font-bold text-emerald-900 underline decoration-emerald-300 underline-offset-4 hover:text-emerald-700"
              >
                Read the buying guides
              </Link>
            </div>
          </section>
        </article>

        <SiteFooter />
      </div>
    </main>
  );
}
