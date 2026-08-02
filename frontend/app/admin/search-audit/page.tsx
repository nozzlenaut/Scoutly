import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";
import { SearchAuditTool } from "@/components/SearchAuditTool";
import { getAdminToken } from "@/lib/adminSession";

export const metadata: Metadata = {
  title: "Search Audit | PriceSift Admin",
  robots: { index: false, follow: false },
};

export default async function SearchAuditPage() {
  const token = await getAdminToken();
  if (!token) redirect("/admin");

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,_#164e63,_#020617_42%)] px-4 py-8 text-white sm:px-6">
      <div className="mx-auto max-w-[1500px]">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <Link href="/admin" className="text-sm font-semibold text-cyan-200 hover:text-cyan-100">← PriceSift admin</Link>
            <p className="mt-7 text-sm font-bold uppercase tracking-[0.25em] text-cyan-300">PriceSift research media</p>
            <h1 className="mt-2 text-4xl font-black sm:text-5xl">Search Audit</h1>
            <p className="mt-3 max-w-3xl text-slate-300">
              Review a consistent sample of marketplace results, count the search-quality problems, and generate a pain-point post plus a PriceSift video reply.
            </p>
          </div>
          <div className="rounded-2xl border border-emerald-200/20 bg-emerald-200/10 px-4 py-3 text-sm text-emerald-100">
            No scraping · no AI judgment · saved in this browser
          </div>
        </div>

        <div className="mt-8">
          <SearchAuditTool />
        </div>
      </div>
    </main>
  );
}
