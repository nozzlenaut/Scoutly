import Link from "next/link";
import { AdminKehDashboard } from "@/components/AdminKehDashboard";
import { SiteFooter } from "@/components/SiteFooter";
import { getKehOverview } from "@/lib/api";

function Gate({ invalid = false }: { invalid?: boolean }) {
  return <main className="min-h-screen bg-slate-950 px-6 py-10 text-white"><div className="mx-auto max-w-xl"><Link href="/" className="text-sm text-cyan-200">← PriceSift</Link><section className="mt-10 rounded-3xl border border-white/10 bg-white/[0.05] p-6"><p className="text-sm uppercase tracking-[0.25em] text-slate-500">PriceSift KEH</p><h1 className="mt-2 text-3xl font-black">Admin token required</h1><p className="mt-3 text-sm text-slate-400">{invalid ? "That token was not accepted." : "Use the same private token as the testing dashboard."}</p><form method="get" action="/admin/keh" className="mt-5 flex flex-col gap-3 sm:flex-row"><input name="token" type="password" required placeholder="Admin token" className="flex-1 rounded-2xl border border-white/10 bg-white/[0.06] px-4 py-3 text-white"/><button className="rounded-2xl bg-white px-5 py-3 font-semibold text-slate-950">Open KEH</button></form></section></div></main>;
}

export default async function KehAdminPage({ searchParams }: { searchParams: Promise<{ token?: string }> }) {
  const token = (await searchParams).token?.trim();
  if (!token) return <Gate />;
  let overview;
  try { overview = await getKehOverview(token, 1000); } catch { return <Gate invalid />; }
  return <main className="min-h-screen bg-slate-950 px-6 py-10 text-white"><div className="mx-auto max-w-[1500px]"><div className="flex flex-wrap items-center justify-between gap-4"><Link href={`/admin?token=${encodeURIComponent(token)}`} className="text-sm text-cyan-200">← Testing dashboard</Link><div className="flex flex-wrap gap-4"><Link href={`/admin/keh/lenses?token=${encodeURIComponent(token)}`} className="text-sm text-emerald-200">Lens builder lab</Link><Link href={`/admin/qa?token=${encodeURIComponent(token)}`} className="text-sm text-slate-400">Search QA</Link></div></div><div className="mt-8"><p className="text-sm uppercase tracking-[0.25em] text-slate-500">PriceSift admin</p><h1 className="mt-2 text-4xl font-black">KEH shadow feed</h1><p className="mt-3 max-w-4xl text-slate-400">Imports KEH camera bodies and interchangeable lenses. Camera bodies use the controlled catalog pilot; lens inventory remains private and can be explored in the Lens Builder Lab.</p></div><AdminKehDashboard initialOverview={overview} token={token}/><SiteFooter /></div></main>;
}
