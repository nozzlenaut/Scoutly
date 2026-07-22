"use client";

import { useEffect } from "react";

function outboundClickEndpoint(anchor: HTMLAnchorElement): string | null {
  try {
    const redirectUrl = new URL(anchor.href, window.location.href);
    const normalizedPath = redirectUrl.pathname.replace(/\/+$/, "");

    if (!/^https?:$/.test(redirectUrl.protocol) || normalizedPath !== "/api/out") {
      return null;
    }

    redirectUrl.pathname = "/api/out/click";
    return redirectUrl.toString();
  } catch {
    return null;
  }
}

function recordVerifiedClick(endpoint: string): void {
  void fetch(endpoint, {
    method: "POST",
    mode: "cors",
    credentials: "omit",
    keepalive: true,
    cache: "no-store",
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Verified click request failed with ${response.status}`);
      }
    })
    .catch(() => {
      // Some browsers or privacy extensions may interrupt a cross-origin
      // keepalive request during navigation. Beacon is a best-effort fallback.
      navigator.sendBeacon?.(endpoint);
    });
}

export function VerifiedOutboundClickTracker() {
  useEffect(() => {
    function record(event: MouseEvent) {
      if (!event.isTrusted || event.defaultPrevented) return;
      if (event.type === "click" && event.button !== 0) return;
      if (event.type === "auxclick" && event.button !== 1) return;

      const target = event.target;
      if (!(target instanceof Element)) return;

      const anchor = target.closest<HTMLAnchorElement>("a[href]");
      if (!anchor) return;

      const endpoint = outboundClickEndpoint(anchor);
      if (!endpoint) return;

      recordVerifiedClick(endpoint);
    }

    document.addEventListener("click", record, true);
    document.addEventListener("auxclick", record, true);

    return () => {
      document.removeEventListener("click", record, true);
      document.removeEventListener("auxclick", record, true);
    };
  }, []);

  return null;
}
