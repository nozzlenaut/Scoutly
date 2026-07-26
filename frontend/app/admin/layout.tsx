import type { ReactNode } from "react";
import { AdminNavigation } from "@/components/AdminNavigation";

export default function AdminLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <AdminNavigation />
      {children}
    </div>
  );
}
