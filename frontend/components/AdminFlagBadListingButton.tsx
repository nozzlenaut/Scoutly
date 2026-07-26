"use client";

import { useState } from "react";
import { reportBadResult, type SearchResult } from "@/lib/api";

const reasons = [
  ["wrong_item", "Wrong item"],
  ["accessory_or_part", "Accessory / part"],
  ["partial_or_incomplete", "Partial / incomplete"],
  ["broken_or_for_parts", "Broken / for parts"],
  ["other", "Other"],
] as const;

type Props = {
  result: SearchResult;
  query: string;
  category: string;
  productId?: string;
};

export function AdminFlagBadListingButton({ result, query, category, productId }: Props) {
  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState<"idle" | "saving" | "saved" | "error">("idle");

  async function flag(reason: string) {
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
    } catch {
      setStatus("error");
    }
  }

  if (status === "saved") {
    return (
      <p className="mt-3 rounded-xl border border-emerald-300/20 bg-emerald-300/10 px-3 py-2 text-xs text-emerald-100">
        Flagged for 72 hours. Run the QA search again to refresh the results.
      </p>
    );
  }

  return (
    <div className="mt-3">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="text-xs font-semibold text-rose-200 underline decoration-rose-400/40 underline-offset-4 hover:text-rose-100"
      >
        Flag bad listing
      </button>

      {open ? (
        <div className="mt-2 grid gap-2 rounded-xl border border-rose-300/15 bg-rose-950/20 p-2">
          {reasons.map(([id, label]) => (
            <button
              key={id}
              type="button"
              disabled={status === "saving"}
              onClick={() => flag(id)}
              className="rounded-lg border border-white/10 bg-white/[0.04] px-3 py-2 text-left text-xs text-slate-200 hover:bg-white/[0.08] disabled:cursor-wait disabled:opacity-50"
            >
              {label}
            </button>
          ))}
        </div>
      ) : null}

      {status === "error" ? (
        <p className="mt-2 text-xs text-amber-300">Could not flag this listing. Try again.</p>
      ) : null}
    </div>
  );
}
