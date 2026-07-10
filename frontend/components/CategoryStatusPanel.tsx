import { searchCategories } from "@/lib/categoryCatalog";

export function CategoryStatusPanel() {
  return (
    <section className="w-full rounded-3xl border border-white/10 bg-white/[0.04] p-4 text-left backdrop-blur">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.22em] text-slate-500">Catalog direction</p>
          <p className="mt-1 text-sm text-slate-300">
            Starting with camera bodies and lenses. As categories grow, we can group them under Photography, PC Parts, and more.
          </p>
        </div>
        <div className="flex flex-wrap gap-2 text-xs text-slate-400">
          {searchCategories.map((category) => (
            <span key={category.id} className="rounded-full border border-white/10 bg-slate-950/40 px-3 py-1">
              {category.group}: {category.label}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
