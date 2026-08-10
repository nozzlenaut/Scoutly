"use client";

import { useEffect, useState } from "react";
import {
  getAIConsoleBetaStatus,
  setAIConsoleBetaEnabled,
  type AIConsoleBetaStatus,
} from "@/lib/aiConsoleBeta";

type Props = {
  token?: string;
};

export function AdminAiConsoleBeta({ token }: Props) {
  const [status, setStatus] = useState<AIConsoleBetaStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getAIConsoleBetaStatus(token)
      .then((next) => {
        if (!cancelled) setStatus(next);
      })
      .catch(() => {
        if (!cancelled) setError("Could not load AI console beta status.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [token]);

  async function toggle() {
    if (!status || saving) return;
    if (!status.enabled && !status.api_key_configured) return;
    setSaving(true);
    setError(null);
    try {
      setStatus(await setAIConsoleBetaEnabled(!status.enabled, token));
    } catch {
      setError("Could not update the AI console beta setting.");
    } finally {
      setSaving(false);
    }
  }

  const stateLabel = loading
    ? "Loading"
    : status?.enabled && !status.api_key_configured
      ? "On, key missing"
      : !status?.api_key_configured
        ? "API key missing"
        : status.enabled
          ? "On"
          : "Off";

  const cannotEnable = Boolean(status && !status.enabled && !status.api_key_configured);

  return (
    <section className="mt-10 rounded-3xl border border-violet-300/20 bg-violet-300/[0.04] p-5">
      <div className="flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-3">
            <h2 className="text-2xl font-bold">AI console review beta</h2>
            <span
              className={`rounded-full px-3 py-1 text-xs font-bold uppercase tracking-[0.12em] ${
                status?.ready
                  ? "bg-emerald-300/15 text-emerald-200"
                  : status?.enabled
                    ? "bg-amber-300/15 text-amber-200"
                    : "bg-white/[0.08] text-slate-300"
              }`}
            >
              {stateLabel}
            </span>
          </div>

          <p className="mt-2 max-w-3xl text-sm text-slate-400">
            A second-pass AI listing check runs only for Nintendo Wii, Nintendo 64, and Nintendo Switch 2. PriceSift runs its normal filters first, gives AI a larger bounded shortlist, then ranks the surviving listings down to the final three.
          </p>

          {status ? (
            <p className="mt-2 text-xs text-slate-500">
              Model: {status.model}. Limits: {status.rate_limit_per_minute}/minute and {status.rate_limit_per_day}/day. The API key stays server-side and is never shown here.
            </p>
          ) : null}

          {!loading && status && !status.api_key_configured ? (
            <p className="mt-3 text-sm font-semibold text-amber-200">
              {status.enabled
                ? "OPENAI_API_KEY is missing, so AI calls are currently skipped. You can still switch the beta off here."
                : "Add OPENAI_API_KEY in Railway first. The switch cannot be turned on until the backend sees it."}
            </p>
          ) : null}

          {error ? <p className="mt-3 text-sm font-semibold text-rose-300">{error}</p> : null}
        </div>

        <button
          type="button"
          role="switch"
          aria-checked={Boolean(status?.enabled)}
          aria-label="Toggle AI console review beta"
          disabled={loading || saving || cannotEnable}
          onClick={toggle}
          className={`relative h-12 w-24 shrink-0 rounded-full border transition ${
            status?.enabled
              ? "border-emerald-200/40 bg-emerald-300/25"
              : "border-white/15 bg-white/[0.06]"
          } disabled:cursor-not-allowed disabled:opacity-50`}
        >
          <span
            className={`absolute top-1 h-9 w-9 rounded-full bg-white shadow transition ${
              status?.enabled ? "left-[50px]" : "left-1"
            }`}
          />
          <span className="sr-only">{status?.enabled ? "Disable" : "Enable"} AI console review beta</span>
        </button>
      </div>
    </section>
  );
}
