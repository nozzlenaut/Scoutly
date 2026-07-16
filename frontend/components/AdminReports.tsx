"use client";

import { useState } from "react";
import { deleteBadResultReport, type BadResultReport } from "@/lib/api";
import { formatAdminDate } from "@/lib/formatAdminDate";
import { AdminCollapsibleSection } from "@/components/AdminCollapsibleSection";

type Props = {
  initialReports: BadResultReport[];
  token?: string;
};

export function AdminReports({ initialReports, token }: Props) {
  const [reports, setReports] = useState(initialReports);
  const [status, setStatus] = useState<"idle" | "saving" | "saved" | "error">("idle");

  async function restore(report: BadResultReport) {
    if (!report.link_key) return;
    setStatus("saving");
    try {
      await deleteBadResultReport(report.link_key, token, {
        productId: report.product_id,
        category: report.category,
      });
      setReports((current) => current.filter((item) => item.link_key !== report.link_key));
      setStatus("saved");
    } catch {
      setStatus("error");
    }
  }

  return (
    <AdminCollapsibleSection
      count={reports.length}
      description="Reported items are hidden for 72 hours. Restore one here if it was flagged by mistake."
      title="Active bad-result reports"
    >
      <div>
        {status === "saved" ? <p className="text-sm text-emerald-300">Report restored.</p> : null}
        {status === "error" ? <p className="text-sm text-amber-300">Could not restore report.</p> : null}
      </div>
      <div className="mt-3 overflow-x-auto">
        <table className="w-full min-w-[1000px] text-left text-sm">
          <thead className="text-slate-500">
            <tr>
              <th className="py-2 pr-4">Reported (ET)</th>
              <th className="py-2 pr-4">Expires (ET)</th>
              <th className="py-2 pr-4">Reason</th>
              <th className="py-2 pr-4">Category</th>
              <th className="py-2 pr-4">Title</th>
              <th className="py-2 pr-4">Item ID</th>
              <th className="py-2 pr-4">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10 text-slate-300">
            {reports.map((report, index) => (
              <tr key={`${report.reported_at}-${report.link_key}-${index}`}>
                <td className="whitespace-nowrap py-3 pr-4 text-slate-400">{formatAdminDate(report.reported_at)}</td>
                <td className="whitespace-nowrap py-3 pr-4 text-slate-400">{formatAdminDate(report.expires_at)}</td>
                <td className="py-3 pr-4">{report.reason || "â€”"}</td>
                <td className="py-3 pr-4">{report.category || "â€”"}</td>
                <td className="py-3 pr-4">{report.title || "â€”"}</td>
                <td className="py-3 pr-4">{report.ebay_item_id || "â€”"}</td>
                <td className="py-3 pr-4">
                  <button
                    type="button"
                    onClick={() => restore(report)}
                    disabled={status === "saving" || !report.link_key}
                    className="rounded-xl border border-white/10 px-3 py-2 text-xs font-semibold text-slate-300 transition hover:bg-white/[0.08] disabled:cursor-wait disabled:opacity-60"
                  >
                    Restore
                  </button>
                </td>
              </tr>
            ))}
            {reports.length === 0 ? (
              <tr><td className="py-4 text-slate-500" colSpan={7}>No active reports.</td></tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </AdminCollapsibleSection>
  );
}
