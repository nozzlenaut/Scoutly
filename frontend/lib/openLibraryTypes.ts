export type OpenLibraryLookupState = "item" | "record" | "none" | "error";

export type OpenLibraryAvailability = {
  isbn: string;
  lookup_state: OpenLibraryLookupState;
  match: "exact" | "similar" | null;
  status: "full access" | "lendable" | "checked out" | "restricted" | string | null;
  item_url: string | null;
  record_url: string | null;
  cover_url: string | null;
  publish_date: string | null;
};
