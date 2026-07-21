import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Affiliate disclosure",
  description: "How PriceSift uses affiliate links and keeps result matching independent from paid placement.",
  alternates: { canonical: "/disclosure" },
};

export default function DisclosurePage() {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-white">
      <section className="mx-auto max-w-3xl rounded-3xl border border-white/10 bg-white/[0.05] p-8 shadow-2xl shadow-black/20">
        <Link href="/" className="text-sm text-cyan-200 hover:text-cyan-100">← Back to PriceSift</Link>
        <p className="mt-8 text-sm uppercase tracking-[0.25em] text-slate-500">Affiliate disclosure</p>
        <h1 className="mt-3 text-4xl font-black">How PriceSift makes money</h1>
        <div className="mt-6 space-y-5 text-base leading-8 text-slate-300">
          <p className="rounded-2xl border border-orange-200/20 bg-orange-200/[0.06] p-4 font-semibold text-orange-50">
            As an Amazon Associate I earn from qualifying purchases.
          </p>
          <p>
            Some PriceSift result buttons are affiliate links. That means if you click one and buy something, PriceSift may earn a small commission at no extra cost to you.
          </p>
          <p>
            Amazon links are shown separately from PriceSift’s ranked eBay and KEH results. Until Amazon API access is available, PriceSift does not display or claim a current Amazon price, condition, seller, or availability. Used and renewed searches are shortcuts only; always verify the exact item and condition on Amazon.
          </p>
          <p>
            The goal is still simple: help you find the exact used item you already wanted. Affiliate links do not change the price you pay, and they should not change which item PriceSift thinks is the best match.
          </p>
          <p>
            Not into affiliate links? Totally fair. You can use PriceSift to find the item, then open eBay, Amazon, or the seller site separately — or use a private/incognito window — and buy it however you prefer.
          </p>
          <p>
            PriceSift is still early, so if a result looks wrong, sketchy, broken, or clearly not the item you searched for, treat it like a bad match and skip it.
          </p>
        </div>
      </section>
    </main>
  );
}
