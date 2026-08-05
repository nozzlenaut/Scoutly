"use client";

import { FormEvent, useState } from "react";
import { submitBetaFeedback } from "@/lib/api";

const CATEGORIES = ["General", "Cameras", "GPUs", "RAM", "CPUs", "Consoles", "LEGO"];

export function BetaFeedbackForm({ theme = "dark" }: { theme?: "dark" | "light" }) {
  const [status, setStatus] = useState<"idle" | "saving" | "saved" | "error">("idle");
  const light = theme === "light";
  const fieldClasses = light
    ? "border-ps-border bg-ps-control text-ps-text-primary focus:border-ps-accent-strong focus:ring-2 focus:ring-ps-accent"
    : "border-white/10 bg-slate-950 text-white focus:border-cyan-300/60";

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    setStatus("saving");
    try {
      await submitBetaFeedback({
        feedback_type: String(data.get("feedback_type") || "general"),
        category: String(data.get("category") || "general").toLowerCase(),
        message: String(data.get("message") || ""),
        email: String(data.get("email") || "") || undefined,
        page_url: window.location.href,
        website: String(data.get("website") || "") || undefined,
      });
      form.reset();
      setStatus("saved");
    } catch {
      setStatus("error");
    }
  }

  if (status === "saved") {
    return (
      <div className={`rounded-3xl border p-6 ${light ? "border-ps-success/40 bg-emerald-50 text-ps-text-primary" : "border-emerald-300/25 bg-emerald-300/10 text-emerald-50"}`}>
        <h2 className="text-2xl font-bold">Feedback saved</h2>
        <p className={`mt-2 text-sm leading-6 ${light ? "text-ps-text-secondary" : "text-emerald-100/90"}`}>Thanks for helping test PriceSift. Your submission is saved to the private feedback inbox for review.</p>
        <button type="button" onClick={() => setStatus("idle")} className={`mt-4 rounded-2xl px-4 py-2 font-semibold ${light ? "bg-ps-accent-strong text-white hover:bg-ps-accent-hover" : "bg-white text-slate-950"}`}>Send another</button>
      </div>
    );
  }

  return (
    <form onSubmit={submit} className={`rounded-3xl border p-6 ${light ? "border-ps-border bg-ps-surface" : "border-white/10 bg-white/[0.05]"}`}>
      <div className="grid gap-5 sm:grid-cols-2">
        <label className={`text-sm ${light ? "text-ps-text-secondary" : "text-slate-300"}`}>
          Feedback type
          <select name="feedback_type" className={`mt-2 w-full rounded-2xl border px-4 py-3 ${fieldClasses}`}>
            <option value="bad_result">Bad or suspicious result</option>
            <option value="missing_product">Missing product</option>
            <option value="usability">Something was confusing</option>
            <option value="feature">Feature idea</option>
            <option value="general">General feedback</option>
          </select>
        </label>
        <label className={`text-sm ${light ? "text-ps-text-secondary" : "text-slate-300"}`}>
          Category
          <select name="category" className={`mt-2 w-full rounded-2xl border px-4 py-3 ${fieldClasses}`}>
            {CATEGORIES.map((category) => <option key={category} value={category}>{category}</option>)}
          </select>
        </label>
      </div>
      <label className={`mt-5 block text-sm ${light ? "text-ps-text-secondary" : "text-slate-300"}`}>
        What happened, or what should change?
        <textarea name="message" required minLength={5} maxLength={2000} rows={7} placeholder="Include the search you tried and what looked wrong." className={`mt-2 w-full rounded-2xl border px-4 py-3 outline-none placeholder:text-ps-text-muted ${fieldClasses}`} />
      </label>
      <label className={`mt-5 block text-sm ${light ? "text-ps-text-secondary" : "text-slate-300"}`}>
        Email <span className={light ? "text-ps-neutral" : "text-slate-500"}>(optional, only if you want a reply)</span>
        <input name="email" type="email" maxLength={254} className={`mt-2 w-full rounded-2xl border px-4 py-3 outline-none ${fieldClasses}`} />
      </label>
      <label className="hidden" aria-hidden="true">Website<input name="website" tabIndex={-1} autoComplete="off" /></label>
      <div className="mt-5 flex flex-wrap items-center gap-4">
        <button disabled={status === "saving"} className={`rounded-2xl px-5 py-3 font-bold transition disabled:cursor-wait disabled:opacity-60 ${light ? "bg-ps-accent-strong text-white hover:bg-ps-accent-hover" : "bg-cyan-200 text-slate-950 hover:bg-cyan-100"}`}>
          {status === "saving" ? "Saving…" : "Send beta feedback"}
        </button>
        {status === "error" ? <p className={`text-sm ${light ? "text-ps-warning" : "text-amber-300"}`}>Could not save that feedback. Please try again.</p> : null}
      </div>
    </form>
  );
}
