
"use client";

import { track } from "@vercel/analytics";
import { type ChangeEvent, useMemo, useRef, useState } from "react";
import {
  exactListingOutboundUrl,
  goodreadsAmazonFallback,
  otherEditionsOutboundUrl,
  searchGoodreadsIsbn,
} from "@/lib/goodreadsApi";
import type { BookLabResponse } from "@/lib/api";

type SearchState = "ready" | "queued" | "searching" | "found" | "miss" | "error";

type ImportedBook = {
  id: string;
  title: string;
  author: string;
  shelf: string;
  binding: string;
  publisher: string;
  year: string;
  isbn10: string;
  isbn13: string;
  isbn: string;
  importStatus: "ready" | "digital" | "missing" | "invalid";
  searchState: SearchState;
  response?: BookLabResponse;
  error?: string;
  batchId?: string;
};

const DIGITAL_WORDS = [
  "kindle",
  "ebook",
  "e-book",
  "audiobook",
  "audio cd",
  "audible",
];

function parseCsv(text: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [];
  let field = "";
  let quoted = false;

  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];

    if (quoted) {
      if (char === '"') {
        if (text[index + 1] === '"') {
          field += '"';
          index += 1;
        } else {
          quoted = false;
        }
      } else {
        field += char;
      }
      continue;
    }

    if (char === '"') {
      quoted = true;
    } else if (char === ",") {
      row.push(field);
      field = "";
    } else if (char === "\n") {
      row.push(field.replace(/\r$/, ""));
      rows.push(row);
      row = [];
      field = "";
    } else {
      field += char;
    }
  }

  if (field.length || row.length) {
    row.push(field.replace(/\r$/, ""));
    rows.push(row);
  }

  return rows.filter((candidate) =>
    candidate.some((value) => value.trim().length > 0),
  );
}

function cleanIsbn(value: string): string {
  const unwrapped = value.trim().replace(/^=\s*"([^"]*)"$/, "$1");
  return unwrapped.replace(/[^0-9Xx]/g, "").toUpperCase();
}

function validIsbn10(value: string): boolean {
  if (!/^\d{9}[\dX]$/.test(value)) return false;
  const total = value.split("").reduce((sum, char, index) => {
    const digit = char === "X" ? 10 : Number(char);
    return sum + (10 - index) * digit;
  }, 0);
  return total % 11 === 0;
}

function validIsbn13(value: string): boolean {
  if (!/^\d{13}$/.test(value)) return false;
  const total = value
    .slice(0, 12)
    .split("")
    .reduce(
      (sum, char, index) =>
        sum + Number(char) * (index % 2 === 0 ? 1 : 3),
      0,
    );
  return (10 - (total % 10)) % 10 === Number(value[12]);
}

