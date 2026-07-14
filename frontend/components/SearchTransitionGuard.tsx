"use client";

import { useEffect, useState, type ReactNode } from "react";

export function SearchTransitionGuard({ children }: { children: ReactNode }) {
  const [isChangingSearch, setIsChangingSearch] = useState(false);

  useEffect(() => {
    const handleStart = () => setIsChangingSearch(true);
    window.addEventListener("pricesift:search-start", handleStart);
    return () => window.removeEventListener("pricesift:search-start", handleStart);
  }, []);

  if (isChangingSearch) {
    return (
      <div className="mt-8 rounded-3xl border border-cyan-300/20 bg-cyan-300/10 p-6 text-cyan-50" role="status">
        <div className="flex items-center gap-3 font-semibold">
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-cyan-100/30 border-t-cyan-100" />
          Loading fresh results…
        </div>
        <p className="mt-2 text-sm text-cyan-50/80">Previous-category results have been cleared.</p>
      </div>
    );
  }

  return <>{children}</>;
}
