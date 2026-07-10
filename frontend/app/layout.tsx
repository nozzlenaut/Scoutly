import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Scoutly",
  description: "Find the best used deals across online marketplaces.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
