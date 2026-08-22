import type { SearchDiagnostics } from "@/lib/api";

type ReasonBucket = {
  label: string;
  count: number;
};

function reasonBucket(reason: string): string {
  const value = reason.toLowerCase();

  if (
    value.includes("bad condition") ||
    value.includes("hardware defect") ||
    value.includes("for parts") ||
    value.includes("repair") ||
    value.includes("defective") ||
    value.includes("not working") ||
    value.includes("untested") ||
    value.includes("as-is") ||
    value.includes("as is") ||
    value.includes("no power")
  ) {
    return "Broken, parts, or risky condition";
  }

  if (
    value.includes("accessory") ||
    value.includes("controller listing") ||
    value.includes("without console")
  ) {
    return "Accessory or incomplete listing";
  }

  if (
    value.includes("model") ||
    value.includes("required term") ||
    value.includes("form factor") ||
    value.includes("conflict")
  ) {
    return "Wrong model or variant";
  }

  if (value.includes("seller-defined variation")) {
    return "Ambiguous variation listing";
  }

  if (value.includes("feedback")) {
    return "Seller quality check";
  }

  if (value.includes("manual filter")) {
    return "Known bad match";
  }

  return "Other low-confidence match";
}

function summarizeReasons(reasons: Record<string, number>): ReasonBucket[] {
  const buckets = new Map<string, number>();

  for (const [reason, count] of Object.entries(reasons)) {
    if (!Number.isFinite(count) || count <= 0) continue;
    const label = reasonBucket(reason);
    buckets.set(label, (buckets.get(label) || 0) + count);
  }

  return Array.from(buckets.entries())
    .map(([label, count]) => ({ label, count }))
    .sort((a, b) => b.count - a.count);
}

export function FilterTransparencyPanel({
  diagnostics,
  resultCount,
}: {
  diagnostics: SearchDiagnostics;
  resultCount: number;
}) {
  const checked = diagnostics.fixed_price_candidates;
  const filtered = diagnostics.fixed_price_filtered;
  const eligible = diagnostics.fixed_price_eligible;
  const duplicates = diagnostics.fixed_price_duplicates_removed;
  const reasons = summarizeReasons(diagnostics.fixed_price_rejection_reasons);

  if (checked <= 0 && filtered <= 0 && eligible <= 0) return null;

  return (
    <section
      className="mt-6 rounded-3xl border border-ps-border bg-ps-surface p-5 sm:p-6"
      aria-label="PriceSift filtering breakdown"
    >
      <p className="text-xs font-bold uppercase tracking-[0.2em] text-ps-accent-hover">
        What PriceSift filtered
      </p>
      <h2 className="mt-2 text-2xl font-black text-ps-text-primary">
        {checked} current candidates checked · {filtered} filtered out
      </h2>
      <p className="mt-3 max-w-4xl text-sm leading-6 text-ps-text-secondary sm:text-base">
        PriceSift checks current marketplace candidates against the exact product,
        removes obvious bad matches when detectable, de-duplicates the survivors,
        and keeps the shortlist focused on eligible listings.
      </p>

      <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-2xl bg-ps-control p-4">
          <p className="text-xs uppercase tracking-[0.16em] text-ps-neutral">Candidates checked</p>
          <p className="mt-2 text-2xl font-black text-ps-text-primary">{checked}</p>
        </div>
        <div className="rounded-2xl bg-ps-control p-4">
          <p className="text-xs uppercase tracking-[0.16em] text-ps-neutral">Filtered out</p>
          <p className="mt-2 text-2xl font-black text-ps-text-primary">{filtered}</p>
        </div>
        <div className="rounded-2xl bg-ps-control p-4">
          <p className="text-xs uppercase tracking-[0.16em] text-ps-neutral">Eligible</p>
          <p className="mt-2 text-2xl font-black text-ps-text-primary">{eligible}</p>
        </div>
        <div className="rounded-2xl bg-ps-control p-4">
          <p className="text-xs uppercase tracking-[0.16em] text-ps-neutral">Shown here</p>
          <p className="mt-2 text-2xl font-black text-ps-text-primary">{resultCount}</p>
          {duplicates > 0 ? (
            <p className="mt-1 text-xs text-ps-neutral">{duplicates} duplicate{duplicates === 1 ? "" : "s"} also removed</p>
          ) : null}
        </div>
      </div>

      {reasons.length > 0 ? (
        <div className="mt-5 rounded-2xl border border-ps-border bg-ps-accent-soft p-4 sm:p-5">
          <div className="flex flex-wrap items-end justify-between gap-2">
            <h3 className="font-bold text-ps-text-primary">Top detected rejection reasons</h3>
            <p className="text-xs text-ps-neutral">One listing can trigger more than one check.</p>
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            {reasons.map((reason) => (
              <span
                key={reason.label}
                className="rounded-full border border-ps-border bg-ps-surface px-3 py-2 text-sm text-ps-text-secondary"
              >
                <strong className="text-ps-text-primary">{reason.count}</strong> {reason.label}
              </span>
            ))}
          </div>
        </div>
      ) : null}

      <p className="mt-4 text-xs leading-5 text-ps-neutral">
        This is a live inventory sample, not a claim that every bad listing can be detected. Counts can change as marketplace inventory changes.
      </p>
    </section>
  );
}
