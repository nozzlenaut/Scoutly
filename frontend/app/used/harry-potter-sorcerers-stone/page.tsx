import type { Metadata } from "next";
import { PopularBookSeoPage } from "@/components/PopularBookSeoPage";
import { getPopularBook } from "@/lib/popularBooks";

const book = getPopularBook("harry-potter-sorcerers-stone")!;
export const revalidate = 1800;
export const metadata: Metadata = {
  title: "Used Harry Potter and the Sorcerer's Stone: Prices & Exact Edition",
  description: book.description,
  alternates: { canonical: "/used/harry-potter-sorcerers-stone" },
  robots: { index: true, follow: true },
};

export default function Page() {
  return <PopularBookSeoPage book={book} />;
}
