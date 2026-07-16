import type { ReactNode } from "react";

type Props = {
  children: ReactNode;
  count: number;
  description: string;
  id?: string;
  title: string;
};

export function AdminCollapsibleSection({ children, count, description, id, title }: Props) {
  const entryLabel = count === 1 ? "entry" : "entries";

  return (
    <details id={id} className="group mt-10 scroll-mt-6 rounded-3xl border border-white/10 bg-white/[0.04]">
      <summary className="cursor-pointer list-none p-5 [&::-webkit-details-marker]:hidden">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-2xl font-bold">{title}</h2>
            <p className="mt-1 text-sm text-slate-500">{description}</p>
          </div>
          <div className="flex shrink-0 items-center gap-3">
            <span className="rounded-full border border-white/10 bg-white/[0.06] px-3 py-1 text-xs font-semibold text-slate-300">
              {count} {entryLabel}
            </span>
            <span aria-hidden="true" className="text-lg text-cyan-200 transition-transform group-open:rotate-180">⌄</span>
          </div>
        </div>
      </summary>
      <div className="border-t border-white/10 p-5">{children}</div>
    </details>
  );
}
