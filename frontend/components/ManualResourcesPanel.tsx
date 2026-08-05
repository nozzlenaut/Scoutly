import { getManualResources } from "@/lib/manualResources";

type Props = {
  query: string;
  category: string;
  productId?: string;
  theme?: "dark" | "light";
};

export function ManualResourcesPanel({ query, category, productId, theme = "dark" }: Props) {
  const resources = getManualResources({ query, category, productId });
  if (resources.length === 0) return null;

  return (
    <section
      className={theme === "light" ? "mt-8 rounded-3xl border border-ps-border bg-ps-surface p-5 sm:p-6" : "mt-8 rounded-3xl border border-emerald-300/25 bg-emerald-300/[0.08] p-5 sm:p-6"}
      aria-label="Manuals and product support"
    >
      <p className={theme === "light" ? "text-xs font-bold uppercase tracking-[0.2em] text-ps-success" : "text-xs font-bold uppercase tracking-[0.2em] text-emerald-200"}>
        Keep it in use
      </p>
      <h2 className={theme === "light" ? "mt-2 text-2xl font-black text-ps-text-primary" : "mt-2 text-2xl font-black text-white"}>
        Already own one? Find the manual.
      </h2>
      <p className={theme === "light" ? "mt-3 max-w-3xl text-sm leading-6 text-ps-text-secondary" : "mt-3 max-w-3xl text-sm leading-6 text-slate-300"}>
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
            className={theme === "light" ? "rounded-2xl border border-ps-border bg-ps-control p-4 transition hover:border-ps-border-strong hover:bg-ps-accent-soft" : "rounded-2xl border border-white/10 bg-white/[0.06] p-4 transition hover:border-emerald-300/35 hover:bg-emerald-300/[0.1]"}
          >
            <span className={theme === "light" ? "block text-xs font-semibold uppercase tracking-[0.16em] text-ps-success" : "block text-xs font-semibold uppercase tracking-[0.16em] text-emerald-200"}>
              {resource.source === "official" ? "Official resource" : "Third-party library"}
            </span>
            <span className={theme === "light" ? "mt-1 block font-bold text-ps-text-primary" : "mt-1 block font-bold text-white"}>{resource.label} →</span>
            <span className={theme === "light" ? "mt-2 block text-xs leading-5 text-ps-neutral" : "mt-2 block text-xs leading-5 text-slate-400"}>
              {resource.description}
            </span>
          </a>
        ))}
      </div>

      <p className={theme === "light" ? "mt-4 text-xs leading-5 text-ps-neutral" : "mt-4 text-xs leading-5 text-slate-400"}>
        PriceSift does not host, scrape, or rewrite manuals. Confirm the model
        number shown on the product before following instructions.
      </p>
    </section>
  );
}
