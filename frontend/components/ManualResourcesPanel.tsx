import { getManualResources } from "@/lib/manualResources";

type Props = {
  query: string;
  category: string;
  productId?: string;
};

export function ManualResourcesPanel({ query, category, productId }: Props) {
  const resources = getManualResources({ query, category, productId });
  if (resources.length === 0) return null;

  return (
    <section
      className="mt-8 rounded-3xl border border-emerald-300/25 bg-emerald-300/[0.08] p-5 sm:p-6"
      aria-label="Manuals and product support"
    >
      <p className="text-xs font-bold uppercase tracking-[0.2em] text-emerald-200">
        Keep it in use
      </p>
      <h2 className="mt-2 text-2xl font-black text-white">
        Already own one? Find the manual.
      </h2>
      <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-300">
        Setup instructions, maintenance guidance, and the right troubleshooting
        steps can keep a good product working longer. PriceSift links to official
        resources when a dependable match is available and provides a
        model-specific ManualsLib search as a fallback.
      </p>

      <div className="mt-5 grid gap-3 md:grid-cols-2">
        {resources.map((resource) => (
          <a
            key={`${resource.source}:${resource.url}`}
            href={resource.url}
            target="_blank"
            rel="noreferrer"
            className="rounded-2xl border border-white/10 bg-white/[0.06] p-4 transition hover:border-emerald-300/35 hover:bg-emerald-300/[0.1]"
          >
            <span className="block text-xs font-semibold uppercase tracking-[0.16em] text-emerald-200">
              {resource.source === "official" ? "Official resource" : "Third-party library"}
            </span>
            <span className="mt-1 block font-bold text-white">{resource.label} →</span>
            <span className="mt-2 block text-xs leading-5 text-slate-400">
              {resource.description}
            </span>
          </a>
        ))}
      </div>

      <p className="mt-4 text-xs leading-5 text-slate-400">
        PriceSift does not host, scrape, or rewrite manuals. Confirm the model
        number shown on the product before following instructions.
      </p>
    </section>
  );
}
