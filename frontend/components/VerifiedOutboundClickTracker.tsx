"use client";

import { useEffect } from "react";
import { analyticsOptedOut } from "@/lib/analyticsOptOut";

function createClickReference(): string {
  const randomValues = new Uint32Array(2);
  crypto.getRandomValues(randomValues);
  const randomPart = Array.from(randomValues, (value) => value.toString(36)).join("");
  return `ps${Date.now().toString(36)}${randomPart}`.slice(0, 50);
}

function outboundClickEndpoint(anchor: HTMLAnchorElement): string | null {
  try {
    const redirectUrl = new URL(anchor.href, window.location.href);
    const normalizedPath = redirectUrl.pathname.replace(/\/+$/, "");

    if (!/^https?:$/.test(redirectUrl.protocol) || normalizedPath !== "/api/out") {
      return null;
    }

    redirectUrl.searchParams.set(
      "source_page",
      `${window.location.pathname}${window.location.search}`,
    );

    const destination = redirectUrl.searchParams.get("url");
    if (!destination) return null;
    const destinationUrl = new URL(destination);
    const hostname = destinationUrl.hostname.toLowerCase();
    const supportsPerClickReference =
      hostname === "awin1.com"
      || hostname.endsWith(".awin1.com")
      || hostname === "ebay.com"
      || hostname.endsWith(".ebay.com");
    if (supportsPerClickReference) {
      redirectUrl.searchParams.set("click_ref", createClickReference());
    }

    // The browser follows this exact URL after the capture listener returns,
    // while the POST below records the same click reference and page context.
    // Restore the rendered link on the next task so a later context-menu open
    // cannot accidentally reuse this click's reference.
    const originalHref = anchor.href;
    const navigationUrl = redirectUrl.toString();
    anchor.href = navigationUrl;
    window.setTimeout(() => {
      if (anchor.href === navigationUrl) anchor.href = originalHref;
    }, 0);
    redirectUrl.pathname = "/api/out/click";
    return redirectUrl.toString();
  } catch {
    return null;
  }
}

function recordVerifiedClick(endpoint: string): void {
  if (analyticsOptedOut()) return;

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
      if (analyticsOptedOut()) return;
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
