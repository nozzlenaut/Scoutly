import type { Metadata } from "next";
import { PopularBookSeoPage, popularBookRevalidate } from "@/components/PopularBookSeoPage";
import { getPopularBook } from "@/lib/popularBooks";

const book = getPopularBook("project-hail-mary")!;
export const revalidate = popularBookRevalidate;
export const metadata: Metadata = {
  title: "Used Project Hail Mary: Prices & Exact Edition",
  description: book.description,
  alternates: { canonical: "/used/project-hail-mary" },
  robots: { index: true, follow: true },
};

export default function Page() {
  return <PopularBookSeoPage book={book} />;
}
