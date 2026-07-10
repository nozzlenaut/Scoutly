import { CategoryStatusPanel } from "@/components/CategoryStatusPanel";
import { CategoryTabs } from "@/components/CategoryTabs";
import { SearchForm } from "@/components/SearchForm";
import { getActiveCategoryStatus } from "@/lib/categoryStatus";

export default function HomePage() {
  const activeCategory = getActiveCategoryStatus();

  return (
    <main className="min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top,_#164e63,_#050816_45%)] px-6 py-10">
      <section className="mx-auto flex min-h-[80vh] max-w-5xl flex-col items-center justify-center text-center">
        <div className="mb-5 rounded-full border border-emerald-300/30 bg-emerald-300/10 px-4 py-2 text-sm font-medium text-emerald-100">
          {activeCategory.tag}
        </div>
        <h1 className="text-5xl font-black tracking-tight text-white sm:text-7xl">Scoutly</h1>
        <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300">
          Search once. Scoutly compares used listings and surfaces the best option from each marketplace.
        </p>

        <div className="mt-8 w-full">
          <CategoryTabs />
        </div>

        <div className="mt-8 w-full">
          <SearchForm />
        </div>

        <div className="mt-10 grid w-full gap-4 text-left sm:grid-cols-3">
          {["One best result per store", "Built for used prices", "Affiliate-ready links"].map((item) => (
            <div key={item} className="rounded-2xl border border-white/10 bg-white/[0.06] p-4 text-sm text-slate-300">
              {item}
            </div>
          ))}
        </div>

        <div className="mt-6 w-full">
          <CategoryStatusPanel />
        </div>
      </section>
    </main>
  );
}
