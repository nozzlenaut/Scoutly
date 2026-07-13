type StatusBadgeProps = {
  status: "active" | "lab" | "planned" | "coming-soon";
  selected?: boolean;
};

const labels = {
  active: "Active",
  lab: "Lab",
  planned: "Planned",
  "coming-soon": "Soon",
};

const classes = {
  active: "border-emerald-300/30 bg-emerald-300/10 text-emerald-100",
  lab: "border-cyan-300/30 bg-cyan-300/10 text-cyan-100",
  planned: "border-slate-400/20 bg-slate-400/10 text-slate-300",
  "coming-soon": "border-amber-300/30 bg-amber-300/10 text-amber-100",
};

const selectedClasses = {
  active: "border-emerald-700 bg-emerald-100 text-emerald-950",
  lab: "border-cyan-700 bg-cyan-100 text-cyan-950",
  planned: "border-slate-600 bg-slate-200 text-slate-950",
  "coming-soon": "border-amber-700 bg-amber-100 text-amber-950",
};

export function StatusBadge({ status, selected = false }: StatusBadgeProps) {
  return (
    <span
      className={`rounded-full border px-2 py-0.5 text-[11px] font-semibold ${selected ? selectedClasses[status] : classes[status]}`}
    >
      {labels[status]}
    </span>
  );
}
