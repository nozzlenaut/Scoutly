import { categoryStatusItems } from "@/lib/categoryStatus";
import { StatusBadge } from "@/components/StatusBadge";

export function CategoryTabs() {
  return (
    <nav aria-label="Scoutly category status" className="w-full overflow-x-auto">
      <div className="mx-auto flex w-max gap-2 rounded-2xl border border-white/10 bg-white/[0.05] p-2 backdrop-blur sm:w-fit">
        {categoryStatusItems
          .filter((item) => item.id !== "ebay-gpu")
          .map((item) => (
            <div
              key={item.id}
              className={`flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium ${
                item.status === "active" ? "bg-white text-slate-950" : "text-slate-400"
              }`}
            >
              <span>{item.label}</span>
              <StatusBadge status={item.status} />
            </div>
          ))}
      </div>
    </nav>
  );
}
