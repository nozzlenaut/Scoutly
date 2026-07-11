import { CategoryStatusPanel } from "@/components/CategoryStatusPanel";
import { SearchForm } from "@/components/SearchForm";

export default function HomePage() {
  return (
    <main className="min-h-screen overflow-x-hidden bg-[radial-gradient(circle_at_top,_#164e63,_#050816_45%)] px-6 py-10">
      <section className="mx-auto flex min-h-[80vh] max-w-5xl flex-col items-center justify-center text-center">
        <div className="mb-5 rounded-full border border-emerald-300/30 bg-emerald-300/10 px-4 py-2 text-sm font-medium text-emerald-100">
          Category-filtered search added
        </div>
        <h1 className="text-5xl font-black tracking-tight text-white sm:text-7xl">Scoutly</h1>
        <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300">
          Pick an active category, choose the exact item, and Scoutly surfaces the best used listing from each marketplace.
        </p>

        <div className="relative z-50 mt-8 w-full">
          <SearchForm />
        </div>

        <div className="relative z-0 mt-10 grid w-full gap-4 text-left sm:grid-cols-3">
          {["Exact-item autocomplete", "Built for used prices", "One best result per store"].map((item) => (
            <div key={item} className="rounded-2xl border border-white/10 bg-white/[0.06] p-4 text-sm text-slate-300">
              {item}
            </div>
          ))}
        </div>

        <div className="relative z-0 mt-6 w-full">
          <CategoryStatusPanel />
        </div>
      </section>
    </main>
  );
}
