import type { SearchResult } from "@/lib/api";
import { buildOutboundUrl } from "@/lib/api";
import { ReportBadResultButton } from "@/components/ReportBadResultButton";

type Props = {
  result: SearchResult;
  query: string;
  category: string;
  productId?: string;
};

export function ResultCard({ result, query, category, productId }: Props) {
  return (
    <article className="overflow-hidden rounded-3xl border border-white/10 bg-white/[0.06] shadow-2xl shadow-black/20">
      {result.image_url ? (
        <div className="flex h-48 items-center justify-center bg-white/[0.03]">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={result.image_url} alt="" className="max-h-44 max-w-full object-contain" />
        </div>
      ) : null}
      <div className="p-5">
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
          href={buildOutboundUrl(result.url, { query, category, productId, provider: result.provider, title: result.title })}
          target="_blank"
          rel="sponsored noreferrer"
          className="mt-5 block rounded-2xl bg-white px-5 py-3 text-center font-semibold text-slate-950 transition hover:bg-slate-200"
        >
          View deal
        </a>
        <ReportBadResultButton result={result} query={query} category={category} productId={productId} />
        <div className="mt-3 space-y-2 text-xs leading-5 text-slate-500">
          <p>Scoutly may earn from qualifying purchases through affiliate links.</p>
          {result.affiliate_url_has_campaign_id ? (
            <p className="text-emerald-300/80">Affiliate tracking active for this eBay link.</p>
          ) : result.affiliate_url_used ? (
            <p className="text-amber-300/80">Affiliate URL returned, but campaign ID was not visible in the final link.</p>
          ) : null}
        </div>
      </div>
    </article>
  );
}
