import Link from "next/link";
import { AdminKehLensLab } from "@/components/AdminKehLensLab";
import { SiteFooter } from "@/components/SiteFooter";
import { getKehLensBuilder } from "@/lib/api";

function Gate({ invalid = false }: { invalid?: boolean }) {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-white">
      <div className="mx-auto max-w-xl">
        <Link href="/" className="text-sm text-cyan-200">← PriceSift</Link>
        <section className="mt-10 rounded-3xl border border-white/10 bg-white/[0.05] p-6">
          <p className="text-sm uppercase tracking-[0.25em] text-slate-500">PriceSift KEH lenses</p>
          <h1 className="mt-2 text-3xl font-black">Admin token required</h1>
          <p className="mt-3 text-sm text-slate-400">{invalid ? "That token was not accepted." : "Use the same private token as the KEH shadow dashboard."}</p>
          <form method="get" action="/admin/keh/lenses" className="mt-5 flex flex-col gap-3 sm:flex-row">
            <input name="token" type="password" required placeholder="Admin token" className="flex-1 rounded-2xl border border-white/10 bg-white/[0.06] px-4 py-3 text-white" />
            <button className="rounded-2xl bg-white px-5 py-3 font-semibold text-slate-950">Open lens lab</button>
          </form>
        </section>
      </div>
    </main>
  );
}

export default async function KehLensAdminPage({ searchParams }: { searchParams: Promise<{ token?: string }> }) {
  const token = (await searchParams).token?.trim();
  if (!token) return <Gate />;
  let data;
  try {
    data = await getKehLensBuilder(token, { limit: 150 });
  } catch {
    return <Gate invalid />;
  }

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-8 text-white sm:px-6 sm:py-10">
      <div className="mx-auto max-w-[1500px]">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <Link href={`/admin/keh?token=${encodeURIComponent(token)}`} className="text-sm text-cyan-200">← KEH shadow feed</Link>
          <Link href={`/admin?token=${encodeURIComponent(token)}`} className="text-sm text-slate-400">Testing dashboard</Link>
        </div>
        <div className="mt-8">
          <p className="text-sm uppercase tracking-[0.25em] text-slate-500">PriceSift admin experiment</p>
          <h1 className="mt-2 text-4xl font-black">KEH lens builder lab</h1>
          <p className="mt-3 max-w-4xl text-slate-400">
            Tests a KEH-only lens flow against the live shadow inventory. It does not add a public category, alter camera results, or publish any lens listing.
          </p>
        </div>
        <AdminKehLensLab initialData={data} token={token} />
        <SiteFooter />
      </div>
    </main>
  );
}
