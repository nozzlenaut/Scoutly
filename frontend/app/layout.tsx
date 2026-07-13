import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Scoutly",
  description: "Cleaner eBay used-listing search for exact items.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
