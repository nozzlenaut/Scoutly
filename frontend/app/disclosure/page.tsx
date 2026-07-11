import Link from "next/link";

export default function DisclosurePage() {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-white">
      <section className="mx-auto max-w-3xl rounded-3xl border border-white/10 bg-white/[0.05] p-8 shadow-2xl shadow-black/20">
        <Link href="/" className="text-sm text-cyan-200 hover:text-cyan-100">← Back to Scoutly</Link>
        <p className="mt-8 text-sm uppercase tracking-[0.25em] text-slate-500">Affiliate disclosure</p>
        <h1 className="mt-3 text-4xl font-black">How Scoutly makes money</h1>
        <div className="mt-6 space-y-5 text-base leading-8 text-slate-300">
          <p>
            Some Scoutly result buttons are affiliate links. That means if you click one and buy something, Scoutly may earn a small commission at no extra cost to you.
          </p>
          <p>
            The goal is still simple: help you find the exact used item you already wanted. Affiliate links do not change the price you pay, and they should not change which item Scoutly thinks is the best match.
          </p>
          <p>
            Not into affiliate links? Totally fair. You can use Scoutly to find the item, then open eBay or the seller site separately — or use a private/incognito window — and buy it however you prefer.
          </p>
          <p>
            Scoutly is still early, so if a result looks wrong, sketchy, broken, or clearly not the item you searched for, treat it like a bad match and skip it.
          </p>
        </div>
      </section>
    </main>
  );
}
