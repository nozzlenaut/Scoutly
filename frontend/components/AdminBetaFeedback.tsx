import type { BetaFeedbackRecord } from "@/lib/api";

function formatDate(value?: string | null): string {
  if (!value) return "—";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

export function AdminBetaFeedback({ feedback }: { feedback: BetaFeedbackRecord[] }) {
  return (
    <section className="mt-10 rounded-3xl border border-white/10 bg-white/[0.04] p-5">
      <div>
        <h2 className="text-2xl font-bold">Beta feedback</h2>
        <p className="mt-1 text-sm text-slate-500">General tester feedback submitted from the public beta form.</p>
      </div>
      <div className="mt-5 overflow-x-auto">
        <table className="w-full min-w-[950px] text-left text-sm">
          <thead className="text-slate-500"><tr><th className="py-2 pr-4">Submitted</th><th className="py-2 pr-4">Type</th><th className="py-2 pr-4">Category</th><th className="py-2 pr-4">Message</th><th className="py-2 pr-4">Email</th></tr></thead>
          <tbody className="divide-y divide-white/10 text-slate-300">
            {feedback.map((item) => (
              <tr key={item.id}>
                <td className="py-3 pr-4 text-slate-400">{formatDate(item.submitted_at)}</td>
                <td className="py-3 pr-4">{item.feedback_type}</td>
                <td className="py-3 pr-4">{item.category || "—"}</td>
                <td className="max-w-xl py-3 pr-4 whitespace-pre-wrap">{item.message}</td>
                <td className="py-3 pr-4">{item.email || "—"}</td>
              </tr>
            ))}
            {feedback.length === 0 ? <tr><td colSpan={5} className="py-4 text-slate-500">No beta feedback yet.</td></tr> : null}
          </tbody>
        </table>
      </div>
    </section>
  );
}
