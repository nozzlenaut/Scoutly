import type { DeliveryEstimateItem, SearchResult } from "@/lib/api";
import { buildOutboundUrl } from "@/lib/api";
import { ReportBadResultButton } from "@/components/ReportBadResultButton";

type Props = {
  result: SearchResult;
  query: string;
  category: string;
  productId?: string;
  variant?: "buy_now" | "auction";
  deliveryStatus?: "idle" | "loading" | "done" | "error";
  deliveryEstimate?: DeliveryEstimateItem | null;
};

function deliveryDate(value?: string | null): string | null {
  if (!value) return null;
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return null;
  return parsed.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

function deliveryWindow(estimate: DeliveryEstimateItem): string {
  const first = deliveryDate(estimate.best_shipping_option?.min_delivery);
  const last = deliveryDate(estimate.best_shipping_option?.max_delivery);
  if (first && last && first !== last) return `${first}–${last}`;
  return first || last || "Delivery date not provided";
}

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
  if (result.provider.toLowerCase() === "keh") return "KEH Camera";
  const rating = result.seller_rating !== null ? `${result.seller_rating}% positive` : null;
  const feedback = result.seller_feedback_score;
  if (rating === null && feedback === null) return "Seller history unavailable";
  if (rating === null) return `${feedback?.toLocaleString()} feedback · rating unavailable`;
  if (feedback === null) return `${rating} · feedback unavailable`;
  return `${rating} · ${feedback.toLocaleString()} feedback`;
}

function sellerTrustLabel(result: SearchResult): string | null {
  if (result.provider.toLowerCase() === "keh") return null;
  const feedback = result.seller_feedback_score;
  if (feedback === null) return "Seller history unavailable";
  if (feedback <= 5) return "New / low-feedback seller";
  if (feedback <= 10) return "Limited seller feedback";
  if (result.seller_rating !== null && result.seller_rating < 95) return "Lower seller rating";
  return null;
}

