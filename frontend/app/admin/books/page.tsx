import Link from "next/link";
import { AdminBookIsbnLab } from "@/components/AdminBookIsbnLab";
import { SiteFooter } from "@/components/SiteFooter";
import { getBooksLabStatus } from "@/lib/api";

function Gate({ invalid = false }: { invalid?: boolean }) {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-white">
      <div className="mx-auto max-w-xl">
        <Link href="/" className="text-sm text-cyan-200">← PriceSift</Link>
        <section className="mt-10 rounded-3xl border border-white/10 bg-white/[0.05] p-6">
          <p className="text-sm uppercase tracking-[0.25em] text-slate-500">PriceSift Books lab</p>
          <h1 className="mt-2 text-3xl font-black">Admin token required</h1>
          <p className="mt-3 text-sm text-slate-400">{invalid ? "That token was not accepted." : "Use the same private token as the other testing pages."}</p>
          <form method="get" action="/admin/books" className="mt-5 flex flex-col gap-3 sm:flex-row">
            <input name="token" type="password" required placeholder="Admin token" className="flex-1 rounded-2xl border border-white/10 bg-white/[0.06] px-4 py-3 text-white" />
            <button className="rounded-2xl bg-white px-5 py-3 font-semibold text-slate-950">Open Books lab</button>
          </form>
        </section>
      </div>
    </main>
  );
}

export default async function BooksAdminPage({ searchParams }: { searchParams: Promise<{ token?: string }> }) {
  const token = (await searchParams).token?.trim();
  if (!token) return <Gate />;
  try {
    await getBooksLabStatus(token);
  } catch {
    return <Gate invalid />;
  }

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-8 text-white sm:px-6 sm:py-10">
      <div className="mx-auto max-w-[1500px]">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <Link href={`/admin?token=${encodeURIComponent(token)}`} className="text-sm text-cyan-200">← Testing dashboard</Link>
          <Link href={`/admin/qa?token=${encodeURIComponent(token)}`} className="text-sm text-slate-400">Search QA</Link>
        </div>
        <div className="mt-8">
          <p className="text-sm uppercase tracking-[0.25em] text-slate-500">PriceSift public-beta diagnostics</p>
          <h1 className="mt-2 text-4xl font-black">Books ISBN lab</h1>
          <p className="mt-3 max-w-4xl text-slate-400">
            Inspect the ISBN lookup path, rejections, and collectible separation behind the public Books beta.
          </p>
        </div>
        <AdminBookIsbnLab token={token} />
        <SiteFooter />
      </div>
    </main>
  );
}
