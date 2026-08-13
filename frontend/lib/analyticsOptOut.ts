export const ANALYTICS_OPT_OUT_COOKIE = "pricesift_analytics_opt_out";

export function analyticsOptedOut(): boolean {
  if (typeof document === "undefined") return false;
  return document.cookie
    .split(";")
    .some((part) => part.trim() === `${ANALYTICS_OPT_OUT_COOKIE}=1`);
}

export function setAnalyticsOptOut(enabled: boolean): void {
  if (typeof document === "undefined") return;
  const secure = location.protocol === "https:" ? "; Secure" : "";
  document.cookie = enabled
    ? `${ANALYTICS_OPT_OUT_COOKIE}=1; Path=/; Max-Age=31536000; SameSite=Lax${secure}`
    : `${ANALYTICS_OPT_OUT_COOKIE}=; Path=/; Max-Age=0; SameSite=Lax${secure}`;
}
