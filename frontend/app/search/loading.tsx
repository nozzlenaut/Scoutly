export default function SearchLoading() {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-white">
      <div className="mx-auto flex min-h-[70vh] max-w-4xl flex-col items-center justify-center text-center">
        <div className="mb-6 h-12 w-12 animate-spin rounded-full border-4 border-cyan-100/20 border-t-cyan-200" />
        <p className="text-sm uppercase tracking-[0.25em] text-slate-500">Searching PriceSift</p>
        <h1 className="mt-3 text-3xl font-black">Finding complete used listings…</h1>
        <p className="mt-3 max-w-xl text-sm leading-6 text-slate-400">
          Checking active Buy It Now results first. Auctions will load after the main results.
        </p>
      </div>
    </main>
  );
}