export function ResultCard({
  result,
  query,
  category,
  productId,
  variant = "buy_now",
  deliveryStatus = "idle",
  deliveryEstimate = null,
}: Props) {
  const isAuction = variant === "auction" || result.listing_type === "auction";
  const endLabel = formatEndDate(result.item_end_date);
  const priceLabel = isAuction ? "Current bid" : "Item price";
  const combinedLabel = isAuction ? "Bid + shipping" : "Item + shipping";
  const trustLabel = sellerTrustLabel(result);
  const hasCaution = Boolean(trustLabel) || result.warning_labels.length > 0;
  const hasEstimatedShipping = Boolean(
    deliveryEstimate?.detail_loaded
    && deliveryEstimate.shipping_cost !== null
    && deliveryEstimate.shipping_cost !== undefined,
  );
  const displayedShipping = hasEstimatedShipping
    ? Number(deliveryEstimate?.shipping_cost)
    : result.shipping;
  const displayedTotal = hasEstimatedShipping && deliveryEstimate?.total_price !== null && deliveryEstimate?.total_price !== undefined
    ? deliveryEstimate.total_price
    : result.total_price;
  const outboundUrl = buildOutboundUrl(result.url, {
    query,
    category,
    productId,
    provider: result.provider,
    title: result.title,
  });

  return (
    <article className="flex h-full flex-col overflow-hidden rounded-3xl border border-white/10 bg-white/[0.06] shadow-2xl shadow-black/20">
      <div className="flex h-44 items-center justify-center bg-white/[0.03]">
        {result.image_url ? (
          <a
            href={outboundUrl}
            target="_blank"
            rel="sponsored noreferrer"
            aria-label={`View listing: ${result.title}`}
            className="flex h-full w-full items-center justify-center p-2 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-cyan-300"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={result.image_url}
              alt={result.title}
              loading="lazy"
              className="max-h-40 max-w-full object-contain transition duration-200 hover:scale-[1.02]"
            />
          </a>
        ) : (
          <span className="text-sm text-slate-400">No image</span>
        )}
      </div>

      <div className="flex flex-1 flex-col p-5">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <span className="rounded-full bg-white/10 px-3 py-1 text-sm font-medium text-cyan-100">
            {result.provider}
          </span>
          <div className="flex flex-wrap justify-end gap-2">
            <span className="rounded-full bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-slate-200">
              {isAuction ? "Auction" : "Buy It Now"}
            </span>
            <span
              className={`rounded-full border px-3 py-1 text-xs font-semibold ${
                hasCaution
                  ? "border-amber-300/30 bg-amber-300/10 text-amber-100"
                  : "border-emerald-300/25 bg-emerald-300/10 text-emerald-100"
              }`}
            >
              {hasCaution ? "Listing checks: review" : "Listing checks passed"}
            </span>
            {result.affiliate_url_used ? (
              <span className="rounded-full border border-emerald-300/20 bg-emerald-300/10 px-3 py-1 text-xs font-semibold text-emerald-100">
                Affiliate link
              </span>
            ) : null}
          </div>
        </div>

        <h2 className="text-lg font-semibold leading-snug text-white">
          <a
            href={outboundUrl}
            target="_blank"
            rel="sponsored noreferrer"
            className="transition hover:text-cyan-200 hover:underline focus-visible:rounded focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-300"
          >
            {result.title}
          </a>
        </h2>

        {trustLabel ? (
          <div className="mt-3 rounded-2xl border border-amber-300/25 bg-amber-300/10 px-4 py-3 text-sm text-amber-100">
            {trustLabel}. PriceSift lowers risky sellers in ranking, but check the seller before buying.
          </div>
        ) : null}

        {result.warning_labels.length > 0 ? (
          <div className="mt-3 rounded-2xl border border-orange-300/25 bg-orange-300/10 px-4 py-3 text-sm text-orange-100">
            {result.warning_labels.join(" · ")}
          </div>
        ) : null}

        <div className="mt-4 grid gap-2 text-sm text-slate-200 sm:grid-cols-3 xl:grid-cols-1 2xl:grid-cols-3">
          <div className="rounded-2xl bg-slate-950/35 p-3">
            <span className="block text-xs uppercase tracking-[0.16em] text-slate-400">{priceLabel}</span>
            <span className="mt-1 block text-lg font-bold text-white">${result.price.toFixed(2)}</span>
          </div>
          <div className="rounded-2xl bg-slate-950/35 p-3">
            <span className="block text-xs uppercase tracking-[0.16em] text-slate-400">
              {hasEstimatedShipping ? "Shipping to ZIP" : "Shipping"}
            </span>
            <span className="mt-1 block text-lg font-bold text-white">
              {displayedShipping === 0 ? "Free" : `$${displayedShipping.toFixed(2)}`}
            </span>
          </div>
          <div className="rounded-2xl bg-slate-950/35 p-3">
            <span className="block text-xs uppercase tracking-[0.16em] text-slate-400">{combinedLabel}</span>
            <span className="mt-1 block text-lg font-bold text-emerald-200">${displayedTotal.toFixed(2)}</span>
          </div>
        </div>
        <p className="mt-2 text-xs leading-5 text-slate-400">
          Taxes and import charges, if any, are not included in this displayed amount.
        </p>

        {result.provider.toLowerCase() === "ebay" && !isAuction && deliveryStatus !== "idle" ? (
          <div className="mt-4 rounded-2xl border border-cyan-200/15 bg-cyan-200/[0.07] px-4 py-3 text-sm" aria-live="polite">
            {deliveryStatus === "loading" ? (
              <p className="flex items-center gap-2 font-semibold text-cyan-100">
                <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-cyan-100/30 border-t-cyan-100" />
                Checking delivery for this listing…
              </p>
            ) : deliveryStatus === "error" ? (
              <p className="text-slate-300">Delivery estimate unavailable. The listing is still usable.</p>
            ) : deliveryEstimate?.detail_loaded ? (
              <>
                <p className="text-xs font-bold uppercase tracking-[0.16em] text-cyan-100">eBay delivery estimate</p>
                <p className="mt-1 font-bold text-emerald-200">{deliveryWindow(deliveryEstimate)}</p>
                <p className="mt-1 text-xs text-slate-400">
                  {deliveryEstimate.best_shipping_option?.service
                    || deliveryEstimate.best_shipping_option?.carrier
                    || deliveryEstimate.best_shipping_option?.speed
                    || "Shipping method not provided"}
                </p>
              </>
            ) : (
              <p className="text-slate-300">eBay did not provide a delivery estimate for this listing.</p>
            )}
          </div>
        ) : null}

        <div className="mt-4 grid gap-2 text-sm text-slate-300">
          <div className="flex justify-between gap-4"><span>Condition</span><span className="text-right text-slate-100">{result.condition}</span></div>
          <div className="flex justify-between gap-4"><span>Seller</span><span className="text-right text-slate-100">{sellerLabel(result)}</span></div>
          {result.item_location ? (
            <div className="flex justify-between gap-4"><span>Location</span><span className="text-right text-slate-100">{result.item_location}</span></div>
          ) : null}
          {isAuction ? (
            <>
              <div className="flex justify-between gap-4"><span>Bids</span><span className="text-slate-100">{result.bid_count ?? "Unknown"}</span></div>
              {endLabel ? <div className="flex justify-between gap-4"><span>Auction</span><span className="text-slate-100">{endLabel}</span></div> : null}
            </>
          ) : null}
        </div>

        <div className="mt-auto pt-5">
          <a
            href={outboundUrl}
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
