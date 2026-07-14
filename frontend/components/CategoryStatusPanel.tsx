import { allCategories } from "@/lib/categoryCatalog";
import { StatusBadge } from "@/components/StatusBadge";

export function CategoryStatusPanel() {
  return (
    <section className="w-full rounded-3xl border border-white/10 bg-white/[0.04] p-4 text-left backdrop-blur">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.22em] text-slate-500">
            Category status
          </p>
          <p className="mt-1 text-sm text-slate-300">
            Cameras, GPUs, and Consoles are active. RAM is a new
            specification-builder lab, LEGO remains an exact set-number lab, and
            Lenses are paused until results are clean enough to trust.
          </p>
        </div>
        <div className="flex flex-wrap gap-2 text-xs text-slate-400">
          {allCategories.map((category) => (
            <span
              key={category.id}
              className="flex items-center gap-2 rounded-full border border-white/10 bg-slate-950/40 px-3 py-1"
            >
              <span>
                {category.group}: {category.label}
              </span>
              <StatusBadge status={category.status} />
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
