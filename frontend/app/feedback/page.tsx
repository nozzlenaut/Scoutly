import type { Metadata } from "next";
import Link from "next/link";
import { BetaFeedbackForm } from "@/components/BetaFeedbackForm";
import { SiteFooter } from "@/components/SiteFooter";

export const metadata: Metadata = {
  title: "Beta feedback | PriceSift",
  description: "Help test PriceSift and report bad results, missing products, confusing behavior, or feature ideas.",
};

export default function FeedbackPage() {
  return (
    <main className="pricesift-public min-h-screen px-6 py-10 text-ps-text-primary">
      <div className="mx-auto max-w-3xl">
        <Link href="/" className="text-sm text-ps-accent-hover hover:text-ps-text-primary hover:underline">← PriceSift</Link>
        <div className="mt-8">
          <p className="text-sm uppercase tracking-[0.25em] text-ps-success">Public beta</p>
          <h1 className="mt-2 text-4xl font-black">Help test PriceSift</h1>
          <p className="mt-4 text-ps-text-secondary leading-7">No signup is required. Search for products you already know, check whether the results are complete and working items, then tell us when something looks wrong or confusing.</p>
          <p className="mt-3 text-sm text-ps-neutral">For one specific marketplace listing, the “Report bad result” button on its result card is the fastest option.</p>
        </div>
        <div className="mt-8"><BetaFeedbackForm theme="light" /></div>
        <SiteFooter />
      </div>
    </main>
  );
}
