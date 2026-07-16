"use client";

import { useMemo, useState } from "react";
import {
  getKehLensBuilder,
  saveQaEvaluation,
  type KehLensBuilderResponse,
  type KehLensModel,
  type QaCase,
  type QaEvaluation,
  type QaOutcome,
} from "@/lib/api";

export type LensQaCase = QaCase & {
  runner: "keh_lens";
  lens_filters: {
    mount: string;
    lens_type: "Prime" | "Zoom";
    focal_group: string;
    brand?: string;
  };
};

const outcomeStyles: Record<QaOutcome, string> = {
  pass: "border-emerald-300/40 bg-emerald-300/15 text-emerald-100",
  top3_only: "border-amber-300/40 bg-amber-300/15 text-amber-100",
  fail: "border-rose-300/40 bg-rose-300/15 text-rose-100",
  no_inventory: "border-slate-400/40 bg-slate-400/10 text-slate-200",
};

const issues = [
  ["wrong_mount", "Wrong mount"],
  ["wrong_lens_type", "Wrong prime / zoom type"],
  ["wrong_focal_group", "Wrong focal group"],
  ["wrong_brand", "Wrong brand"],
  ["accessory_or_part", "Accessory or lens part"],
  ["duplicate_model", "Duplicate model grouping"],
  ["poor_grouping", "Model grouping looks wrong"],
  ["other", "Other"],
] as const;

function money(value?: number | null, currency = "USD") {
  if (value === null || value === undefined) return "—";
  try {
    return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(value);
  } catch {
    return `$${value.toFixed(2)}`;
  }
}

function matches(model: KehLensModel, testCase: LensQaCase) {
  const filters = testCase.lens_filters;
  return (
    model.mount === filters.mount &&
    model.lens_type === filters.lens_type &&
    model.focal_group === filters.focal_group &&
    (!filters.brand || model.brand === filters.brand)
  );
}

function responseIsCorrect(data: KehLensBuilderResponse, testCase: LensQaCase) {
  const filters = testCase.lens_filters;
  return (
    data.selected.mount === filters.mount &&
    data.selected.lens_type === filters.lens_type &&
    data.selected.focal_group === filters.focal_group &&
    (!filters.brand || data.selected.brand === filters.brand) &&
    data.models.every((model) => matches(model, testCase))
  );
}

function Status({ evaluation }: { evaluation?: QaEvaluation | null }) {
  if (!evaluation) {
    return <span className="rounded-full border border-white/10 px-2 py-1 text-xs text-slate-500">Untested</span>;
  }
  const labels: Record<QaOutcome, string> = {
    pass: "Pass",
    top3_only: "Top-3",
    fail: "Fail",
    no_inventory: "No inventory",
  };
  return (
    <span className={`rounded-full border px-2 py-1 text-xs font-semibold ${outcomeStyles[evaluation.outcome]}`}>
      {labels[evaluation.outcome]}
    </span>
  );
}

