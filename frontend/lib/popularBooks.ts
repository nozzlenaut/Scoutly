export type PopularBook = {
  slug: string;
  title: string;
  author: string;
  isbn: string;
  editionLabel: string;
  description: string;
  buyingChecks: string[];
  commonTraps: string[];
};

export const popularBooks: PopularBook[] = [
  {
    slug: "project-hail-mary",
    title: "Project Hail Mary",
    author: "Andy Weir",
    isbn: "9780593135228",
    editionLabel: "Ballantine paperback",
    description:
      "Cleaner used listings for a common U.S. paperback edition of Project Hail Mary, matched by exact ISBN instead of title alone.",
    buyingChecks: [
      "Confirm ISBN 9780593135228 if this is the edition you want.",
      "Check that the listing is a physical book rather than an audiobook, ebook code, summary, or study guide.",
      "Look for disclosed water damage, heavy highlighting, missing pages, or binding damage.",
    ],
    commonTraps: ["movie tie-in or deluxe editions", "audiobooks and summaries", "other paperback or hardcover ISBNs"],
  },
  {
    slug: "dungeon-crawler-carl",
    title: "Dungeon Crawler Carl",
    author: "Matt Dinniman",
    isbn: "9780593820254",
    editionLabel: "Ace paperback",
    description:
      "Cleaner used listings for the Ace paperback edition of Dungeon Crawler Carl, matched to its exact physical ISBN.",
    buyingChecks: [
      "Confirm ISBN 9780593820254 for the Ace paperback edition.",
      "Make sure the listing is book one rather than another Dungeon Crawler Carl volume or a multi-book lot.",
      "Check for binding damage, writing, missing pages, or other condition notes that materially affect a reading copy.",
    ],
    commonTraps: ["other books in the series", "multi-book bundles", "audiobook or non-physical formats"],
  },
  {
    slug: "harry-potter-sorcerers-stone",
    title: "Harry Potter and the Sorcerer's Stone",
    author: "J.K. Rowling",
    isbn: "9780590353427",
    editionLabel: "Scholastic paperback",
    description:
      "Cleaner used listings for the familiar Scholastic paperback edition of Harry Potter and the Sorcerer's Stone, matched by exact ISBN.",
    buyingChecks: [
      "Confirm ISBN 9780590353427 if you want this specific Scholastic paperback.",
      "Check that the listing is the first novel rather than a box set, illustrated edition, companion book, or different printing.",
      "Look for missing pages, detached covers, writing, water damage, or other meaningful condition issues.",
    ],
    commonTraps: ["box sets and bundles", "illustrated or special editions", "different Harry Potter titles or ISBNs"],
  },
];

export function getPopularBook(slug: string): PopularBook | undefined {
  return popularBooks.find((book) => book.slug === slug);
}
