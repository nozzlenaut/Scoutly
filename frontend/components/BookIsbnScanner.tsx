"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import type { IScannerControls } from "@zxing/browser";

function validIsbn13(value: string): boolean {
  if (!/^97[89]\d{10}$/.test(value)) return false;
  const digits = value.split("").map(Number);
  const weighted = digits.slice(0, 12).reduce(
    (sum, digit, index) => sum + digit * (index % 2 === 0 ? 1 : 3),
    0,
  );
  return (10 - (weighted % 10)) % 10 === digits[12];
}

function cameraErrorMessage(error: unknown): string {
  const name = error instanceof DOMException ? error.name : "";
  if (name === "NotAllowedError" || name === "SecurityError") {
    return "Camera permission was blocked. Allow camera access for PriceSift, then open the scanner again.";
  }
  if (name === "NotFoundError" || name === "OverconstrainedError") {
    return "No usable rear camera was found. You can still type the ISBN above.";
  }
  if (name === "NotReadableError" || name === "AbortError") {
    return "The camera is busy or could not start. Close other camera apps and try again.";
  }
  return "The camera could not start. You can still type the ISBN above.";
}

export function BookIsbnScanner({ usOnly = false }: { usOnly?: boolean }) {
  const router = useRouter();
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const controlsRef = useRef<IScannerControls | null>(null);
  const stoppedRef = useRef(false);
  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState("Aim at the ISBN barcode on the back cover.");
  const [error, setError] = useState<string | null>(null);

  function stopCamera() {
    stoppedRef.current = true;
    controlsRef.current?.stop();
    controlsRef.current = null;

    const video = videoRef.current;
    if (video?.srcObject instanceof MediaStream) {
      video.srcObject.getTracks().forEach((track) => track.stop());
    }
    if (video) video.srcObject = null;
  }

  function closeScanner() {
    stopCamera();
    setOpen(false);
  }

  function navigateToIsbn(isbn: string) {
    stopCamera();
    setOpen(false);
    const params = new URLSearchParams({ category: "books", q: isbn });
    if (usOnly) params.set("us_only", "1");
    window.dispatchEvent(new CustomEvent("pricesift:search-start"));
    router.push(`/search?${params.toString()}`);
  }

  useEffect(() => {
    if (!open) return;

    stoppedRef.current = false;
    setError(null);
    setStatus("Loading barcode scanner…");

    async function begin() {
      if (!window.isSecureContext) {
        setError("Camera scanning requires a secure HTTPS page. You can still type the ISBN above.");
        return;
      }
      if (!navigator.mediaDevices?.getUserMedia) {
        setError("Camera access is not available in this browser. You can still type the ISBN above.");
        return;
      }

      try {
        const [{ BrowserMultiFormatReader }, { BarcodeFormat, DecodeHintType }] = await Promise.all([
          import("@zxing/browser"),
          import("@zxing/library"),
        ]);
        if (stoppedRef.current) return;

        const video = videoRef.current;
        if (!video) return;

        const hints = new Map();
        hints.set(DecodeHintType.POSSIBLE_FORMATS, [BarcodeFormat.EAN_13]);
        hints.set(DecodeHintType.TRY_HARDER, true);

        const reader = new BrowserMultiFormatReader(hints, {
          delayBetweenScanAttempts: 140,
          delayBetweenScanSuccess: 500,
          tryPlayVideoTimeout: 5000,
        });

        setStatus("Starting rear camera…");
        const controls = await reader.decodeFromConstraints(
          {
            audio: false,
            video: {
              facingMode: { ideal: "environment" },
              width: { ideal: 1280 },
              height: { ideal: 720 },
            },
          },
          video,
          (result) => {
            if (!result || stoppedRef.current) return;
            const digits = result.getText().replace(/\D/g, "");
            if (!validIsbn13(digits)) {
              setStatus("That barcode is not a valid ISBN-13. Try the barcode beginning with 978 or 979.");
              return;
            }

            setStatus(`ISBN ${digits} found. Searching…`);
            navigateToIsbn(digits);
          },
        );

        if (stoppedRef.current) {
          controls.stop();
          return;
        }

        controlsRef.current = controls;
        setStatus("Aim the 978 or 979 ISBN barcode inside the box.");
      } catch (scanError) {
        stopCamera();
        setError(cameraErrorMessage(scanError));
      }
    }

    void begin();
    return stopCamera;
  }, [open]);

  return (
    <>
      <div className="mt-3 flex flex-col justify-between gap-3 rounded-2xl border border-cyan-300/15 bg-cyan-300/[0.05] p-4 sm:flex-row sm:items-center">
        <div>
          <p className="font-semibold text-cyan-50">Have the book in your hand?</p>
          <p className="mt-1 text-sm text-slate-300">Scan the back-cover ISBN barcode instead of typing it.</p>
        </div>
        <button
          type="button"
          onClick={() => setOpen(true)}
          className="min-h-11 rounded-xl border border-cyan-200/25 bg-cyan-200/10 px-5 text-sm font-bold text-cyan-50 transition hover:bg-cyan-200/15"
        >
          Scan ISBN
        </button>
      </div>

      {open ? (
        <div
          className="fixed inset-0 z-[200] flex items-center justify-center bg-slate-950/90 p-4"
          role="dialog"
          aria-modal="true"
          aria-label="Scan ISBN barcode"
        >
          <div className="w-full max-w-lg rounded-3xl border border-white/10 bg-slate-900 p-5 shadow-2xl">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-cyan-200">ISBN scanner</p>
                <h2 className="mt-1 text-2xl font-black">Scan the book barcode</h2>
              </div>
              <button
                type="button"
                onClick={closeScanner}
                className="rounded-xl border border-white/10 px-3 py-2 text-sm text-slate-200 hover:bg-white/[0.08]"
                aria-label="Close ISBN scanner"
              >
                Close
              </button>
            </div>

            <div className="relative mt-5 overflow-hidden rounded-2xl border border-white/10 bg-black">
              <video ref={videoRef} muted playsInline autoPlay className="aspect-[4/3] w-full object-cover" />
              {!error ? (
                <div
                  className="pointer-events-none absolute inset-x-[9%] top-1/2 h-24 -translate-y-1/2 rounded-xl border-2 border-cyan-200/90 shadow-[0_0_0_999px_rgba(2,6,23,0.35)]"
                  aria-hidden="true"
                />
              ) : null}
            </div>

            <p
              className={`mt-4 text-sm leading-6 ${error ? "text-amber-200" : "text-slate-300"}`}
              role={error ? "alert" : "status"}
            >
              {error || status}
            </p>
          </div>
        </div>
      ) : null}
    </>
  );
}
