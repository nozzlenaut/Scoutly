import type { ReactNode } from "react";
import { AdminNavigation } from "@/components/AdminNavigation";

export default function AdminLayout({ children }: { children: ReactNode }) {
  return (
    <div className="pricesift-admin min-h-screen bg-ps-canvas text-ps-text-primary">
      <AdminNavigation />
      {children}
    </div>
  );
}
