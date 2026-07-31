import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter } from "@/components/SiteFooter";
import { indexedProducts } from "@/lib/indexedProducts";

export const metadata: Metadata = {
  title: "Used product price guides",
  description: "Cleaner current used listings and buying guidance for exact cameras, consoles, graphics cards, and LEGO sets.",
  alternates: { canonical: "/used" },
  robots: { index: true, follow: true },
};

export default function UsedProductGuidesPage() {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-white">
      <div className="mx-auto max-w-6xl">
        <Link href="/" className="text-sm text-cyan-200 hover:text-cyan-100">← PriceSift</Link>
        <section className="mt-8 rounded-[2rem] border border-white/10 bg-white/[0.04] p-7 sm:p-10">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200">Curated exact products</p>
          <h1 className="mt-3 text-4xl font-black tracking-tight sm:text-5xl">Used product price guides</h1>
          <p className="mt-5 max-w-3xl text-lg leading-8 text-slate-300">
            Each page uses PriceSift’s normal exact-item matching and listing filters. These are manually approved products—not thousands of thin pages generated from random searches.
          </p>
          <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {indexedProducts.map((product) => (
              <Link
                key={product.slug}
                href={`/used/${product.slug}`}
                className="rounded-2xl border border-white/10 bg-slate-950/50 p-5 transition hover:border-cyan-300/30 hover:bg-slate-900"
              >
                <p className="text-xs uppercase tracking-[0.18em] text-slate-400">{product.category}</p>
                <h2 className="mt-2 text-xl font-bold">{product.title}</h2>
                <p className="mt-3 text-sm leading-6 text-slate-400">{product.description}</p>
              </Link>
            ))}
          </div>
          <div className="mt-8 rounded-2xl border border-emerald-300/20 bg-emerald-300/[0.07] p-5">
            <h2 className="text-xl font-bold">Why used?</h2>
            <p className="mt-2 text-sm leading-6 text-slate-300">Keeping a solid product in use longer can be cheaper and avoid an unnecessary new purchase.</p>
            <Link href="/reuse" className="mt-3 inline-flex text-sm font-semibold text-emerald-200 hover:text-emerald-100">Read PriceSift’s reuse mission →</Link>
          </div>
        </section>
        <SiteFooter />
      </div>
    </main>
  );
}