function normalizeShelfLabel(value: string): string {
  if (value === "to-read") return "Want to Read";
  if (value === "currently-reading") return "Currently Reading";
  if (value === "read") return "Read";
  return value
    .split("-")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function importRows(text: string): ImportedBook[] {
  const rows = parseCsv(text);
  if (rows.length < 2) {
    throw new Error("The CSV did not contain any Goodreads book rows.");
  }

  const headers = rows[0].map((header) =>
    header.replace(/^\uFEFF/, "").trim(),
  );
  const required = [
    "Title",
    "Author",
    "Exclusive Shelf",
    "ISBN",
    "ISBN13",
    "Binding",
  ];
  const missingHeaders = required.filter(
    (header) => !headers.includes(header),
  );
  if (missingHeaders.length) {
    throw new Error(
      `This does not look like a Goodreads library export. Missing: ${missingHeaders.join(", ")}`,
    );
  }

  return rows.slice(1).map((values, index) => {
    const record = Object.fromEntries(
      headers.map((header, position) => [header, values[position] || ""]),
    );
    const isbn10 = cleanIsbn(record.ISBN || "");
    const isbn13 = cleanIsbn(record.ISBN13 || "");
    const valid13 = validIsbn13(isbn13) ? isbn13 : "";
    const valid10 = validIsbn10(isbn10) ? isbn10 : "";
    const isbn = valid13 || valid10;
    const binding = (record.Binding || "").trim();
    const digital = DIGITAL_WORDS.some((word) =>
      binding.toLowerCase().includes(word),
    );

    let importStatus: ImportedBook["importStatus"];
    if (digital) {
      importStatus = "digital";
    } else if (isbn) {
      importStatus = "ready";
    } else if (isbn10 || isbn13) {
      importStatus = "invalid";
    } else {
      importStatus = "missing";
    }

    return {
      id: `${index}-${isbn || record["Book Id"] || record.Title}`,
      title: (record.Title || "Untitled book").trim(),
      author: (record.Author || "").trim(),
      shelf: (record["Exclusive Shelf"] || "unknown").trim(),
      binding,
      publisher: (record.Publisher || "").trim(),
      year: (record["Year Published"] || "").replace(/\.0$/, "").trim(),
      isbn10: valid10,
      isbn13: valid13,
      isbn,
      importStatus,
      searchState: "ready",
    };
  });
}

function csvCell(value: string | number): string {
  const text = String(value ?? "");
  return /[",\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

function downloadResults(books: ImportedBook[]): void {
  const headers = [
    "Title",
    "Author",
    "Shelf",
    "Binding",
    "ISBN",
    "Status",
    "Match Method",
    "Best Total",
    "Condition",
    "Clean Options",
    "Candidates",
    "Listing",
    "Separated Exact Listing",
    "Amazon Fallback",
  ];
  const rows = books.map((book) => {
    const top = book.response?.top_results?.[0];
    const separatedExact =
      book.response?.collectible_results?.[0] ||
      book.response?.bundle_results?.[0];
    const hasSeparatedExact = Boolean(separatedExact);
    const showAmazonFallback =
      book.importStatus === "digital" || book.searchState === "miss";
    const amazonFallback = goodreadsAmazonFallback(
      {
        title: book.title,
        author: book.author,
        binding: book.binding,
        isbn10: book.isbn10,
        isbn13: book.isbn13,
      },
      book.batchId || "export",
      book.id,
    );
    const status =
      book.searchState === "found"
        ? "Exact edition found"
        : book.searchState === "miss"
          ? hasSeparatedExact
            ? "No standard used copy; separated exact alternative available"
            : "No standard used copy for exact edition"
          : book.searchState === "error"
            ? "Search error"
            : book.importStatus === "digital"
              ? "Digital/audio Amazon fallback available"
              : book.importStatus === "missing"
                ? "ISBN missing"
                : book.importStatus === "invalid"
                  ? "Invalid ISBN"
                  : "Not searched";

    return [
      book.title,
      book.author,
      book.shelf,
      book.binding,
      book.isbn,
      status,
      book.response?.selected_match_method || "",
      top?.total_price?.toFixed(2) || "",
      top?.condition || "",
      book.response?.top_results?.length || 0,
      book.response?.candidate_count || 0,
      top?.url || "",
      separatedExact?.url || "",
      showAmazonFallback ? amazonFallback.url : "",
    ];
  });

  const content = [headers, ...rows]
    .map((row) => row.map(csvCell).join(","))
    .join("\n");
  const blob = new Blob([content], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "pricesift-goodreads-results.csv";
  anchor.click();
  URL.revokeObjectURL(url);
}

export function GoodreadsImportTool() {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [books, setBooks] = useState<ImportedBook[]>([]);
  const [selectedShelf, setSelectedShelf] = useState("to-read");
  const [fileName, setFileName] = useState("");
  const [parseError, setParseError] = useState("");
  const [running, setRunning] = useState(false);
  const [completed, setCompleted] = useState(0);

  const shelves = useMemo(
    () =>
      Array.from(
        new Set(books.map((book) => book.shelf).filter(Boolean)),
      ).sort(),
    [books],
  );

  const visibleBooks = useMemo(
    () =>
      selectedShelf === "all"
        ? books
        : books.filter((book) => book.shelf === selectedShelf),
    [books, selectedShelf],
  );

  const counts = useMemo(() => {
    const ready = visibleBooks.filter(
      (book) => book.importStatus === "ready",
    ).length;
    const digital = visibleBooks.filter(
      (book) => book.importStatus === "digital",
    ).length;
    const missing = visibleBooks.filter(
      (book) =>
        book.importStatus === "missing" ||
        book.importStatus === "invalid",
    ).length;
    const found = visibleBooks.filter(
      (book) => book.searchState === "found",
    ).length;
    const misses = visibleBooks.filter(
      (book) => book.searchState === "miss",
    ).length;
    const errors = visibleBooks.filter(
      (book) => book.searchState === "error",
    ).length;

    return {
      total: visibleBooks.length,
      ready,
      digital,
      missing,
      found,
      misses,
      errors,
    };
  }, [visibleBooks]);

  const searchedBooks = visibleBooks.filter((book) =>
    ["found", "miss", "error"].includes(book.searchState),
  );
  const bestTotal = searchedBooks.reduce((sum, book) => {
    return sum + (book.response?.top_results?.[0]?.total_price || 0);
  }, 0);

  async function loadFile(file: File): Promise<void> {
    setParseError("");
    setRunning(false);
    setCompleted(0);

    try {
      const text = await file.text();
      const imported = importRows(text);
      const importedShelves = new Set(imported.map((book) => book.shelf));
      setBooks(imported);
      setFileName(file.name);
      setSelectedShelf(importedShelves.has("to-read") ? "to-read" : "all");
      track("goodreads_csv_loaded", {
        rows: imported.length,
        has_to_read: importedShelves.has("to-read"),
      });
    } catch (error) {
      setBooks([]);
      setFileName("");
      setParseError(
        error instanceof Error ? error.message : "Could not read that CSV.",
      );
    }
  }

  function updateBook(
    id: string,
    update: Partial<ImportedBook>,
  ): void {
    setBooks((current) =>
      current.map((book) =>
        book.id === id ? { ...book, ...update } : book,
      ),
    );
  }

  async function searchAll(): Promise<void> {
    const targetBooks = visibleBooks.filter(
      (book) => book.importStatus === "ready",
    );
    if (!targetBooks.length || running) return;

    const batchId = crypto.randomUUID();
    const metadata = {
      batchId,
      shelf: selectedShelf,
      importedCount: visibleBooks.length,
      searchableCount: counts.ready,
      digitalCount: counts.digital,
      missingIsbnCount: counts.missing,
    };

    setRunning(true);
    setCompleted(0);
    setBooks((current) =>
      current.map((book) =>
        targetBooks.some((target) => target.id === book.id)
          ? {
              ...book,
              searchState: "queued",
              response: undefined,
              error: undefined,
              batchId,
            }
          : book,
      ),
    );

    track("goodreads_batch_started", {
      shelf: selectedShelf,
      searchable: counts.ready,
      imported: visibleBooks.length,
    });

    let cursor = 0;
    let foundCount = 0;
    let missCount = 0;
    let errorCount = 0;

    async function worker(): Promise<void> {
      while (cursor < targetBooks.length) {
        const position = cursor;
        cursor += 1;
        const book = targetBooks[position];
        updateBook(book.id, { searchState: "searching", batchId });

        try {
          const response = await searchGoodreadsIsbn(book.isbn, metadata, {
            title: book.title,
            author: book.author,
          });
          const found = response.top_results.length > 0;
          if (found) foundCount += 1;
          else missCount += 1;
          updateBook(book.id, {
            searchState: found ? "found" : "miss",
            response,
            error: undefined,
            batchId,
          });
        } catch (error) {
          errorCount += 1;
          updateBook(book.id, {
            searchState: "error",
            error:
              error instanceof Error
                ? error.message
                : "The exact-edition search failed.",
            batchId,
          });
        } finally {
          setCompleted((value) => value + 1);
        }
      }
    }

    await Promise.all([worker(), worker()]);
    setRunning(false);

    track("goodreads_batch_completed", {
      shelf: selectedShelf,
      searched: targetBooks.length,
      found: foundCount,
      misses: missCount,
      errors: errorCount,
    });
  }

  return (
    <div className="mt-8 space-y-6">
      <section className="rounded-[2rem] border border-cyan-200/20 bg-cyan-200/[0.07] p-6 sm:p-8">
        <p className="text-sm font-bold uppercase tracking-[0.22em] text-cyan-200">
          Goodreads Import · Beta
        </p>
        <h1 className="mt-3 text-4xl font-black text-white sm:text-5xl">
          Price an entire reading list.
        </h1>
        <p className="mt-4 max-w-3xl text-base leading-7 text-slate-300">
          Export your Goodreads library, upload the CSV, and PriceSift will
          search the exact physical ISBN saved for each book. Digital and
          audio rows receive an unranked Amazon fallback. Your file stays
          in this browser and is not uploaded or retained.
        </p>

        <div className="mt-6 rounded-3xl border border-emerald-200/25 bg-emerald-200/10 p-5 text-emerald-50">
          <p className="font-black">Exact editions only.</p>
          <p className="mt-2 text-sm leading-6 text-emerald-100/90">
            PriceSift searches the ISBN contained in your Goodreads export.
            It will never silently replace it with another edition. A broader
            edition search is offered only after an exact-edition miss, and
            only when you click it.
          </p>
        </div>
      </section>

      <section className="rounded-[2rem] border border-white/10 bg-white/[0.05] p-6 sm:p-8">
        <div className="grid gap-6 lg:grid-cols-[1fr_auto] lg:items-end">
          <div>
            <h2 className="text-2xl font-black text-white">
              1. Export your Goodreads library
            </h2>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-300">
              Goodreads currently exposes its CSV export through the website.
              The mobile app may not show the export option, so open the page
              in a desktop browser when necessary.
            </p>
          </div>
          <a
            href="https://www.goodreads.com/review/import"
            target="_blank"
            rel="noreferrer"
            onClick={() => track("goodreads_export_link_clicked")}
            className="rounded-2xl border border-white/15 bg-white px-5 py-3 text-center font-bold text-slate-950 transition hover:bg-slate-200"
          >
            Click here to export from Goodreads ↗
          </a>
        </div>
      </section>

      <section className="rounded-[2rem] border border-white/10 bg-white/[0.05] p-6 sm:p-8">
        <h2 className="text-2xl font-black text-white">
          2. Upload the exported CSV
        </h2>
        <p className="mt-3 text-sm leading-6 text-slate-400">
          Choose the file named <code>goodreads_library_export.csv</code>.
          Ratings, reviews, notes, and account details are ignored.
        </p>

        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,text/csv"
          className="hidden"
          onChange={(event: ChangeEvent<HTMLInputElement>) => {
            const file = event.target.files?.[0];
            if (file) void loadFile(file);
          }}
        />

        <div className="mt-5 flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="rounded-2xl bg-cyan-200 px-5 py-3 font-bold text-slate-950 transition hover:bg-cyan-100"
          >
            Choose Goodreads CSV
          </button>
          {fileName ? (
            <span className="text-sm text-slate-300">{fileName}</span>
          ) : null}
        </div>

        {parseError ? (
          <div className="mt-5 rounded-2xl border border-rose-300/20 bg-rose-300/10 p-4 text-sm text-rose-100">
            {parseError}
          </div>
        ) : null}
      </section>

      {books.length ? (
        <>
          <section className="rounded-[2rem] border border-white/10 bg-white/[0.05] p-6 sm:p-8">
            <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <h2 className="text-2xl font-black text-white">
                  3. Choose a shelf and search
                </h2>
                <p className="mt-3 text-sm leading-6 text-slate-400">
                  Searches run two at a time. Large shelves may take a few
                  minutes, but you can leave the page open and let it work.
                </p>
              </div>

              <label className="block text-sm font-semibold text-slate-200">
                Goodreads shelf
                <select
                  value={selectedShelf}
                  disabled={running}
                  onChange={(event: ChangeEvent<HTMLSelectElement>) => {
                    setSelectedShelf(event.target.value);
                    setCompleted(0);
                  }}
                  className="mt-2 block min-w-56 rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-white"
                >
                  <option value="all">All shelves</option>
                  {shelves.map((shelf) => (
                    <option key={shelf} value={shelf}>
                      {normalizeShelfLabel(shelf)}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <div className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
              {[
                ["Books on shelf", counts.total],
                ["Exact ISBNs ready", counts.ready],
                ["Digital/audio fallbacks", counts.digital],
                ["Need an ISBN", counts.missing],
                ["Exact editions found", counts.found],
              ].map(([label, value]) => (
                <div
                  key={String(label)}
                  className="rounded-2xl border border-white/10 bg-slate-950/40 p-4"
                >
                  <p className="text-xs uppercase tracking-[0.16em] text-slate-500">
                    {label}
                  </p>
                  <p className="mt-2 text-2xl font-black text-white">
                    {value}
                  </p>
                </div>
              ))}
            </div>

            <div className="mt-6 flex flex-wrap items-center gap-3">
              <button
                type="button"
                disabled={running || counts.ready === 0}
                onClick={() => void searchAll()}
                className="rounded-2xl bg-emerald-200 px-5 py-3 font-bold text-slate-950 transition hover:bg-emerald-100 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {running
                  ? `Searching ${completed} of ${counts.ready}…`
                  : `Search ${counts.ready} exact editions`}
              </button>

              {searchedBooks.length ? (
                <button
                  type="button"
                  onClick={() => downloadResults(visibleBooks)}
                  className="rounded-2xl border border-white/15 px-5 py-3 font-bold text-white transition hover:bg-white/[0.08]"
                >
                  Download results CSV
                </button>
              ) : null}

              {searchedBooks.length ? (
                <p className="text-sm text-slate-400">
                  {counts.found} found · {counts.misses} exact-edition misses
                  {counts.errors ? ` · ${counts.errors} errors` : ""}
                  {bestTotal > 0
                    ? ` · Best-price total $${bestTotal.toFixed(2)}`
                    : ""}
                </p>
              ) : null}
            </div>

            {running ? (
              <div className="mt-5 h-3 overflow-hidden rounded-full bg-white/10">
                <div
                  className="h-full rounded-full bg-cyan-200 transition-all"
                  style={{
                    width: `${Math.min(
                      100,
                      (completed / Math.max(1, counts.ready)) * 100,
                    )}%`,
                  }}
                />
              </div>
            ) : null}
          </section>

          <section className="overflow-hidden rounded-[2rem] border border-white/10 bg-white/[0.04]">
            <div className="border-b border-white/10 p-5 sm:p-6">
              <h2 className="text-2xl font-black text-white">
                Exact-edition results
              </h2>
              <p className="mt-2 text-sm leading-6 text-slate-400">
                Candidate counts are available for transparency, but the
                primary answer is the cheapest clean exact-edition copy.
              </p>
            </div>

            <div className="divide-y divide-white/10">
              {visibleBooks.map((book) => {
                const top = book.response?.top_results?.[0];
                const cleanCount = book.response?.top_results?.length || 0;
                const batchId = book.batchId || "unsearched";
                const exactUrl = top
                  ? exactListingOutboundUrl(top, batchId, book.isbn)
                  : "";
                const otherUrl = otherEditionsOutboundUrl(
                  book.title,
                  book.author,
                  batchId,
                );
                const separatedExact =
                  book.response?.collectible_results?.[0] ||
                  book.response?.bundle_results?.[0];
                const separatedKind = book.response?.collectible_results
                  ?.length
                  ? "collectible"
                  : "bundle";
                const separatedUrl = separatedExact
                  ? exactListingOutboundUrl(
                      separatedExact,
                      batchId,
                      book.isbn || book.isbn10 || book.isbn13,
                    )
                  : "";
                const amazonFallback = goodreadsAmazonFallback(
                  {
                    title: book.title,
                    author: book.author,
                    binding: book.binding,
                    isbn10: book.isbn10,
                    isbn13: book.isbn13,
                  },
                  batchId,
                  book.id,
                );
                const showAmazonFallback =
                  book.importStatus === "digital" ||
                  book.searchState === "miss";

                return (
                  <article
                    key={book.id}
                    className="grid gap-4 p-5 sm:p-6 lg:grid-cols-[minmax(0,1fr)_minmax(220px,auto)] lg:items-center"
                  >
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <h3 className="text-lg font-black text-white">
                          {book.title}
                        </h3>
                        {book.binding ? (
                          <span className="rounded-full border border-white/10 px-2.5 py-1 text-xs text-slate-400">
                            {book.binding}
                          </span>
                        ) : null}
                      </div>
                      <p className="mt-1 text-sm text-slate-400">
                        {book.author || "Unknown author"}
                        {book.year ? ` · ${book.year}` : ""}
                        {book.isbn ? ` · ISBN ${book.isbn}` : ""}
                      </p>

                      {book.importStatus === "digital" ? (
                        <p className="mt-3 text-sm leading-6 text-violet-200">
                          eBay used-copy search skipped for this digital or
                          audio edition. Use the Amazon fallback below.
                        </p>
                      ) : null}
                      {book.importStatus === "missing" ? (
                        <p className="mt-3 text-sm text-amber-200">
                          Goodreads did not include an ISBN for this edition.
                        </p>
                      ) : null}
                      {book.importStatus === "invalid" ? (
                        <p className="mt-3 text-sm text-amber-200">
                          Goodreads included an ISBN that did not pass checksum
                          validation.
                        </p>
                      ) : null}
                      {book.searchState === "queued" ||
                      book.searchState === "searching" ? (
                        <p className="mt-3 text-sm text-cyan-200">
                          {book.searchState === "searching"
                            ? "Searching this exact ISBN…"
                            : "Queued for exact-edition search…"}
                        </p>
                      ) : null}
                      {book.searchState === "error" ? (
                        <p className="mt-3 text-sm text-rose-200">
                          Search error: {book.error}
                        </p>
                      ) : null}
                      {book.searchState === "miss" ? (
                        <div className="mt-3">
                          <p className="font-bold text-amber-100">
                            {separatedExact
                              ? "No standard used copy for this exact edition."
                              : "No listing for this exact edition."}
                          </p>
                          <p className="mt-1 text-sm leading-6 text-slate-400">
                            {separatedExact
                              ? `PriceSift found only ${separatedKind} exact copies and kept them out of the standard price result.`
                              : "PriceSift did not replace it with another ISBN."}{" "}
                            Amazon and broader-edition fallbacks are available
                            below.
                          </p>
                        </div>
                      ) : null}
                      {top ? (
                        <div className="mt-3">
                          <p className="text-xl font-black text-emerald-200">
                            ${top.total_price.toFixed(2)}
                          </p>
                          <p className="mt-1 line-clamp-2 text-sm text-slate-300">
                            {top.title}
                          </p>
                          <p className="mt-1 text-xs text-slate-500">
                            {top.condition || "Condition not supplied"} ·{" "}
                            {cleanCount} clean option
                            {cleanCount === 1 ? "" : "s"} shown ·{" "}
                            {book.response?.candidate_count || 0} candidates
                            reviewed
                          </p>
                          {book.response?.selected_verification ? (
                            <p className="mt-1 text-xs text-cyan-200/80">
                              {book.response.selected_verification}
                            </p>
                          ) : null}
                        </div>
                      ) : null}
                    </div>

                    <div className="flex flex-wrap gap-2 lg:justify-end">
                      {top ? (
                        <a
                          href={exactUrl}
                          target="_blank"
                          rel="noreferrer"
                          onClick={() =>
                            track("goodreads_exact_listing_clicked", {
                              isbn: book.isbn,
                              provider: top.provider,
                            })
                          }
                          className="rounded-xl bg-white px-4 py-2.5 text-sm font-bold text-slate-950 transition hover:bg-slate-200"
                        >
                          Open exact listing ↗
                        </a>
                      ) : null}
                      {book.searchState === "miss" && separatedExact ? (
                        <a
                          href={separatedUrl}
                          target="_blank"
                          rel="noreferrer"
                          onClick={() =>
                            track("goodreads_separated_exact_clicked", {
                              isbn: book.isbn,
                              kind: separatedKind,
                            })
                          }
                          className="rounded-xl border border-purple-200/25 bg-purple-200/10 px-4 py-2.5 text-sm font-bold text-purple-100 transition hover:bg-purple-200/15"
                        >
                          {separatedKind === "collectible"
                            ? "Open collectible exact copy ↗"
                            : "Open exact book bundle ↗"}
                        </a>
                      ) : null}
                      {showAmazonFallback ? (
                        <a
                          href={amazonFallback.url}
                          target="_blank"
                          rel="sponsored noreferrer"
                          onClick={() =>
                            track("goodreads_amazon_fallback_clicked", {
                              format: amazonFallback.format,
                              has_exact_identifier:
                                amazonFallback.exactIdentifier,
                              source:
                                book.importStatus === "digital"
                                  ? "digital"
                                  : "exact_miss",
                            })
                          }
                          className="rounded-xl border border-orange-200/25 bg-orange-200/10 px-4 py-2.5 text-sm font-bold text-orange-100 transition hover:bg-orange-200/15"
                        >
                          {amazonFallback.label}
                        </a>
                      ) : null}
                      {book.searchState === "miss" ? (
                        <a
                          href={otherUrl}
                          target="_blank"
                          rel="noreferrer"
                          onClick={() =>
                            track("goodreads_other_editions_clicked", {
                              isbn: book.isbn,
                            })
                          }
                          className="rounded-xl border border-amber-200/25 bg-amber-200/10 px-4 py-2.5 text-sm font-bold text-amber-100 transition hover:bg-amber-200/15"
                        >
                          Search other editions ↗
                        </a>
                      ) : null}
                    </div>
                  </article>
                );
              })}
            </div>
          </section>
        </>
      ) : null}

      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-6 text-slate-400">
        <p className="font-bold text-slate-200">Privacy</p>
        <p className="mt-2">
          The CSV remains in your browser. Exact searches send the selected
          ISBN, title, and author so PriceSift can reject obvious eBay catalog
          mismatches, plus aggregate counts needed to evaluate the beta.
          Clicking a marketplace link records that outbound click. PriceSift
          does not upload or retain the CSV, Goodreads account, ratings,
          reviews, private notes, or complete reading list.
        </p>
      </section>
    </div>
  );
}
