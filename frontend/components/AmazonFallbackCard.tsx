import { buildOutboundUrl } from "@/lib/api";
import {
  buildAmazonAllOptionsUrl,
  buildAmazonProductUrl,
  buildAmazonRenewedSearchUrl,
  buildAmazonUsedSearchUrl,
} from "@/lib/amazon";

type Props = {
  query: string;
  category: string;
  productId?: string;
  asin?: string | null;
  isbn10?: string | null;
  book?: boolean;
  emphasized?: boolean;
};

function trackedAmazonUrl(
  url: string,
  metadata: {
    query: string;
    category: string;
    productId?: string;
    title: string;
  },
): string {
  return buildOutboundUrl(url, {
    query: metadata.query,
    category: metadata.category,
    productId: metadata.productId,
    provider: "Amazon",
    title: metadata.title,
  });
}

export function AmazonFallbackCard({
  query,
  category,
  productId,
  asin,
  isbn10,
  book = false,
  emphasized = false,
}: Props) {
  const exactIdentifier = asin?.trim() || (book ? isbn10?.trim() : "");
  const exactUrl = exactIdentifier
    ? trackedAmazonUrl(buildAmazonProductUrl(exactIdentifier), {
        query,
        category,
        productId,
        title: `Amazon exact product: ${query}`,
      })
    : null;
  const usedUrl = trackedAmazonUrl(buildAmazonUsedSearchUrl(query), {
    query,
    category,
    productId,
    title: `Amazon used search: ${query}`,
  });
  const renewedUrl = trackedAmazonUrl(buildAmazonRenewedSearchUrl(query), {
    query,
    category,
    productId,
    title: `Amazon Renewed search: ${query}`,
  });
  const allOptionsUrl = trackedAmazonUrl(buildAmazonAllOptionsUrl(query), {
    query,
    category,
    productId,
    title: `Amazon all options search: ${query}`,
  });

  return (
    <section
      className={`mt-8 rounded-3xl border p-5 sm:p-6 ${
        emphasized
          ? "border-amber-300/30 bg-amber-300/[0.09]"
          : "border-orange-300/20 bg-orange-300/[0.05]"
      }`}
      aria-label="Amazon fallback"
    >
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-start">
        <div className="max-w-3xl">
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-orange-200">
            Also check Amazon · paid links
          </p>
          <h2 className="mt-2 text-2xl font-black">
            {emphasized ? "No safe match here? Check Amazon too." : "Compare with Amazon before buying."}
          </h2>
          <p className="mt-3 text-sm leading-6 text-slate-300">
            PriceSift does not have Amazon pricing or availability access yet. These links open Amazon directly,
            with used or renewed wording where practical. Amazon may still mix conditions or sellers, so verify the
            exact model, condition, and seller before purchasing.
          </p>
        </div>
        <span className="w-fit rounded-full border border-orange-200/20 bg-orange-200/10 px-3 py-1 text-xs font-semibold text-orange-100">
          Not ranked with PriceSift results
        </span>
      </div>

      <div className="mt-5 flex flex-wrap gap-3">
        {exactUrl ? (
          <a
            href={exactUrl}
            target="_blank"
            rel="sponsored noreferrer"
            className="rounded-2xl bg-orange-200 px-5 py-3 text-sm font-bold text-slate-950 transition hover:bg-orange-100"
          >
            {book ? "Check this exact edition on Amazon" : "Check exact product on Amazon"}
          </a>
        ) : (
          <a
            href={usedUrl}
            target="_blank"
            rel="sponsored noreferrer"
            className="rounded-2xl bg-orange-200 px-5 py-3 text-sm font-bold text-slate-950 transition hover:bg-orange-100"
          >
            Search used on Amazon
          </a>
        )}

        {book && exactUrl ? (
          <a
            href={usedUrl}
            target="_blank"
            rel="sponsored noreferrer"
            className="rounded-2xl border border-white/15 bg-white/[0.06] px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/[0.1]"
          >
            Search used copies
          </a>
        ) : null}

        {!book ? (
          <a
            href={renewedUrl}
            target="_blank"
            rel="sponsored noreferrer"
            className="rounded-2xl border border-white/15 bg-white/[0.06] px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/[0.1]"
          >
            Search Amazon Renewed
          </a>
        ) : null}

        <a
          href={allOptionsUrl}
          target="_blank"
          rel="sponsored noreferrer"
          className="rounded-2xl border border-white/15 bg-white/[0.06] px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/[0.1]"
        >
          See all Amazon options
        </a>
      </div>
    </section>
  );
}
