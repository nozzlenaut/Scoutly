import Link from "next/link";
import { searchCategories } from "@/lib/categoryCatalog";
import { StatusBadge } from "@/components/StatusBadge";

export function CategoryTabs({ selectedId }: { selectedId?: string }) {
  return (
    <nav aria-label="PriceSift categories" className="w-full overflow-x-auto">
      <div className="flex w-max gap-2 rounded-2xl border border-white/10 bg-white/[0.05] p-2 backdrop-blur sm:w-fit">
        {searchCategories.map((category) => {
          const selected = category.id === selectedId;
          return (
            <Link
              key={category.id}
              href={`/?category=${category.id}`}
              className={`flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium ${
                selected ? "bg-white text-slate-950" : "text-slate-400 hover:text-white"
              }`}
            >
              <span>{category.label}</span>
              <StatusBadge status={category.status} selected={selected} />
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
