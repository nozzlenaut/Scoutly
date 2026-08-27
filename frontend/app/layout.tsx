import { Analytics } from "@vercel/analytics/next";
import { VerifiedOutboundClickTracker } from "@/components/VerifiedOutboundClickTracker";
import type { Metadata } from "next";
import "./globals.css";

const siteUrl = "https://www.pricesift.app";
const siteDescription =
  "Make buying secondhand easier with cleaner listings for exact used products—and resources to keep them in use.";

const impactVerificationMeta = {
  name: "impact-site-verification",
  value: "7b9311d5-53f8-42a8-80ed-a5448aa404c8",
} as React.MetaHTMLAttributes<HTMLMetaElement> & { value: string };

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
      <head>
        <meta {...impactVerificationMeta} />
      </head>
      <body>
        {children}
        <VerifiedOutboundClickTracker />
        <Analytics />
      </body>
    </html>
  );
}
