const AMAZON_ORIGIN = "https://www.amazon.com";

function associateTag(): string {
  return process.env.NEXT_PUBLIC_AMAZON_ASSOCIATE_TAG?.trim() || "average3d-20";
}

function cleanProductIdentifier(value: string): string {
  return value.trim().replace(/[^A-Za-z0-9]/g, "").slice(0, 20);
}

function buildAmazonSearchUrl(query: string): string {
  const params = new URLSearchParams({
    k: query.trim(),
    tag: associateTag(),
  });
  return `${AMAZON_ORIGIN}/s?${params.toString()}`;
}

export function buildAmazonProductUrl(asin: string): string {
  const cleanAsin = cleanProductIdentifier(asin);
  if (!cleanAsin) return buildAmazonAllOptionsUrl(asin);
  const params = new URLSearchParams({ tag: associateTag() });
  return `${AMAZON_ORIGIN}/dp/${encodeURIComponent(cleanAsin)}?${params.toString()}`;
}

export function buildAmazonUsedSearchUrl(query: string): string {
  return buildAmazonSearchUrl(`${query.trim()} used`);
}

export function buildAmazonRenewedSearchUrl(query: string): string {
  return buildAmazonSearchUrl(`${query.trim()} renewed`);
}

export function buildAmazonAllOptionsUrl(query: string): string {
  return buildAmazonSearchUrl(query);
}
