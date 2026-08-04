import { Analytics } from "@vercel/analytics/next";
import { VerifiedOutboundClickTracker } from "@/components/VerifiedOutboundClickTracker";
import type { Metadata } from "next";
import "./globals.css";

const siteUrl = "https://www.pricesift.app";
const siteDescription =
  "Make buying secondhand easier with cleaner listings for exact used products—and resources to keep them in use.";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "PriceSift",
    template: "%s | PriceSift",
  },
  description: siteDescription,
  applicationName: "PriceSift",
  openGraph: {
    type: "website",
    url: siteUrl,
    siteName: "PriceSift",
    title: "PriceSift",
    description: siteDescription,
  },
  twitter: {
    card: "summary",
    title: "PriceSift",
    description: siteDescription,
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        {children}
        <VerifiedOutboundClickTracker />
        <Analytics />
      </body>
    </html>
  );
}
