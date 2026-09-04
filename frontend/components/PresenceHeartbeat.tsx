"use client";

import { useEffect } from "react";
import { analyticsOptedOut } from "@/lib/analyticsOptOut";

const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const storageKey = "pricesift_presence_session";

function sessionId(): string {
  const existing = sessionStorage.getItem(storageKey);
  if (existing) return existing;
  const created = crypto.randomUUID().replaceAll("-", "");
  sessionStorage.setItem(storageKey, created);
  return created;
}

export function PresenceHeartbeat() {
  useEffect(() => {
    if (analyticsOptedOut()) return;

    const id = sessionId();
    const ping = () => {
      if (document.visibilityState !== "visible" || analyticsOptedOut()) return;
      void fetch(`${baseUrl}/api/presence`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: id }),
        keepalive: true,
      }).catch(() => undefined);
    };

    ping();
    const timer = window.setInterval(ping, 60_000);
    document.addEventListener("visibilitychange", ping);
    return () => {
      window.clearInterval(timer);
      document.removeEventListener("visibilitychange", ping);
    };
  }, []);

  return null;
}
