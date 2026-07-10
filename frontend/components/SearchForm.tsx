"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export function SearchForm() {
  const [query, setQuery] = useState("RTX 3060 12GB");
  const router = useRouter();

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const cleaned = query.trim();
    if (!cleaned) return;
    router.push(`/search?q=${encodeURIComponent(cleaned)}`);
  }

  return (
    <form onSubmit={handleSubmit} className="mx-auto flex w-full max-w-2xl flex-col gap-3 sm:flex-row">
      <input
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder="Search for a used GPU..."
        className="min-h-14 flex-1 rounded-2xl border border-white/10 bg-white/10 px-5 text-base text-white outline-none placeholder:text-slate-400 focus:border-cyan-300"
      />
      <button className="min-h-14 rounded-2xl bg-cyan-300 px-7 font-semibold text-slate-950 transition hover:bg-cyan-200">
        Search
      </button>
    </form>
  );
}
