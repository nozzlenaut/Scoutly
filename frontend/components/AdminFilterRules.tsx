"use client";

import { useState, type FormEvent } from "react";
import { createManualFilterRule, deleteManualFilterRule, type ManualFilterRule } from "@/lib/api";
import { allCategories } from "@/lib/categoryCatalog";

type Props = {
  initialRules: ManualFilterRule[];
  token?: string;
};

const CATEGORY_OPTIONS = [
  { value: "", label: "All categories" },
  ...allCategories.map((category) => ({ value: category.id, label: category.label })),
];

function splitExceptions(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean)
    .slice(0, 12);
}

function formatDate(value?: string | null): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

export function AdminFilterRules({ initialRules, token }: Props) {
  const [rules, setRules] = useState(initialRules);
  const [phrase, setPhrase] = useState("");
  const [category, setCategory] = useState("lego");
  const [productId, setProductId] = useState("");
  const [exceptPhrases, setExceptPhrases] = useState("");
  const [note, setNote] = useState("");
  const [status, setStatus] = useState<"idle" | "saving" | "saved" | "error">("idle");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("saving");
    try {
      const created = await createManualFilterRule(
        {
          phrase,
          category: category || null,
          product_id: productId.trim() || null,
          except_phrases: splitExceptions(exceptPhrases),
          note: note.trim() || null,
        },
        token,
      );
      setRules((current) => [created, ...current.filter((rule) => rule.id !== created.id)]);
      setPhrase("");
      setProductId("");
      setExceptPhrases("");
      setNote("");
      setStatus("saved");
    } catch {
      setStatus("error");
    }
  }

  async function removeRule(id: string) {
    setStatus("saving");
    try {
      await deleteManualFilterRule(id, token);
      setRules((current) => current.filter((rule) => rule.id !== id));
      setStatus("saved");
    } catch {
      setStatus("error");
    }
  }

  return (
    <section className="mt-10 rounded-3xl border border-cyan-300/20 bg-cyan-300/[0.04] p-5">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold">Live filter rules</h2>
          <p className="mt-1 max-w-3xl text-sm text-slate-400">
            Add rejection phrases here without redeploying. New rules apply to future searches. Scope them to a category or exact product ID when a phrase is risky.
          </p>
        </div>
        <div className="text-sm text-slate-400">{rules.length} active/manual rules</div>
      </div>

      <form onSubmit={submit} className="mt-5 grid gap-3 rounded-2xl border border-white/10 bg-slate-950/45 p-4 lg:grid-cols-5">
        <label className="lg:col-span-2">
          <span className="text-xs uppercase tracking-[0.16em] text-slate-500">Reject phrase</span>
          <input
            value={phrase}
            onChange={(event) => setPhrase(event.target.value)}
            required
            minLength={2}
            maxLength={120}
            placeholder="base & towers only"
            className="mt-2 w-full rounded-2xl border border-white/10 bg-white/[0.06] px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-300/60"
          />
        </label>

        <label>
          <span className="text-xs uppercase tracking-[0.16em] text-slate-500">Category</span>
          <select
            value={category}
            onChange={(event) => setCategory(event.target.value)}
            className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-900 px-4 py-3 text-sm text-white outline-none transition focus:border-cyan-300/60"
          >
            {CATEGORY_OPTIONS.map((option) => (
              <option key={option.value || "all"} value={option.value}>{option.label}</option>
            ))}
          </select>
        </label>

        <label>
          <span className="text-xs uppercase tracking-[0.16em] text-slate-500">Product ID</span>
          <input
            value={productId}
            onChange={(event) => setProductId(event.target.value)}
            placeholder="optional"
            className="mt-2 w-full rounded-2xl border border-white/10 bg-white/[0.06] px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-300/60"
          />
        </label>

        <label>
          <span className="text-xs uppercase tracking-[0.16em] text-slate-500">Unless phrase</span>
          <input
            value={exceptPhrases}
            onChange={(event) => setExceptPhrases(event.target.value)}
            placeholder="no problems, no issues"
            className="mt-2 w-full rounded-2xl border border-white/10 bg-white/[0.06] px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-300/60"
          />
        </label>

        <label className="lg:col-span-4">
          <span className="text-xs uppercase tracking-[0.16em] text-slate-500">Note</span>
          <input
            value={note}
            onChange={(event) => setNote(event.target.value)}
            placeholder="Why this rule exists"
            className="mt-2 w-full rounded-2xl border border-white/10 bg-white/[0.06] px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-300/60"
          />
        </label>

        <button
          type="submit"
          disabled={status === "saving"}
          className="rounded-2xl bg-white px-5 py-3 font-semibold text-slate-950 transition hover:bg-slate-200 disabled:cursor-wait disabled:opacity-60 lg:self-end"
        >
          Add rule
        </button>
      </form>

      {status === "error" ? <p className="mt-3 text-sm text-amber-300">Could not save that rule. Check the token or try again.</p> : null}
      {status === "saved" ? <p className="mt-3 text-sm text-emerald-300">Rule list updated.</p> : null}

      <div className="mt-5 overflow-x-auto">
        <table className="w-full min-w-[900px] text-left text-sm">
          <thead className="text-slate-500">
            <tr>
              <th className="py-2 pr-4">Phrase</th>
              <th className="py-2 pr-4">Scope</th>
              <th className="py-2 pr-4">Unless</th>
              <th className="py-2 pr-4">Note</th>
              <th className="py-2 pr-4">Created</th>
              <th className="py-2 pr-4">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10 text-slate-300">
            {rules.map((rule) => (
              <tr key={rule.id}>
                <td className="py-3 pr-4 font-semibold text-white">{rule.phrase}</td>
                <td className="py-3 pr-4">
                  {rule.product_id ? rule.product_id : rule.category || "global"}
                </td>
                <td className="py-3 pr-4">{rule.except_phrases?.length ? rule.except_phrases.join(", ") : "—"}</td>
                <td className="py-3 pr-4">{rule.note || "—"}</td>
                <td className="py-3 pr-4 text-slate-400">{formatDate(rule.created_at)}</td>
                <td className="py-3 pr-4">
                  <button
                    type="button"
                    onClick={() => removeRule(rule.id)}
                    disabled={status === "saving"}
                    className="rounded-xl border border-white/10 px-3 py-2 text-xs font-semibold text-slate-300 transition hover:bg-white/[0.08] disabled:cursor-wait disabled:opacity-60"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
            {rules.length === 0 ? (
              <tr><td className="py-4 text-slate-500" colSpan={6}>No manual filter rules yet.</td></tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </section>
  );
}
