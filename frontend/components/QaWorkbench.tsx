"use client";

import { useMemo, useState } from "react";
import {
  saveQaEvaluation,
  searchDeals,
  type QaCase,
  type QaEvaluation,
  type QaOutcome,
  type QaSummary,
  type SearchResponse,
} from "@/lib/api";

type Props = {
  initialCases: QaCase[];
  initialSummary: QaSummary;
  token: string;
};

type Filter = "all" | "consoles" | "lego" | "untested" | "review";

const outcomeLabels: Record<QaOutcome, { label: string; detail: string; className: string }> = {
  pass: {
    label: "Pass",
    detail: "Correct match and the first listing is valid.",
    className: "border-emerald-300/40 bg-emerald-300/15 text-emerald-100",
  },
  top3_only: {
    label: "Top-3 only",
    detail: "The first result is weak, but a valid result appears in the top three.",
    className: "border-amber-300/40 bg-amber-300/15 text-amber-100",
  },
  fail: {
    label: "Fail",
    detail: "Wrong resolution or no valid result in the top three.",
    className: "border-rose-300/40 bg-rose-300/15 text-rose-100",
  },
  no_inventory: {
    label: "No inventory",
    detail: "The product resolved correctly, but no safe live listing was available.",
    className: "border-slate-400/40 bg-slate-400/10 text-slate-200",
  },
};

const issueOptions = [
  ["wrong_product_resolution", "Wrong product resolution"],
  ["wrong_model", "Wrong model / version"],
  ["accessory_or_part", "Accessory or replacement part"],
  ["incomplete_or_broken", "Incomplete or broken"],
  ["wrong_set", "Wrong LEGO set"],
  ["missing_pieces", "Missing pieces / partial set"],
  ["instructions_or_box_only", "Instructions or box only"],
  ["compatible_brand", "Compatible brand / knockoff"],
  ["suspicious_variation", "Suspicious variation listing"],
  ["catalog_gap", "Catalog gap"],
  ["other", "Other"],
] as const;

function formatDate(value?: string | null): string {
  if (!value) return "Never";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

function money(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value);
}

function topRejectionReasons(reasons: Record<string, number> | undefined): [string, number][] {
  return Object.entries(reasons ?? {})
    .sort((left, right) => right[1] - left[1])
    .slice(0, 6);
}

