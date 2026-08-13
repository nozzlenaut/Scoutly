"use client";

import { useEffect, useState } from "react";
import {
  analyticsOptedOut,
  setAnalyticsOptOut,
} from "@/lib/analyticsOptOut";

export function AdminAnalyticsOptOut() {
  const [excluded, setExcluded] = useState(false);

  useEffect(() => {
    setExcluded(analyticsOptedOut());
  }, []);

  function toggle() {
    const next = !excluded;
    setAnalyticsOptOut(next);
    setExcluded(next);
  }

  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/35 p-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="font-bold text-slate-100">Exclude this browser from PriceSift analytics</p>
          <p className="mt-1 max-w-2xl text-sm leading-6 text-slate-400">
            Turn this on before screenshots, demos, audits, or social posts. Searches and verified outbound clicks from this browser will not be logged until you turn it back off.
          </p>
        </div>
        <button
          type="button"
          onClick={toggle}
          aria-pressed={excluded}
          className={`shrink-0 rounded-2xl px-4 py-2 text-sm font-bold transition ${
            excluded
              ? "bg-emerald-300 text-slate-950 hover:bg-emerald-200"
              : "border border-white/15 bg-white/[0.06] text-slate-100 hover:bg-white/[0.1]"
          }`}
        >
          {excluded ? "Excluded: ON" : "Excluded: OFF"}
        </button>
      </div>
    </div>
  );
}
