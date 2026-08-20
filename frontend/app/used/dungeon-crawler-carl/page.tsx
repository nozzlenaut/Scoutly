import type { Metadata } from "next";
import { PopularBookSeoPage, popularBookRevalidate } from "@/components/PopularBookSeoPage";
import { getPopularBook } from "@/lib/popularBooks";

const book = getPopularBook("dungeon-crawler-carl")!;
export const revalidate = popularBookRevalidate;
export const metadata: Metadata = {
  title: "Used Dungeon Crawler Carl: Prices & Exact Edition",
  description: book.description,
  alternates: { canonical: "/used/dungeon-crawler-carl" },
  robots: { index: true, follow: true },
};

export default function Page() {
  return <PopularBookSeoPage book={book} />;
}
