"use client";

import { useEffect, useRef, useState } from "react";

type ShareStatus = "idle" | "shared" | "copied" | "error";

export function SharePageButton({
  title,
  text,
  path,
  variant = "blue",
}: {
  title: string;
  text: string;
  path: string;
  variant?: "blue" | "green";
}) {
  const [status, setStatus] = useState<ShareStatus>("idle");
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (timerRef.current !== null) window.clearTimeout(timerRef.current);
    };
  }, []);

  function resetLater() {
    if (timerRef.current !== null) window.clearTimeout(timerRef.current);
    timerRef.current = window.setTimeout(() => setStatus("idle"), 2400);
  }

  async function copyLink(url: string) {
    await navigator.clipboard.writeText(url);
    setStatus("copied");
    resetLater();
  }

  async function share() {
    const url = new URL(path, window.location.origin).toString();

    try {
      if (navigator.share) {
        await navigator.share({ title: `${title} | PriceSift`, text, url });
        setStatus("shared");
        resetLater();
        return;
      }

      await copyLink(url);
    } catch (error) {
      if (error instanceof DOMException && error.name === "AbortError") return;

      try {
        await copyLink(url);
      } catch {
        setStatus("error");
        resetLater();
      }
    }
  }

  const label =
    status === "shared"
      ? "Shared"
      : status === "copied"
        ? "Link copied"
        : status === "error"
          ? "Couldn’t copy"
          : "Share this page";

  const classes =
    variant === "green"
      ? "inline-flex min-h-11 items-center justify-center rounded-2xl border border-emerald-300 bg-white px-5 py-3 text-sm font-bold text-emerald-900 transition hover:bg-emerald-100 focus:outline-none focus:ring-2 focus:ring-emerald-700 focus:ring-offset-2"
      : "inline-flex min-h-11 items-center justify-center rounded-2xl border border-ps-border bg-ps-control px-5 py-3 text-sm font-bold text-ps-text-primary transition hover:border-ps-border-strong hover:bg-ps-accent-soft focus:outline-none focus:ring-2 focus:ring-ps-accent-strong focus:ring-offset-2";

  return (
    <div>
      <button type="button" onClick={share} className={classes}>
        {label}
      </button>
      <span className="sr-only" role="status" aria-live="polite">
        {status === "idle" ? "" : label}
      </span>
    </div>
  );
}
