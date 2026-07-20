import type { Metadata } from "next";
import Link from "next/link";
import { PublicKehCameraDirectory } from "@/components/PublicKehCameraDirectory";
import { SiteFooter } from "@/components/SiteFooter";
import { getPublicKehCameraCatalog, type KehCameraCatalogResponse } from "@/lib/api";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Used camera models and current KEH inventory",
  description: "Browse current used camera models at KEH. PriceSift catalog matches compare eBay and KEH; additional KEH models remain KEH-only.",
  alternates: { canonical: "/cameras" },
};

export default async function CamerasPage() {
  let data: KehCameraCatalogResponse | null = null;
  try {
    data = await getPublicKehCameraCatalog({ limit: 1000 });
  } catch {
    data = null;
  }

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-8 text-white sm:px-6 sm:py-10">
      <div className="mx-auto max-w-[1500px]">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <Link href="/" className="text-2xl font-black tracking-tight text-white">PriceSift</Link>
          <Link href="/#search" className="text-sm font-semibold text-cyan-200 hover:text-cyan-100">Search all categories</Link>
        </div>

        <section className="mt-8">
          <p className="text-sm uppercase tracking-[0.25em] text-cyan-200">Current used-camera inventory</p>
          <h1 className="mt-2 max-w-5xl text-4xl font-black sm:text-5xl">Camera models currently available at KEH</h1>
          <p className="mt-4 max-w-4xl text-base leading-7 text-slate-300">
            KEH’s standardized feed is grouped into exact camera models. Models confidently matched to PriceSift’s tuned catalog can compare eBay and KEH. Everything else remains KEH-only instead of being sent through an unsafe broad marketplace search.
          </p>
        </section>

        {data ? (
          <PublicKehCameraDirectory data={data} />
        ) : (
          <div className="mt-8 rounded-3xl border border-amber-300/20 bg-amber-300/10 p-7 text-amber-50">
            <h2 className="text-2xl font-black">KEH camera inventory is temporarily unavailable.</h2>
            <p className="mt-3 text-sm text-amber-100/90">Try the normal PriceSift camera search while the next feed sync completes.</p>
          </div>
        )}

        <SiteFooter />
      </div>
    </main>
  );
}
