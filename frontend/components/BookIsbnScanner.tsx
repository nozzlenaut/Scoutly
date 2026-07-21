"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

type DetectedBarcode = { rawValue?: string };
type BarcodeDetectorInstance = {
  detect(source: HTMLVideoElement): Promise<DetectedBarcode[]>;
};
type BarcodeDetectorConstructor = new (options?: { formats?: string[] }) => BarcodeDetectorInstance;
type ScannerWindow = Window & { BarcodeDetector?: BarcodeDetectorConstructor };

function validIsbn13(value: string): boolean {
  if (!/^97[89]\d{10}$/.test(value)) return false;
  const digits = value.split("").map(Number);
  const weighted = digits.slice(0, 12).reduce(
    (sum, digit, index) => sum + digit * (index % 2 === 0 ? 1 : 3),
    0,
  );
  return (10 - (weighted % 10)) % 10 === digits[12];
}

export function BookIsbnScanner({ usOnly = false }: { usOnly?: boolean }) {
  const router = useRouter();
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const stoppedRef = useRef(false);
  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState("Aim at the ISBN barcode on the back cover.");
  const [error, setError] = useState<string | null>(null);

  function stopCamera() {
    stoppedRef.current = true;
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = null;
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (videoRef.current) videoRef.current.srcObject = null;
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
    setStatus("Starting camera…");

    async function begin() {
      const Detector = (window as ScannerWindow).BarcodeDetector;
      if (!Detector) {
        setError("This browser cannot scan barcodes here yet. You can still type the ISBN above.");
        return;
      }
      if (!navigator.mediaDevices?.getUserMedia) {
        setError("Camera access is not available in this browser. You can still type the ISBN above.");
        return;
      }

      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: false,
          video: { facingMode: { ideal: "environment" } },
        });
        if (stoppedRef.current) {
          stream.getTracks().forEach((track) => track.stop());
          return;
        }

        streamRef.current = stream;
        const video = videoRef.current;
        if (!video) {
          stopCamera();
          return;
        }
        video.srcObject = stream;
        await video.play();
        const detector = new Detector({ formats: ["ean_13"] });
        setStatus("Aim at the ISBN barcode on the back cover.");

        const scan = async () => {
          if (stoppedRef.current || !videoRef.current) return;
          try {
            const barcodes = await detector.detect(videoRef.current);
            for (const barcode of barcodes) {
              const digits = (barcode.rawValue || "").replace(/\D/g, "");
              if (validIsbn13(digits)) {
                setStatus(`ISBN ${digits} found. Searching…`);
                navigateToIsbn(digits);
                return;
              }
            }
          } catch {
            // A frame can fail while the camera is focusing. Keep scanning.
          }
          timerRef.current = setTimeout(scan, 180);
        };

        void scan();
      } catch {
        stopCamera();
        setError("Camera permission was blocked or the camera could not start. You can still type the ISBN above.");
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
        <div className="fixed inset-0 z-[200] flex items-center justify-center bg-slate-950/90 p-4" role="dialog" aria-modal="true" aria-label="Scan ISBN barcode">
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

            <div className="mt-5 overflow-hidden rounded-2xl border border-white/10 bg-black">
              <video ref={videoRef} muted playsInline className="aspect-[4/3] w-full object-cover" />
            </div>
            <p className={`mt-4 text-sm leading-6 ${error ? "text-amber-200" : "text-slate-300"}`} role={error ? "alert" : "status"}>
              {error || status}
            </p>
          </div>
        </div>
      ) : null}
    </>
  );
}
