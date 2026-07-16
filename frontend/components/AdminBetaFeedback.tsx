import type { BetaFeedbackRecord } from "@/lib/api";
import { formatAdminDate } from "@/lib/formatAdminDate";
import { AdminCollapsibleSection } from "@/components/AdminCollapsibleSection";

export function AdminBetaFeedback({ feedback }: { feedback: BetaFeedbackRecord[] }) {
  return (
    <AdminCollapsibleSection
      count={feedback.length}
      description="Public beta submissions stored in PostgreSQL when connected, with local JSON used only as a development fallback."
      id="feedback"
      title="Feedback inbox"
    >
      <div className="overflow-x-auto">
        <table className="w-full min-w-[1100px] text-left text-sm">
          <thead className="text-slate-500">
            <tr>
              <th className="py-2 pr-4">Submitted (ET)</th>
              <th className="py-2 pr-4">Type</th>
              <th className="py-2 pr-4">Category</th>
              <th className="py-2 pr-4">Message</th>
              <th className="py-2 pr-4">Email</th>
              <th className="py-2 pr-4">Page</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10 text-slate-300">
            {feedback.map((item) => (
              <tr key={item.id}>
                <td className="whitespace-nowrap py-3 pr-4 text-slate-400">{formatAdminDate(item.submitted_at)}</td>
                <td className="py-3 pr-4">{item.feedback_type}</td>
                <td className="py-3 pr-4">{item.category || "â€”"}</td>
                <td className="max-w-xl whitespace-pre-wrap py-3 pr-4">{item.message}</td>
                <td className="break-all py-3 pr-4">{item.email || "â€”"}</td>
                <td className="py-3 pr-4">
                  {item.page_url ? (
                    <a href={item.page_url} target="_blank" rel="noreferrer" className="text-cyan-200 hover:text-cyan-100">
                      Open page
                    </a>
                  ) : "â€”"}
                </td>
              </tr>
            ))}
            {feedback.length === 0 ? (
              <tr><td colSpan={6} className="py-4 text-slate-500">No feedback submitted yet.</td></tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </AdminCollapsibleSection>
  );
}
