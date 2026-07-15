import type { BetaFeedbackRecord } from "@/lib/api";
import { formatAdminDate } from "@/lib/formatAdminDate";

export function AdminBetaFeedback({ feedback }: { feedback: BetaFeedbackRecord[] }) {
  return (
    <section id="feedback" className="mt-10 scroll-mt-6 rounded-3xl border border-white/10 bg-white/[0.04] p-5">
      <div>
        <h2 className="text-2xl font-bold">Feedback inbox</h2>
        <p className="mt-1 text-sm text-slate-500">
          Public beta submissions are stored in PostgreSQL when connected, with local JSON used only as a development fallback.
        </p>
      </div>
      <div className="mt-5 overflow-x-auto">
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
    </section>
  );
}
