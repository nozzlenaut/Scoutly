import type { SearchResult } from "@/lib/api";

export function ResultCard({ result }: { result: SearchResult }) {
  return (
    <article className="rounded-3xl border border-white/10 bg-white/[0.06] p-5 shadow-2xl shadow-black/20">
      <div className="mb-4 flex items-center justify-between gap-4">
        <span className="rounded-full bg-white/10 px-3 py-1 text-sm font-medium text-cyan-200">
          {result.provider}
        </span>
        <span className="text-sm text-slate-400">Score {Math.round(result.score)}</span>
      </div>
      <h2 className="text-xl font-semibold text-white">{result.title}</h2>
      <div className="mt-4 grid gap-2 text-sm text-slate-300">
        <div className="flex justify-between"><span>Item price</span><span>${result.price.toFixed(2)}</span></div>
        <div className="flex justify-between"><span>Shipping</span><span>${result.shipping.toFixed(2)}</span></div>
        <div className="flex justify-between border-t border-white/10 pt-2 text-lg font-bold text-white"><span>Total</span><span>${result.total_price.toFixed(2)}</span></div>
        <div className="flex justify-between"><span>Condition</span><span>{result.condition}</span></div>
        <div className="flex justify-between"><span>Seller</span><span>{result.seller_rating ? `${result.seller_rating}%` : "Unknown"}</span></div>
      </div>
      <a
        href={result.url}
        target="_blank"
        rel="noreferrer"
        className="mt-5 block rounded-2xl bg-white px-5 py-3 text-center font-semibold text-slate-950 transition hover:bg-slate-200"
      >
        View deal
      </a>
    </article>
  );
}
