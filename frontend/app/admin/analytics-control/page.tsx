import Link from "next/link";
import { AdminLoginForm } from "@/components/AdminLoginForm";
import { AdminAnalyticsOptOut } from "@/components/AdminAnalyticsOptOut";
import { getAdminToken } from "@/lib/adminSession";

function Gate({ invalid = false }: { invalid?: boolean }) {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-white">
      <div className="mx-auto max-w-xl">
        <Link href="/" className="text-sm text-cyan-200">← PriceSift</Link>
        <section className="mt-10 rounded-3xl border border-white/10 bg-white/[0.05] p-6">
          <p className="text-sm uppercase tracking-[0.25em] text-slate-500">PriceSift admin</p>
          <h1 className="mt-2 text-3xl font-black">Admin token required</h1>
          <p className="mt-3 text-sm text-slate-400">
            {invalid ? "That token was not accepted." : "Use the same private token as the other admin pages."}
          </p>
          <AdminLoginForm next="/admin/analytics-control" />
        </section>
      </div>
    </main>
  );
}

export default async function AnalyticsControlPage({
  searchParams,
}: {
  searchParams: Promise<{ invalid?: string }>;
}) {
  const params = await searchParams;
  const token = await getAdminToken();
  if (!token) return <Gate invalid={params.invalid === "1"} />;

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-8 text-white sm:px-6 sm:py-10">
      <div className="mx-auto max-w-3xl">
        <Link href="/admin" className="text-sm text-cyan-200">← Testing dashboard</Link>
        <div className="mt-8">
          <p className="text-sm uppercase tracking-[0.25em] text-slate-500">PriceSift admin</p>
          <h1 className="mt-2 text-4xl font-black">Analytics controls</h1>
          <p className="mt-3 max-w-2xl text-slate-400">
            Use this browser-level switch when you are making screenshots, demos, audits, or social posts and do not want your own activity added to PriceSift statistics.
          </p>
        </div>
        <div className="mt-8">
          <AdminAnalyticsOptOut />
        </div>
        <p className="mt-5 text-sm leading-6 text-slate-500">
          The setting applies only to this browser. It does not change public behavior for anyone else and it does not travel with shared search links.
        </p>
      </div>
    </main>
  );
}
