import type { Metadata } from "next";
import type { ReactNode } from "react";
import { AdminNavigation } from "@/components/AdminNavigation";
import "./admin-theme.css";

export const metadata: Metadata = {
  title: "PriceSift Admin",
  robots: {
    index: false,
    follow: false,
    noarchive: true,
    nocache: true,
  },
};

export default function AdminLayout({ children }: { children: ReactNode }) {
  return (
    <div className="pricesift-admin min-h-screen bg-ps-canvas text-ps-text-primary">
      <AdminNavigation />
      {children}
    </div>
  );
}
