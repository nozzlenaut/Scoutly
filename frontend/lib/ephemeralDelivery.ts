"use client";

const DELIVERY_ZIP_EVENT = "pricesift:delivery-zip";

declare global {
  interface Window {
    __pricesiftDeliveryZip?: string;
  }
}

export function currentDeliveryZip(): string {
  if (typeof window === "undefined") return "";
  return window.__pricesiftDeliveryZip || "";
}

export function commitDeliveryZip(postalCode: string): void {
  if (typeof window === "undefined") return;
  const cleaned = postalCode.trim();
  window.__pricesiftDeliveryZip = cleaned;
  window.dispatchEvent(new CustomEvent(DELIVERY_ZIP_EVENT, { detail: cleaned }));
}

export function subscribeToDeliveryZip(listener: (postalCode: string) => void): () => void {
  if (typeof window === "undefined") return () => undefined;
  const handleChange = (event: Event) => {
    listener(String((event as CustomEvent<string>).detail || ""));
  };
  window.addEventListener(DELIVERY_ZIP_EVENT, handleChange);
  return () => window.removeEventListener(DELIVERY_ZIP_EVENT, handleChange);
}