export function LensQaWorkbench({ initialCases, token }: { initialCases: LensQaCase[]; token: string }) {
  const [cases, setCases] = useState(initialCases);
  const [selectedId, setSelectedId] = useState(initialCases[0]?.id ?? "");
  const [filter, setFilter] = useState("all");
  const [data, setData] = useState<KehLensBuilderResponse | null>(null);
  const [outcome, setOutcome] = useState<QaOutcome | null>(null);
  const [resolutionCorrect, setResolutionCorrect] = useState(false);
  const [issueTags, setIssueTags] = useState<string[]>([]);
  const [notes, setNotes] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const mounts = useMemo(
    () => Array.from(new Set(cases.map((testCase) => testCase.lens_filters.mount))).sort(),
    [cases],
  );
  const filtered = cases.filter((testCase) => {
    if (filter === "all") return true;
    if (filter === "untested") return !testCase.latest_evaluation;
    if (filter === "review") {
      return ["fail", "top3_only"].includes(testCase.latest_evaluation?.outcome ?? "");
    }
    return testCase.lens_filters.mount === filter;
  });
  const selected = filtered.find((testCase) => testCase.id === selectedId) ?? filtered[0] ?? cases[0];

  const counts = useMemo(() => {
    const result = { pass: 0, top3_only: 0, fail: 0, no_inventory: 0, untested: 0 };
    for (const testCase of cases) result[testCase.latest_evaluation?.outcome ?? "untested"] += 1;
    return result;
  }, [cases]);

  function choose(testCase: LensQaCase) {
    setSelectedId(testCase.id);
    setData(null);
    setOutcome(null);
    setResolutionCorrect(false);
    setIssueTags([]);
    setNotes("");
    setMessage(null);
  }

  async function run() {
    if (!selected) return;
    setBusy(true);
    setData(null);
    setOutcome(null);
    setIssueTags([]);
    setMessage(null);
    try {
      const filters = selected.lens_filters;
      const next = await getKehLensBuilder(token, {
        mount: filters.mount,
        lensType: filters.lens_type,
        focalGroup: filters.focal_group,
        brand: filters.brand,
        limit: 250,
      });
      const correct = responseIsCorrect(next, selected);
      setData(next);
      setResolutionCorrect(correct);
      if (!correct) {
        setOutcome("fail");
        setIssueTags(["poor_grouping"]);
      } else if (!next.summary.filtered_model_count || !next.summary.filtered_listing_count) {
        setOutcome("no_inventory");
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Lens Lab search failed.");
    } finally {
      setBusy(false);
    }
  }

  async function save() {
    if (!selected || !data || !outcome) return;
    setBusy(true);
    setMessage(null);
    try {
      const evaluation = await saveQaEvaluation(
        {
          case_id: selected.id,
          category: "lenses",
          query: selected.query,
          expected_product_id: selected.expected_product_id,
          expected_label: selected.expected_label,
          resolved_product_id: resolutionCorrect ? selected.expected_product_id : null,
          resolved_label: `${data.summary.filtered_model_count} models · ${data.summary.filtered_listing_count} listings`,
          resolution_correct: resolutionCorrect,
          outcome,
          issue_tags: issueTags,
          notes,
          result_titles: data.models.slice(0, 3).map((model) => model.model_name),
          diagnostics: {
            runner: "keh_lens",
            requested_filters: selected.lens_filters,
            selected_filters: data.selected,
            summary: data.summary,
            mismatched_models: data.models
              .filter((model) => !matches(model, selected))
              .slice(0, 10)
              .map((model) => model.model_name),
          },
        },
        token,
      );
      setCases((current) =>
        current.map((testCase) =>
          testCase.id === selected.id
            ? { ...testCase, latest_evaluation: evaluation, attempt_count: testCase.attempt_count + 1 }
            : testCase,
        ),
      );
      setMessage("Lens evaluation saved.");
    } catch {
      setMessage("Could not save this lens evaluation.");
    } finally {
      setBusy(false);
    }
  }

  if (!selected) return null;
  const filters = selected.lens_filters;

  return (
    <section className="mt-14 border-t border-white/10 pt-12">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.25em] text-emerald-300/70">KEH Lens Lab QA</p>
          <h2 className="mt-2 text-3xl font-black">Lens filter regression suite</h2>
          <p className="mt-3 max-w-4xl text-slate-400">
            Test live KEH lens inventory by mount, prime/zoom type, and focal group. These runs stay out of public analytics.
          </p>
        </div>
        <a href={`/admin/keh/lenses?token=${encodeURIComponent(token)}`} className="text-sm font-semibold text-emerald-200">
          Open full Lens Lab →
        </a>
      </div>

      <div className="mt-7 grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
        {[
          ["Tested", cases.length - counts.untested],
          ["Pass", counts.pass],
          ["Top-3", counts.top3_only],
          ["Failures", counts.fail],
          ["No inventory", counts.no_inventory],
        ].map(([label, value]) => (
          <div key={label} className="rounded-3xl border border-white/10 bg-white/[0.05] p-5">
            <p className="text-sm text-slate-400">{label}</p>
            <p className="mt-2 text-3xl font-black">{value}</p>
          </div>
        ))}
      </div>

      <div className="mt-7 flex flex-wrap gap-2">
        {[["all", "All"], ...mounts.map((mount) => [mount, mount]), ["untested", "Untested"], ["review", "Needs review"]].map(
          ([value, label]) => (
            <button
              key={value}
              type="button"
              onClick={() => setFilter(value)}
              className={`rounded-full border px-4 py-2 text-sm font-semibold ${
                filter === value
                  ? "border-emerald-300/50 bg-emerald-300/15 text-emerald-100"
                  : "border-white/10 text-slate-400"
              }`}
            >
              {label}
            </button>
          ),
        )}
      </div>

      <div className="mt-5 grid gap-5 xl:grid-cols-[360px_minmax(0,1fr)]">
        <div className="max-h-[900px] overflow-y-auto rounded-3xl border border-white/10 bg-white/[0.035] p-3">
          <div className="space-y-2">
            {filtered.map((testCase) => (
              <button
                key={testCase.id}
                type="button"
                onClick={() => choose(testCase)}
                className={`w-full rounded-2xl border p-4 text-left ${
                  selected.id === testCase.id ? "border-emerald-300/40 bg-emerald-300/10" : "border-white/5 bg-black/10"
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-semibold text-white">{testCase.expected_label}</p>
                    <p className="mt-1 text-xs text-slate-500">{testCase.lens_filters.mount} · {testCase.lens_filters.lens_type}</p>
                  </div>
                  <Status evaluation={testCase.latest_evaluation} />
                </div>
              </button>
            ))}
          </div>
        </div>

        <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-5 sm:p-6">
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-emerald-300/70">{filters.mount} · {filters.lens_type}</p>
          <h3 className="mt-2 text-2xl font-black">{selected.expected_label}</h3>
          <p className="mt-2 text-sm text-slate-400">{selected.goal}</p>
          <div className="mt-4 flex flex-wrap gap-2 text-xs">
            {[filters.mount, filters.lens_type, filters.focal_group, filters.brand].filter(Boolean).map((value) => (
              <span key={value} className="rounded-full bg-white/10 px-3 py-1 text-slate-200">{value}</span>
            ))}
          </div>

          <button
            type="button"
            onClick={run}
            disabled={busy}
            className="mt-6 rounded-2xl bg-emerald-300 px-5 py-3 font-bold text-slate-950 disabled:opacity-50"
          >
            {busy ? "Working…" : "Run this lens case"}
          </button>
          {message ? <p className="mt-4 rounded-2xl border border-white/10 bg-black/20 p-3 text-sm">{message}</p> : null}

          {data ? (
            <>
              <div className="mt-6 grid gap-3 sm:grid-cols-3">
                <div className="rounded-2xl bg-black/20 p-4"><p className="text-xs text-slate-500">Models</p><p className="text-2xl font-black">{data.summary.filtered_model_count}</p></div>
                <div className="rounded-2xl bg-black/20 p-4"><p className="text-xs text-slate-500">Listings</p><p className="text-2xl font-black">{data.summary.filtered_listing_count}</p></div>
                <div className="rounded-2xl bg-black/20 p-4"><p className="text-xs text-slate-500">Filter integrity</p><p className={resolutionCorrect ? "font-black text-emerald-200" : "font-black text-rose-200"}>{resolutionCorrect ? "Matched" : "Mismatch"}</p></div>
              </div>

              <div className="mt-6 space-y-3">
                {data.models.slice(0, 16).map((model, index) => (
                  <details key={model.model_key} className={`rounded-2xl border p-4 ${matches(model, selected) ? "border-white/10" : "border-rose-300/40 bg-rose-300/10"}`}>
                    <summary className="cursor-pointer list-none">
                      <div className="flex flex-wrap justify-between gap-3">
                        <div>
                          <p className="text-xs text-slate-500">Model {index + 1}</p>
                          <p className="font-semibold">{model.model_name}</p>
                          <p className="text-xs text-slate-400">{model.brand} · {model.mount} · {model.lens_type} · {model.focal_group}</p>
                        </div>
                        <p className="text-sm text-emerald-200">{model.listing_count} available · from {money(model.lowest_price, model.currency)}</p>
                      </div>
                    </summary>
                    <div className="mt-3 space-y-2 border-t border-white/10 pt-3">
                      {model.listings.slice(0, 3).map((listing) => (
                        <p key={listing.aw_product_id} className="rounded-xl bg-black/20 p-3 text-sm">
                          {listing.title} · {money(listing.price, listing.currency)}
                        </p>
                      ))}
                    </div>
                  </details>
                ))}
                {!data.models.length ? <p className="rounded-2xl border border-dashed border-white/15 p-5 text-sm text-slate-400">No current KEH inventory matched this combination.</p> : null}
              </div>

              <div className="mt-7 border-t border-white/10 pt-6">
                <div className="flex flex-wrap gap-2">
                  {([["pass", "Pass"], ["top3_only", "Top-3 only"], ["fail", "Fail"], ["no_inventory", "No inventory"]] as Array<[QaOutcome, string]>).map(
                    ([value, label]) => (
                      <button key={value} type="button" onClick={() => setOutcome(value)} className={`rounded-full border px-4 py-2 text-sm ${outcome === value ? outcomeStyles[value] : "border-white/10 text-slate-400"}`}>
                        {label}
                      </button>
                    ),
                  )}
                </div>
                <label className="mt-5 flex gap-3 text-sm">
                  <input type="checkbox" checked={resolutionCorrect} onChange={(event) => setResolutionCorrect(event.target.checked)} />
                  Returned filters and model rows match this case
                </label>
                <div className="mt-5 flex flex-wrap gap-2">
                  {issues.map(([value, label]) => (
                    <button key={value} type="button" onClick={() => setIssueTags((current) => current.includes(value) ? current.filter((tag) => tag !== value) : [...current, value])} className={`rounded-full border px-3 py-1.5 text-xs ${issueTags.includes(value) ? "border-rose-300/40 bg-rose-300/15 text-rose-100" : "border-white/10 text-slate-500"}`}>
                      {label}
                    </button>
                  ))}
                </div>
                <textarea value={notes} onChange={(event) => setNotes(event.target.value)} rows={3} maxLength={1200} placeholder="Notes about anything odd or ambiguous…" className="mt-5 w-full rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm" />
                <button type="button" onClick={save} disabled={busy || !outcome} className="mt-4 rounded-2xl bg-white px-5 py-3 font-bold text-slate-950 disabled:opacity-40">
                  Save lens evaluation
                </button>
              </div>
            </>
          ) : null}
        </div>
      </div>
    </section>
  );
}
