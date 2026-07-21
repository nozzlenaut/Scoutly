import Link from "next/link";
import { AdminLoginForm } from "@/components/AdminLoginForm";
import { ADMIN_BROWSER_SESSION, getAdminToken } from "@/lib/adminSession";
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
          <AdminLoginForm next="/admin/books" />
        </section>
      </div>
    </main>
  );
}

export default async function BooksAdminPage({ searchParams }: { searchParams: Promise<{ invalid?: string }> }) {
  const params = await searchParams;
  const token = await getAdminToken();
  if (!token) return <Gate invalid={params.invalid === "1"} />;
  try {
    await getBooksLabStatus(token);
  } catch {
    return <Gate invalid />;
  }

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-8 text-white sm:px-6 sm:py-10">
      <div className="mx-auto max-w-[1500px]">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <Link href={`/admin`} className="text-sm text-cyan-200">← Testing dashboard</Link>
          <Link href={`/admin/qa`} className="text-sm text-slate-400">Search QA</Link>
        </div>
        <div className="mt-8">
          <p className="text-sm uppercase tracking-[0.25em] text-slate-500">PriceSift public-beta diagnostics</p>
          <h1 className="mt-2 text-4xl font-black">Books ISBN lab</h1>
          <p className="mt-3 max-w-4xl text-slate-400">
            Inspect the ISBN lookup path, rejections, and collectible separation behind the public Books beta.
          </p>
        </div>
        <AdminBookIsbnLab token={ADMIN_BROWSER_SESSION} />
        <SiteFooter />
      </div>
    </main>
  );
}
