"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { reportBadResult, type SearchResult } from "@/lib/api";

const REASONS = [
  { id: "wrong_item", label: "Wrong item" },
  { id: "accessory_or_part", label: "Accessory / part" },
  { id: "partial_or_incomplete", label: "Partial / incomplete" },
  { id: "broken_or_for_parts", label: "Broken / for parts" },
  { id: "other", label: "Other" },
];

type Props = {
  result: SearchResult;
  query: string;
  category: string;
  productId?: string;
};

export function ReportBadResultButton({ result, query, category, productId }: Props) {
  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState<"idle" | "saving" | "saved" | "error">("idle");
  const router = useRouter();

  async function submit(reason: string) {
    setStatus("saving");
    try {
      await reportBadResult({
        url: result.url,
        title: result.title,
        provider: result.provider,
        category,
        product_id: productId,
        query,
        reason,
      });
      setStatus("saved");
      setOpen(false);
      router.refresh();
      window.setTimeout(() => {
        window.location.reload();
      }, 450);
    } catch {
      setStatus("error");
    }
  }

  if (status === "saved") {
    return (
      <p className="mt-3 rounded-2xl border border-emerald-300/20 bg-emerald-300/10 px-4 py-3 text-sm text-emerald-100">
        Thanks — Scoutly will hide this result for this item for 72 hours. Refreshing results...
      </p>
    );
  }

  return (
    <div className="mt-3">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="text-sm font-medium text-slate-400 underline decoration-slate-600 underline-offset-4 transition hover:text-slate-200"
      >
        Report bad result
      </button>

      {open ? (
        <div className="mt-3 rounded-2xl border border-white/10 bg-slate-950/95 p-3 shadow-xl shadow-black/30">
          <p className="mb-2 text-xs text-slate-400">What is wrong with this listing?</p>
          <div className="grid gap-2 sm:grid-cols-2">
            {REASONS.map((reason) => (
              <button
                key={reason.id}
                type="button"
                disabled={status === "saving"}
                onClick={() => submit(reason.id)}
                className="rounded-xl border border-white/10 bg-white/[0.04] px-3 py-2 text-left text-sm text-slate-200 transition hover:bg-white/[0.08] disabled:cursor-wait disabled:opacity-60"
              >
                {reason.label}
              </button>
            ))}
          </div>
        </div>
      ) : null}

      {status === "error" ? (
        <p className="mt-2 text-xs text-amber-300">Could not save that report. Try again after refresh.</p>
      ) : null}
    </div>
  );
}
