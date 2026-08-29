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
  {
    slug: "atomic-habits",
    title: "Atomic Habits",
    author: "James Clear",
    isbn: "9780735211292",
    editionLabel: "Avery hardcover",
    description:
      "Cleaner used listings for the standard U.S. hardcover edition of Atomic Habits, matched by exact ISBN instead of a title-only search.",
    buyingChecks: [
      "Confirm ISBN 9780735211292 if you want the Avery hardcover edition.",
      "Make sure the listing is the full physical book rather than a summary, workbook, ebook, or audiobook.",
      "Check for writing, highlighting, water damage, loose pages, or a badly worn binding.",
    ],
    commonTraps: ["summaries and workbooks", "audiobook or digital formats", "international or paperback editions"],
  },
  {
    slug: "the-let-them-theory",
    title: "The Let Them Theory",
    author: "Mel Robbins",
    isbn: "9781401971366",
    editionLabel: "Hay House hardcover",
    description:
      "Cleaner used listings for the Hay House hardcover edition of The Let Them Theory, tied to one physical ISBN so other formats do not get mixed in.",
    buyingChecks: [
      "Confirm ISBN 9781401971366 for this hardcover edition.",
      "Check that the listing is the complete physical book, not a summary, workbook, or audio edition.",
      "Look for disclosed highlighting, writing, water damage, or binding wear before comparing prices.",
    ],
    commonTraps: ["summaries and companion workbooks", "audiobooks and ebooks", "different bindings or editions"],
  },
  {
    slug: "sunrise-on-the-reaping",
    title: "Sunrise on the Reaping",
    author: "Suzanne Collins",
    isbn: "9781546171461",
    editionLabel: "Scholastic Press hardcover",
    description:
      "Cleaner used listings for the Scholastic Press hardcover edition of Sunrise on the Reaping, matched to the exact physical ISBN.",
    buyingChecks: [
      "Confirm ISBN 9781546171461 if this is the hardcover edition you want.",
      "Make sure the listing is this Hunger Games novel rather than another book in the series or a multi-book lot.",
      "Check the dust jacket, boards, binding, and pages for damage that affects the value of a newer hardcover.",
    ],
    commonTraps: ["other Hunger Games titles", "box sets and multi-book lots", "audiobook or digital formats"],
  },
  {
    slug: "the-women-kristin-hannah",
    title: "The Women",
    author: "Kristin Hannah",
    isbn: "9781250178633",
    editionLabel: "St. Martin's Press hardcover",
    description:
      "Cleaner used listings for the St. Martin's Press hardcover edition of The Women by Kristin Hannah, matched by exact ISBN.",
    buyingChecks: [
      "Confirm ISBN 9781250178633 for this U.S. hardcover edition.",
      "Check the author as well as the title, since several unrelated books are also called The Women.",
      "Look for a missing or damaged dust jacket, writing, water damage, loose pages, or other condition notes.",
    ],
    commonTraps: ["different books with the same title", "large-print or international editions", "audiobooks and non-physical formats"],
  },
];

export function getPopularBook(slug: string): PopularBook | undefined {
  return popularBooks.find((book) => book.slug === slug);
}
