import type { PriceContext } from "@/lib/api";

function money(value: number | null): string {
  return value === null ? "—" : `$${value.toFixed(2)}`;
}

function comparisonLabel(value: number | null): string | null {
  if (value === null) return null;
  const magnitude = Math.abs(value).toFixed(1);
  if (value <= -2) return `${magnitude}% below the recent median`;
  if (value >= 2) return `${magnitude}% above the recent median`;
  return "Near the recent median";
}

export function PriceContextPanel({ context }: { context: PriceContext }) {
  if (!context.product_id) return null;

  const comparison = comparisonLabel(context.current_vs_median_percent);
  const historyProgress = Math.min(context.available_snapshot_count, 3);

  return (
    <section className="mt-6 rounded-3xl border border-cyan-300/15 bg-cyan-300/[0.07] p-5" aria-label="Price context">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan-200/70">Price context</p>
          <h2 className="mt-1 text-xl font-bold text-white">
            {context.current_best_price !== null ? `Best current price: ${money(context.current_best_price)}` : "No safe current price"}
          </h2>
        </div>
        {comparison ? (
          <span className={`w-fit rounded-full border px-3 py-1 text-xs font-semibold ${
            (context.current_vs_median_percent ?? 0) <= -2
              ? "border-emerald-300/25 bg-emerald-300/10 text-emerald-100"
              : (context.current_vs_median_percent ?? 0) >= 2
                ? "border-amber-300/25 bg-amber-300/10 text-amber-100"
                : "border-white/15 bg-white/[0.06] text-slate-200"
          }`}>
            {comparison}
          </span>
        ) : null}
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-3">
        <div className="rounded-2xl bg-slate-950/35 p-4">
          <p className="text-xs uppercase tracking-[0.16em] text-slate-400">Current eligible listings</p>
          <p className="mt-2 text-2xl font-black text-white">{context.current_eligible_count}</p>
          <p className="mt-1 text-xs text-slate-400">
            {context.current_eligible_count > 0
              ? `${money(context.current_low_price)}–${money(context.current_high_price)} delivered`
              : "Scoutly filtered the current marketplace sample safely."}
          </p>
        </div>

        <div className="rounded-2xl bg-slate-950/35 p-4">
          <p className="text-xs uppercase tracking-[0.16em] text-slate-400">Typical recent range</p>
          {context.history_ready ? (
            <>
              <p className="mt-2 text-2xl font-black text-white">
                {money(context.typical_low_price)}–{money(context.typical_high_price)}
              </p>
              <p className="mt-1 text-xs text-slate-400">Recent median {money(context.historical_median_price)}</p>
            </>
          ) : (
            <>
              <p className="mt-2 text-lg font-bold text-slate-200">Building price history</p>
              <p className="mt-1 text-xs text-slate-400">
                {historyProgress}/3 inventory snapshots collected. Scoutly waits for enough observations before calling a range typical.
              </p>
            </>
          )}
        </div>

        <div className="rounded-2xl bg-slate-950/35 p-4">
          <p className="text-xs uppercase tracking-[0.16em] text-slate-400">30-day observations</p>
          <p className="mt-2 text-2xl font-black text-white">{context.snapshot_count}</p>
          <p className="mt-1 text-xs text-slate-400">
            {context.availability_rate !== null
              ? `Safe inventory appeared in ${context.availability_rate.toFixed(1)}% of snapshots.`
              : "This is the first observation for this item."}
          </p>
        </div>
      </div>
    </section>
  );
}
