import { SearchForm } from "@/components/SearchForm";

export default function HomePage() {
  return (
    <main className="min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top,_#164e63,_#050816_45%)] px-6 py-10">
      <section className="mx-auto flex min-h-[80vh] max-w-5xl flex-col items-center justify-center text-center">
        <div className="mb-5 rounded-full border border-cyan-300/30 bg-cyan-300/10 px-4 py-2 text-sm text-cyan-100">
          Used deal search, starting with GPUs
        </div>
        <h1 className="text-5xl font-black tracking-tight text-white sm:text-7xl">Scoutly</h1>
        <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300">
          Search once. Scoutly compares used listings and surfaces the best option from each marketplace.
        </p>
        <div className="mt-10 w-full">
          <SearchForm />
        </div>
        <div className="mt-10 grid gap-4 text-left sm:grid-cols-3">
          {["One best result per store", "Built for used prices", "Affiliate-ready links"].map((item) => (
            <div key={item} className="rounded-2xl border border-white/10 bg-white/[0.06] p-4 text-sm text-slate-300">
              {item}
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