function statusPill(evaluation?: QaEvaluation | null) {
  if (!evaluation) {
    return <span className="rounded-full border border-white/10 px-2.5 py-1 text-xs text-slate-500">Untested</span>;
  }
  const style = outcomeLabels[evaluation.outcome];
  return <span className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${style.className}`}>{style.label}</span>;
}

function buildSummary(cases: QaCase[]): QaSummary {
  const counts: QaSummary["counts"] = {
    pass: 0,
    top3_only: 0,
    fail: 0,
    no_inventory: 0,
    untested: 0,
  };
  const categoryCounts: QaSummary["category_counts"] = {};
  for (const testCase of cases) {
    if (!categoryCounts[testCase.category]) {
      categoryCounts[testCase.category] = {
        pass: 0,
        top3_only: 0,
        fail: 0,
        no_inventory: 0,
        untested: 0,
      };
    }
    const outcome = testCase.latest_evaluation?.outcome ?? "untested";
    counts[outcome] += 1;
    categoryCounts[testCase.category][outcome] += 1;
  }
  const tested = cases.length - counts.untested;
  const quality = counts.pass + counts.top3_only;
  return {
    total_cases: cases.length,
    tested_cases: tested,
    counts,
    category_counts: categoryCounts,
    quality_rate: tested ? Math.round((quality / tested) * 1000) / 10 : null,
  };
}

export function QaWorkbench({ initialCases, initialSummary, token }: Props) {
  const [cases, setCases] = useState(initialCases);
  const [summary, setSummary] = useState(initialSummary);
  const [filter, setFilter] = useState<Filter>("all");
  const [selectedId, setSelectedId] = useState(initialCases[0]?.id ?? "");
  const [searchData, setSearchData] = useState<SearchResponse | null>(null);
  const [running, setRunning] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [outcome, setOutcome] = useState<QaOutcome | null>(null);
  const [resolutionCorrect, setResolutionCorrect] = useState(false);
  const [issueTags, setIssueTags] = useState<string[]>([]);
  const [notes, setNotes] = useState("");

  const filteredCases = useMemo(() => {
    return cases.filter((testCase) => {
      if (filter === "all") return true;
      if (filter === "consoles" || filter === "lego") return testCase.category === filter;
      if (filter === "untested") return !testCase.latest_evaluation;
      return testCase.latest_evaluation?.outcome === "fail" || testCase.latest_evaluation?.outcome === "top3_only";
    });
  }, [cases, filter]);

  const selected = filteredCases.find((testCase) => testCase.id === selectedId) ?? filteredCases[0] ?? cases[0];

  function selectCase(testCase: QaCase) {
    setSelectedId(testCase.id);
    setSearchData(null);
    setOutcome(null);
    setResolutionCorrect(false);
    setIssueTags([]);
    setNotes("");
    setMessage(null);
  }

  async function runTest() {
    if (!selected) return;
    setRunning(true);
    setMessage(null);
    setSearchData(null);
    setOutcome(null);
    setIssueTags([]);
    setNotes("");
    try {
      const data = await searchDeals(selected.query, selected.category, "ebay", {
        includeAuctions: false,
      });
      const correct = data.resolved_product?.product.id === selected.expected_product_id;
      setSearchData(data);
      setResolutionCorrect(correct);
      if (!correct) {
        setOutcome("fail");
        setIssueTags(["wrong_product_resolution"]);
      } else if (data.results.length === 0) {
        setOutcome("no_inventory");
      }
    } catch {
      setMessage("The live search failed. Check the backend connection and try again.");
    } finally {
      setRunning(false);
    }
  }

  function toggleIssue(tag: string) {
    setIssueTags((current) =>
      current.includes(tag) ? current.filter((item) => item !== tag) : [...current, tag],
    );
  }

  async function saveEvaluation() {
    if (!selected || !searchData || !outcome) return;
    setSaving(true);
    setMessage(null);
    try {
      const evaluation = await saveQaEvaluation(
        {
          case_id: selected.id,
          category: selected.category,
          query: selected.query,
          expected_product_id: selected.expected_product_id,
          expected_label: selected.expected_label,
          resolved_product_id: searchData.resolved_product?.product.id,
          resolved_label: searchData.resolved_product?.product.display_name,
          resolution_correct: resolutionCorrect,
          outcome,
          issue_tags: issueTags,
          notes,
          result_titles: searchData.results.slice(0, 3).map((result) => result.title),
          diagnostics: searchData.diagnostics,
        },
        token,
      );
      const updated = cases.map((testCase) =>
        testCase.id === selected.id
          ? {
              ...testCase,
              latest_evaluation: evaluation,
              attempt_count: testCase.attempt_count + 1,
            }
          : testCase,
      );
      setCases(updated);
      setSummary(buildSummary(updated));
      setMessage("Evaluation saved.");
    } catch {
      setMessage("Could not save this evaluation.");
    } finally {
      setSaving(false);
    }
  }

  if (!selected) {
    return <p className="mt-8 text-slate-400">No QA cases are configured.</p>;
  }

  const resolved = searchData?.resolved_product?.product;

  return (
    <>
      <section className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <div className="rounded-3xl border border-white/10 bg-white/[0.05] p-5">
          <p className="text-sm text-slate-400">Tested</p>
          <p className="mt-2 text-3xl font-black">{summary.tested_cases}/{summary.total_cases}</p>
        </div>
        <div className="rounded-3xl border border-emerald-300/15 bg-emerald-300/[0.06] p-5">
          <p className="text-sm text-emerald-100/70">Pass</p>
          <p className="mt-2 text-3xl font-black text-emerald-200">{summary.counts.pass}</p>
        </div>
        <div className="rounded-3xl border border-amber-300/15 bg-amber-300/[0.06] p-5">
          <p className="text-sm text-amber-100/70">Top-3 only</p>
          <p className="mt-2 text-3xl font-black text-amber-200">{summary.counts.top3_only}</p>
        </div>
        <div className="rounded-3xl border border-rose-300/15 bg-rose-300/[0.06] p-5">
          <p className="text-sm text-rose-100/70">Failures</p>
          <p className="mt-2 text-3xl font-black text-rose-200">{summary.counts.fail}</p>
        </div>
        <div className="rounded-3xl border border-white/10 bg-white/[0.05] p-5">
          <p className="text-sm text-slate-400">Usable top-three rate</p>
          <p className="mt-2 text-3xl font-black">{summary.quality_rate === null ? "—" : `${summary.quality_rate}%`}</p>
        </div>
      </section>

      <div className="mt-8 flex flex-wrap gap-2">
        {([
          ["all", "All"],
          ["consoles", "Consoles"],
          ["lego", "LEGO"],
          ["untested", "Untested"],
          ["review", "Needs review"],
        ] as const).map(([value, label]) => (
          <button
            key={value}
            type="button"
            onClick={() => setFilter(value)}
            className={`rounded-full border px-4 py-2 text-sm font-semibold transition ${
              filter === value
                ? "border-cyan-300/50 bg-cyan-300/15 text-cyan-100"
                : "border-white/10 bg-white/[0.04] text-slate-400 hover:bg-white/[0.08]"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      <section className="mt-5 grid gap-5 xl:grid-cols-[360px_minmax(0,1fr)]">
        <div className="max-h-[850px] overflow-y-auto rounded-3xl border border-white/10 bg-white/[0.035] p-3">
          <div className="space-y-2">
            {filteredCases.map((testCase) => (
              <button
                key={testCase.id}
                type="button"
                onClick={() => selectCase(testCase)}
                className={`w-full rounded-2xl border p-4 text-left transition ${
                  selected.id === testCase.id
                    ? "border-cyan-300/40 bg-cyan-300/10"
                    : "border-white/5 bg-white/[0.025] hover:border-white/15 hover:bg-white/[0.06]"
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                      {testCase.category} · {testCase.priority}
                    </p>
                    <p className="mt-2 font-bold text-white">{testCase.query}</p>
                  </div>
                  {statusPill(testCase.latest_evaluation)}
                </div>
                <p className="mt-2 line-clamp-2 text-xs leading-5 text-slate-500">{testCase.expected_label}</p>
              </button>
            ))}
            {filteredCases.length === 0 ? (
              <p className="p-5 text-sm text-slate-500">Nothing matches this filter. A rare and beautiful empty inbox.</p>
            ) : null}
          </div>
        </div>

        <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-5 sm:p-6">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan-200/70">
                {selected.category} · {selected.priority} priority
              </p>
              <h2 className="mt-2 text-3xl font-black">{selected.query}</h2>
              <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-400">{selected.goal}</p>
              <div className="mt-4 rounded-2xl border border-white/10 bg-slate-950/40 p-4">
                <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Expected catalog item</p>
                <p className="mt-2 font-semibold text-slate-100">{selected.expected_label}</p>
                <p className="mt-1 break-all text-xs text-slate-600">{selected.expected_product_id}</p>
              </div>
            </div>
            <button
              type="button"
              onClick={runTest}
              disabled={running}
              className="shrink-0 rounded-2xl bg-white px-5 py-3 font-bold text-slate-950 transition hover:bg-slate-200 disabled:cursor-wait disabled:opacity-60"
            >
              {running ? "Running search…" : searchData ? "Run again" : "Run live test"}
            </button>
          </div>

          {selected.latest_evaluation ? (
            <div className="mt-5 flex flex-col gap-2 rounded-2xl border border-white/10 bg-white/[0.03] p-4 text-sm sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-3">
                {statusPill(selected.latest_evaluation)}
                <span className="text-slate-400">Last tested {formatDate(selected.latest_evaluation.created_at)}</span>
              </div>
              <span className="text-slate-500">{selected.attempt_count} saved attempt{selected.attempt_count === 1 ? "" : "s"}</span>
            </div>
          ) : null}

          {message ? (
            <p className={`mt-5 rounded-2xl border p-4 text-sm ${message === "Evaluation saved." ? "border-emerald-300/20 bg-emerald-300/10 text-emerald-100" : "border-amber-300/20 bg-amber-300/10 text-amber-100"}`}>
              {message}
            </p>
          ) : null}

          {searchData ? (
            <div className="mt-6">
              <div className={`rounded-2xl border p-4 ${resolutionCorrect ? "border-emerald-300/25 bg-emerald-300/[0.08]" : "border-rose-300/25 bg-rose-300/[0.08]"}`}>
                <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Scoutly resolved</p>
                    <p className="mt-2 font-bold">{resolved?.display_name ?? "No catalog product"}</p>
                    <p className="mt-1 break-all text-xs text-slate-500">{resolved?.id ?? "—"}</p>
                    {searchData.resolved_product ? (
                      <p className="mt-1 text-xs text-slate-500">Confidence {Math.round(searchData.resolved_product.confidence * 100)}%</p>
                    ) : null}
                  </div>
                  <label className="flex cursor-pointer items-center gap-3 rounded-xl border border-white/10 bg-slate-950/30 px-4 py-3 text-sm font-semibold">
                    <input
                      type="checkbox"
                      checked={resolutionCorrect}
                      onChange={(event) => setResolutionCorrect(event.target.checked)}
                      className="h-4 w-4 accent-emerald-400"
                    />
                    Resolution is correct
                  </label>
                </div>
              </div>

              <div className="mt-6">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                  <div>
                    <h3 className="text-xl font-bold">Top live results</h3>
                    <p className="mt-1 text-sm text-slate-500">
                      {searchData.diagnostics.fixed_price_candidates} candidates · {searchData.diagnostics.fixed_price_eligible} eligible · {searchData.diagnostics.fixed_price_filtered} filtered
                    </p>
                  </div>
                  <p className="text-xs text-slate-600">Links open directly so QA clicks do not pollute normal click analytics.</p>
                </div>
                {searchData.results.length ? (
                  <div className="mt-4 grid gap-4 lg:grid-cols-3">
                    {searchData.results.slice(0, 3).map((result, index) => (
                      <article key={`${result.url}-${index}`} className="rounded-2xl border border-white/10 bg-slate-950/35 p-4">
                        <div className="flex items-center justify-between gap-3">
                          <span className="rounded-full border border-white/10 px-2.5 py-1 text-xs text-slate-400">#{index + 1}</span>
                          <span className="text-sm font-black text-cyan-100">{money(result.total_price)}</span>
                        </div>
                        <h4 className="mt-3 line-clamp-4 min-h-20 text-sm font-semibold leading-5 text-slate-100">{result.title}</h4>
                        <p className="mt-3 text-xs text-slate-500">{result.condition} · score {Math.round(result.score)}</p>
                        {result.warning_labels.length ? (
                          <p className="mt-2 text-xs text-amber-200">{result.warning_labels.join(", ")}</p>
                        ) : null}
                        <a
                          href={result.url}
                          target="_blank"
                          rel="noreferrer"
                          className="mt-4 inline-flex rounded-xl border border-white/10 px-3 py-2 text-xs font-semibold text-cyan-200 transition hover:bg-white/[0.08]"
                        >
                          Inspect listing ↗
                        </a>
                      </article>
                    ))}
                  </div>
                ) : (
                  <div className="mt-4 rounded-2xl border border-slate-400/20 bg-slate-400/[0.06] p-5 text-sm text-slate-300">
                    No safe Buy It Now listings were returned.
                  </div>
                )}
                {topRejectionReasons(searchData.diagnostics.fixed_price_rejection_reasons).length ? (
                  <div className="mt-4 rounded-2xl border border-white/10 bg-slate-950/30 p-4">
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Top filter reasons</p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {topRejectionReasons(searchData.diagnostics.fixed_price_rejection_reasons).map(([reason, count]) => (
                        <span key={reason} className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5 text-xs text-slate-300">
                          {count}× {reason}
                        </span>
                      ))}
                    </div>
                  </div>
                ) : null}
              </div>

              <div className="mt-7 border-t border-white/10 pt-6">
                <h3 className="text-xl font-bold">Record the outcome</h3>
                <p className="mt-1 text-sm text-slate-500">Judge the listings, not merely whether eBay returned something shiny.</p>
                <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                  {(Object.keys(outcomeLabels) as QaOutcome[]).map((value) => {
                    const option = outcomeLabels[value];
                    return (
                      <button
                        key={value}
                        type="button"
                        onClick={() => setOutcome(value)}
                        className={`rounded-2xl border p-4 text-left transition ${
                          outcome === value ? option.className : "border-white/10 bg-white/[0.025] text-slate-300 hover:bg-white/[0.06]"
                        }`}
                      >
                        <span className="font-bold">{option.label}</span>
                        <span className="mt-1 block text-xs leading-5 opacity-75">{option.detail}</span>
                      </button>
                    );
                  })}
                </div>

                <div className="mt-6">
                  <p className="text-sm font-semibold text-slate-300">Issue tags</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {issueOptions.map(([value, label]) => (
                      <button
                        key={value}
                        type="button"
                        onClick={() => toggleIssue(value)}
                        className={`rounded-full border px-3 py-2 text-xs font-semibold transition ${
                          issueTags.includes(value)
                            ? "border-rose-300/35 bg-rose-300/15 text-rose-100"
                            : "border-white/10 bg-white/[0.025] text-slate-500 hover:text-slate-300"
                        }`}
                      >
                        {label}
                      </button>
                    ))}
                  </div>
                </div>

                <label className="mt-6 block">
                  <span className="text-sm font-semibold text-slate-300">Notes</span>
                  <textarea
                    value={notes}
                    onChange={(event) => setNotes(event.target.value)}
                    maxLength={1200}
                    rows={4}
                    placeholder="Example: Result #1 was tablet-only; result #2 was a complete console and should rank first."
                    className="mt-3 w-full rounded-2xl border border-white/10 bg-slate-950/45 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-700 focus:border-cyan-300/40"
                  />
                </label>

                <button
                  type="button"
                  onClick={saveEvaluation}
                  disabled={!outcome || saving}
                  className="mt-5 rounded-2xl bg-cyan-200 px-5 py-3 font-bold text-slate-950 transition hover:bg-cyan-100 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  {saving ? "Saving…" : "Save evaluation"}
                </button>
              </div>
            </div>
          ) : (
            <div className="mt-6 rounded-2xl border border-dashed border-white/10 p-8 text-center text-sm text-slate-500">
              Run the case to compare the expected catalog item with live Scoutly results.
            </div>
          )}
        </div>
      </section>
    </>
  );
}
