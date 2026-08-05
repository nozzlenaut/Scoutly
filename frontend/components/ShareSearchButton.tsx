"use client";

import { useState } from "react";

type Props = {
  label: string;
  bestPrice?: number | null;
  theme?: "dark" | "light";
};

export function ShareSearchButton({ label, bestPrice, theme = "dark" }: Props) {
  const [status, setStatus] = useState<"idle" | "shared" | "copied" | "error">("idle");

  async function share() {
    const url = window.location.href;
    const priceText = bestPrice == null ? "" : ` Best clean price: $${bestPrice.toFixed(2)}.`;
    const text = `PriceSift results for ${label}.${priceText}`;

    try {
      if (navigator.share) {
        await navigator.share({ title: `${label} prices | PriceSift`, text, url });
        setStatus("shared");
      } else {
        await navigator.clipboard.writeText(`${text} ${url}`);
        setStatus("copied");
      }
    } catch (error) {
      if (error instanceof DOMException && error.name === "AbortError") return;
      try {
        await navigator.clipboard.writeText(`${text} ${url}`);
        setStatus("copied");
      } catch {
        setStatus("error");
      }
    }
    window.setTimeout(() => setStatus("idle"), 2400);
  }

  const buttonLabel =
    status === "copied" ? "Link copied" : status === "shared" ? "Shared" : status === "error" ? "Copy failed" : "Share search";

  return (
    <button
      type="button"
      onClick={share}
      className={theme === "light" ? "rounded-2xl border border-ps-border bg-ps-control px-4 py-2 text-sm font-semibold text-ps-text-primary transition hover:border-ps-border-strong hover:bg-ps-accent-soft" : "rounded-2xl border border-white/15 bg-white/[0.06] px-4 py-2 text-sm font-semibold text-slate-100 transition hover:bg-white/[0.1]"}
    >
      {buttonLabel}
    </button>
  );
}
