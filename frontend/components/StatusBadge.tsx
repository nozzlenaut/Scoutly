type StatusBadgeProps = {
  status: "active" | "lab" | "planned" | "coming-soon";
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

export function StatusBadge({ status }: StatusBadgeProps) {
  return <span className={`rounded-full border px-2 py-0.5 text-[11px] font-semibold ${classes[status]}`}>{labels[status]}</span>;
}
