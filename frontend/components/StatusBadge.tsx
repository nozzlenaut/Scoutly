import type { CategoryStatus } from "@/lib/categoryStatus";

const statusStyles: Record<CategoryStatus, string> = {
  active: "border-emerald-300/30 bg-emerald-300/10 text-emerald-100",
  "coming-soon": "border-cyan-300/30 bg-cyan-300/10 text-cyan-100",
  planned: "border-white/10 bg-white/[0.06] text-slate-300",
};

const statusLabels: Record<CategoryStatus, string> = {
  active: "Added",
  "coming-soon": "Soon",
  planned: "Planned",
};

export function StatusBadge({ status }: { status: CategoryStatus }) {
  return (
    <span className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${statusStyles[status]}`}>
      {statusLabels[status]}
    </span>
  );
}
