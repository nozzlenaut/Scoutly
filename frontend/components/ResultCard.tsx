import type { SearchResult } from "@/lib/api";
import { buildOutboundUrl } from "@/lib/api";
import { ReportBadResultButton } from "@/components/ReportBadResultButton";

type Props = {
  result: SearchResult;
  query: string;
  category: string;
  productId?: string;
  variant?: "buy_now" | "auction";
};

function formatEndDate(value: string | null): string | null {
  if (!value) return null;
  const end = new Date(value);
  if (Number.isNaN(end.getTime())) return null;

  const now = Date.now();
  const ms = end.getTime() - now;
  if (ms <= 0) return "ending now";

  const hours = Math.floor(ms / (1000 * 60 * 60));
  const minutes = Math.floor((ms % (1000 * 60 * 60)) / (1000 * 60));
  if (hours <= 0) return `ends in ${minutes}m`;
  return `ends in ${hours}h ${minutes}m`;
}

function sellerLabel(result: SearchResult): string {
  const rating = result.seller_rating !== null ? `${result.seller_rating}% positive` : "Rating unknown";
  const feedback = result.seller_feedback_score;
  if (feedback === null) return rating;
  return `${rating} · ${feedback.toLocaleString()} feedback`;
}

function sellerTrustLabel(result: SearchResult): string | null {
  const feedback = result.seller_feedback_score;
  if (feedback === null) return null;
  if (feedback <= 5) return "New / low-feedback seller";
  if (feedback <= 10) return "Limited seller feedback";
  return null;
}

export function ResultCard({ result, query, category, productId, variant = "buy_now" }: Props) {
  const isAuction = variant === "auction" || result.listing_type === "auction";
  const endLabel = formatEndDate(result.item_end_date);
  const priceLabel = isAuction ? "Current bid" : "Item price";
  const totalLabel = isAuction ? "Current total" : "Total";
  const trustLabel = sellerTrustLabel(result);

  return (
    <article className="flex h-full flex-col overflow-hidden rounded-3xl border border-white/10 bg-white/[0.06] shadow-2xl shadow-black/20">
      <div className="flex h-44 items-center justify-center bg-white/[0.03]">
        {result.image_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={result.image_url} alt={result.title} loading="lazy" className="max-h-40 max-w-full object-contain" />
        ) : (
          <span className="text-sm text-slate-500">No image</span>
        )}
      </div>

      <div className="flex flex-1 flex-col p-5">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <span className="rounded-full bg-white/10 px-3 py-1 text-sm font-medium text-cyan-200">
            {result.provider}
          </span>
          <div className="flex flex-wrap justify-end gap-2">
            <span className="rounded-full bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-slate-300">
              {isAuction ? "Auction" : "Buy It Now"}
            </span>
            {result.affiliate_url_used ? (
              <span className="rounded-full border border-emerald-300/20 bg-emerald-300/10 px-3 py-1 text-xs font-semibold text-emerald-100">
                Sponsored link
              </span>
            ) : null}
          </div>
        </div>

        <h2 className="text-lg font-semibold leading-snug text-white">{result.title}</h2>

        {trustLabel ? (
          <div className="mt-3 rounded-2xl border border-amber-300/25 bg-amber-300/10 px-4 py-3 text-sm text-amber-100">
            {trustLabel}. Price may be good, but check the seller carefully.
          </div>
        ) : null}

        {result.warning_labels.length > 0 ? (
          <div className="mt-3 rounded-2xl border border-orange-300/25 bg-orange-300/10 px-4 py-3 text-sm text-orange-100">
            {result.warning_labels.join(" · ")}
          </div>
        ) : null}

        <div className="mt-4 grid gap-2 text-sm text-slate-300 sm:grid-cols-3 xl:grid-cols-1 2xl:grid-cols-3">
          <div className="rounded-2xl bg-slate-950/35 p-3">
            <span className="block text-xs uppercase tracking-[0.16em] text-slate-500">{priceLabel}</span>
            <span className="mt-1 block text-lg font-bold text-white">${result.price.toFixed(2)}</span>
          </div>
          <div className="rounded-2xl bg-slate-950/35 p-3">
            <span className="block text-xs uppercase tracking-[0.16em] text-slate-500">Shipping</span>
            <span className="mt-1 block text-lg font-bold text-white">${result.shipping.toFixed(2)}</span>
          </div>
          <div className="rounded-2xl bg-slate-950/35 p-3">
            <span className="block text-xs uppercase tracking-[0.16em] text-slate-500">{totalLabel}</span>
            <span className="mt-1 block text-lg font-bold text-emerald-200">${result.total_price.toFixed(2)}</span>
          </div>
        </div>

        <div className="mt-4 grid gap-2 text-sm text-slate-400">
          <div className="flex justify-between gap-4"><span>Condition</span><span className="text-right text-slate-200">{result.condition}</span></div>
          <div className="flex justify-between gap-4"><span>Seller</span><span className="text-right text-slate-200">{sellerLabel(result)}</span></div>
          {result.item_location ? (
            <div className="flex justify-between gap-4"><span>Location</span><span className="text-right text-slate-200">{result.item_location}</span></div>
          ) : null}
          {isAuction ? (
            <>
              <div className="flex justify-between gap-4"><span>Bids</span><span className="text-slate-200">{result.bid_count ?? "Unknown"}</span></div>
              {endLabel ? <div className="flex justify-between gap-4"><span>Auction</span><span className="text-slate-200">{endLabel}</span></div> : null}
            </>
          ) : null}
        </div>

        <div className="mt-auto pt-5">
          <a
            href={buildOutboundUrl(result.url, { query, category, productId, provider: result.provider, title: result.title })}
            target="_blank"
            rel="sponsored noreferrer"
            className="block rounded-2xl bg-white px-5 py-3 text-center font-semibold text-slate-950 transition hover:bg-slate-200"
          >
            {isAuction ? "View auction" : "View deal"}
          </a>
          <ReportBadResultButton result={result} query={query} category={category} productId={productId} />
        </div>
      </div>
    </article>
  );
}
