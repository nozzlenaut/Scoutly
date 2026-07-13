import type { Metadata } from "next";
import "./globals.css";

const siteUrl = "https://www.pricesift.app";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "PriceSift",
    template: "%s | PriceSift",
  },
  description: "Find cleaner used listings and better prices for the exact item you already want.",
  applicationName: "PriceSift",
  openGraph: {
    type: "website",
    url: siteUrl,
    siteName: "PriceSift",
    title: "PriceSift",
    description: "Find cleaner used listings and better prices for the exact item you already want.",
  },
  twitter: {
    card: "summary",
    title: "PriceSift",
    description: "Find cleaner used listings and better prices for the exact item you already want.",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
