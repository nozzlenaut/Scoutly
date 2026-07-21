"use client";

import { useEffect } from "react";

function outboundClickEndpoint(anchor: HTMLAnchorElement): string | null {
  try {
    const redirectUrl = new URL(anchor.href, window.location.href);
    if (!/^https?:$/.test(redirectUrl.protocol) || redirectUrl.pathname !== "/api/out") return null;
    redirectUrl.pathname = "/api/out/click";
    return redirectUrl.toString();
  } catch {
    return null;
  }
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

      if (navigator.sendBeacon?.(endpoint)) return;
      void fetch(endpoint, {
        method: "POST",
        mode: "cors",
        credentials: "omit",
        keepalive: true,
      }).catch(() => undefined);
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
