import { categoryStatusItems } from "@/lib/categoryStatus";
import { StatusBadge } from "@/components/StatusBadge";

export function CategoryStatusPanel() {
  return (
    <section className="w-full rounded-3xl border border-white/10 bg-white/[0.06] p-5 text-left shadow-2xl shadow-black/20 backdrop-blur">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.25em] text-slate-500">What&apos;s added</p>
          <h2 className="mt-2 text-2xl font-black text-white">Current Scoutly status</h2>
        </div>
        <p className="max-w-sm text-sm text-slate-400">
          We&apos;ll keep this updated as new item categories and marketplaces go live.
        </p>
      </div>

      <div className="mt-5 grid gap-3">
        {categoryStatusItems.map((item) => (
          <div
            key={item.id}
            className="flex flex-col gap-3 rounded-2xl border border-white/10 bg-slate-950/40 p-4 sm:flex-row sm:items-center sm:justify-between"
          >
            <div>
              <div className="flex items-center gap-3">
                <h3 className="font-semibold text-white">{item.tag}</h3>
                <StatusBadge status={item.status} />
              </div>
              <p className="mt-1 text-sm text-slate-400">{item.description}</p>
            </div>
            <span className="text-sm font-medium text-slate-500">{item.label}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
