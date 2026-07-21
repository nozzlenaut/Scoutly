import "server-only";

import type { OpenLibraryAvailability } from "@/lib/openLibraryTypes";

type OpenLibraryItem = {
  match?: string;
  status?: string;
  itemURL?: string;
  cover?: { small?: string; medium?: string; large?: string };
  fromRecord?: string;
  publishDate?: string;
};

type OpenLibraryRecord = {
  recordURL?: string;
};

type OpenLibraryPayload = {
  items?: OpenLibraryItem[];
  records?: Record<string, OpenLibraryRecord>;
};

function cleanIsbn(value: string): string | null {
  const cleaned = value.toUpperCase().replace(/[^0-9X]/g, "");
  return cleaned.length === 10 || cleaned.length === 13 ? cleaned : null;
}

function secureUrl(value?: string | null): string | null {
  if (!value) return null;
  try {
    const parsed = new URL(value);
    const hostname = parsed.hostname.toLowerCase();
    const allowed =
      hostname === "openlibrary.org" ||
      hostname.endsWith(".openlibrary.org") ||
      hostname === "archive.org" ||
      hostname.endsWith(".archive.org");
    if (!allowed || !["http:", "https:"].includes(parsed.protocol)) return null;
    parsed.protocol = "https:";
    return parsed.toString();
  } catch {
    return null;
  }
}

export async function lookupOpenLibraryAvailability(
  rawIsbn: string,
): Promise<OpenLibraryAvailability> {
  const isbn = cleanIsbn(rawIsbn);
  if (!isbn) {
    return {
      isbn: rawIsbn,
      lookup_state: "none",
      match: null,
      status: null,
      item_url: null,
      record_url: null,
      cover_url: null,
      publish_date: null,
    };
  }

  try {
    const response = await fetch(
      `https://openlibrary.org/api/volumes/brief/isbn/${encodeURIComponent(isbn)}.json`,
      {
        headers: {
          Accept: "application/json",
          "User-Agent": "PriceSift/0.6.39 (https://github.com/nozzlenaut/Scoutly)",
        },
        next: { revalidate: 21600 },
        signal: AbortSignal.timeout(4500),
      },
    );

    if (!response.ok) throw new Error(`Open Library returned ${response.status}`);

    const payload = (await response.json()) as OpenLibraryPayload;
    const items = Array.isArray(payload.items) ? payload.items : [];
    const records = payload.records || {};
    const item = items[0] || null;
    const itemRecord = item?.fromRecord ? records[item.fromRecord] : undefined;
    const firstRecord = itemRecord || Object.values(records)[0];
    const recordUrl = secureUrl(firstRecord?.recordURL);
    const itemRecordUrl =
      item?.fromRecord?.startsWith("/books/")
        ? secureUrl(`https://openlibrary.org${item.fromRecord}`)
        : null;

    if (item) {
      const match = item.match === "exact" || item.match === "similar" ? item.match : null;
      return {
        isbn,
        lookup_state: "item",
        match,
        status: item.status || null,
        item_url: secureUrl(item.itemURL),
        record_url: itemRecordUrl || recordUrl,
        cover_url: secureUrl(item.cover?.medium || item.cover?.small || item.cover?.large),
        publish_date: item.publishDate || null,
      };
    }

    return {
      isbn,
      lookup_state: firstRecord ? "record" : "none",
      match: null,
      status: null,
      item_url: null,
      record_url: recordUrl,
      cover_url: null,
      publish_date: null,
    };
  } catch {
    return {
      isbn,
      lookup_state: "error",
      match: null,
      status: null,
      item_url: null,
      record_url: null,
      cover_url: null,
      publish_date: null,
    };
  }
}
