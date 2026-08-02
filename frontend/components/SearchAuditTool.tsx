"use client";

import { ChangeEvent, useEffect, useMemo, useRef, useState } from "react";
import { adminFetch } from "@/lib/api";
import { ADMIN_BROWSER_SESSION } from "@/lib/adminSessionShared";

type CategoryKey =
  | "cameras"
  | "lenses"
  | "consoles"
  | "cpus"
  | "gpus"
  | "ram"
  | "books"
  | "lego";

type AuditStatus = "draft" | "scheduled" | "posted";

type IssueDefinition = {
  key: string;
  label: string;
  postText: string;
  shortText: string;
  positive?: boolean;
};

type ListingRow = {
  id: string;
  title: string;
  price: string;
  url: string;
  condition?: string;
  imageUrl?: string;
  shipping?: number;
  totalPrice?: number;
  notes: string;
  flags: Record<string, boolean>;
};

type SearchAudit = {
  id: string;
  category: CategoryKey;
  query: string;
  marketplace: string;
  resultCount: number;
  condition: string;
  location: string;
  purchaseFormat: string;
  sortOrder: string;
  status: AuditStatus;
  scheduledFor: string;
  screenshotDone: boolean;
  videoDone: boolean;
  hashtags: string;
  customIssues: IssueDefinition[];
  listings: ListingRow[];
  createdAt: string;
  updatedAt: string;
};

type RawEbayListing = {
  title: string;
  price: number;
  shipping: number;
  total_price: number;
  condition: string;
  url: string;
  image_url: string | null;
  item_location: string | null;
  marketplace_item_id: string | null;
};

type RawEbayResponse = {
  query: string;
  returned: number;
  method: { pricesift_filters_applied: boolean };
  listings: RawEbayListing[];
};

const STORAGE_KEY = "pricesift-search-audits-v1";
const SELECTED_KEY = "pricesift-search-audits-selected-v1";
const DEFAULT_RESULT_COUNT = 15;

const CATEGORY_LABELS: Record<CategoryKey, string> = {
  cameras: "Cameras",
  lenses: "Lenses",
  consoles: "Consoles",
  cpus: "CPUs",
  gpus: "GPUs",
  ram: "RAM",
  books: "Books",
  lego: "LEGO",
};

const CATEGORY_LINKS: Record<CategoryKey, string> = {
  cameras: "https://www.pricesift.app/cameras",
  lenses: "https://www.pricesift.app/lenses",
  consoles: "https://www.pricesift.app/consoles",
  cpus: "https://www.pricesift.app/cpus",
  gpus: "https://www.pricesift.app/gpus",
  ram: "https://www.pricesift.app/ram",
  books: "https://www.pricesift.app/books",
  lego: "https://www.pricesift.app/lego",
};

const CATEGORY_HASHTAGS: Record<CategoryKey, string> = {
  cameras: "#Photography #UsedGear",
  lenses: "#Photography #UsedGear",
  consoles: "#Gaming #UsedTech",
  cpus: "#PCBuilding #UsedTech",
  gpus: "#PCGaming #UsedTech",
  ram: "#PCBuilding #UsedTech",
  books: "#Books #Secondhand",
  lego: "#LEGO #Secondhand",
};

const CATEGORY_ISSUES: Record<CategoryKey, IssueDefinition[]> = {
  cameras: [
    { key: "wrong_model", label: "Wrong model / variant", postText: "were the wrong model or variant.", shortText: "wrong model/variant" },
    { key: "bundle", label: "Lens or other gear included", postText: "included lenses or other gear.", shortText: "bundles" },
    { key: "missing_detail", label: "No shutter count", postText: "didn’t list a shutter count.", shortText: "missing shutter count" },
    { key: "condition", label: "Condition concern", postText: "had a condition concern.", shortText: "condition concerns" },
    { key: "parts", label: "Parts / repair / accessory only", postText: "were parts, repair, or accessory-only listings.", shortText: "parts/repair/accessory only" },
    { key: "worth", label: "Worth investigating", postText: "looked worth investigating.", shortText: "worth investigating", positive: true },
  ],
  lenses: [
    { key: "wrong_model", label: "Wrong lens or mount", postText: "were the wrong lens or mount.", shortText: "wrong lens/mount" },
    { key: "bundle", label: "Camera or bundle included", postText: "included a camera or other bundled gear.", shortText: "bundles" },
    { key: "missing_detail", label: "Optical condition missing", postText: "didn’t clearly describe the optical condition.", shortText: "missing optical condition" },
    { key: "condition", label: "Fungus / haze / damage concern", postText: "raised a fungus, haze, or damage concern.", shortText: "optical/condition concerns" },
    { key: "parts", label: "Parts / repair / accessory only", postText: "were parts, repair, or accessory-only listings.", shortText: "parts/repair/accessory only" },
    { key: "worth", label: "Worth investigating", postText: "looked worth investigating.", shortText: "worth investigating", positive: true },
  ],
  consoles: [
    { key: "wrong_model", label: "Wrong model / storage / region", postText: "were the wrong model, storage, or region.", shortText: "wrong model/storage/region" },
    { key: "bundle", label: "Bundle changes the value", postText: "were bundles that changed the comparison.", shortText: "bundles" },
    { key: "missing_detail", label: "Controller / cables unclear", postText: "didn’t clearly include the expected controller or cables.", shortText: "missing essentials" },
    { key: "condition", label: "Condition concern", postText: "had a condition concern.", shortText: "condition concerns" },
    { key: "parts", label: "Parts / repair / box only", postText: "were parts, repair, or packaging-only listings.", shortText: "parts/repair/box only" },
    { key: "worth", label: "Worth investigating", postText: "looked worth investigating.", shortText: "worth investigating", positive: true },
  ],
  cpus: [
    { key: "wrong_model", label: "Wrong model / generation", postText: "were the wrong model or generation.", shortText: "wrong model/generation" },
    { key: "bundle", label: "Motherboard or system bundle", postText: "were motherboard or system bundles.", shortText: "bundles" },
    { key: "missing_detail", label: "Working proof unclear", postText: "didn’t clearly show that the CPU was tested and working.", shortText: "missing working proof" },
    { key: "condition", label: "Engineering sample / unusual variant", postText: "were engineering samples or unusual variants.", shortText: "engineering samples/variants" },
    { key: "parts", label: "Damaged / parts only", postText: "were damaged or parts-only listings.", shortText: "damaged/parts only" },
    { key: "worth", label: "Worth investigating", postText: "looked worth investigating.", shortText: "worth investigating", positive: true },
  ],
  gpus: [
    { key: "wrong_model", label: "Wrong GPU / VRAM / variant", postText: "were the wrong GPU, VRAM size, or variant.", shortText: "wrong GPU/VRAM/variant" },
    { key: "bundle", label: "Full system or multi-item bundle", postText: "were full systems or multi-item bundles.", shortText: "systems/bundles" },
    { key: "missing_detail", label: "Working proof unclear", postText: "didn’t clearly show that the GPU was tested and working.", shortText: "missing working proof" },
    { key: "condition", label: "Condition concern", postText: "had a condition concern.", shortText: "condition concerns" },
    { key: "parts", label: "Parts / repair / cooler only", postText: "were parts, repair, or cooler-only listings.", shortText: "parts/repair/accessory only" },
    { key: "worth", label: "Worth investigating", postText: "looked worth investigating.", shortText: "worth investigating", positive: true },
  ],
  ram: [
    { key: "wrong_model", label: "Wrong capacity / speed / type", postText: "had the wrong capacity, speed, or memory type.", shortText: "wrong capacity/speed/type" },
    { key: "bundle", label: "Mixed or mismatched kit", postText: "were mixed or mismatched kits.", shortText: "mixed/mismatched kits" },
    { key: "missing_detail", label: "Part number unclear", postText: "didn’t clearly provide the exact part number.", shortText: "missing part number" },
    { key: "condition", label: "Laptop / desktop mismatch", postText: "used the wrong laptop or desktop form factor.", shortText: "wrong form factor" },
    { key: "parts", label: "Untested / damaged", postText: "were untested or damaged listings.", shortText: "untested/damaged" },
    { key: "worth", label: "Worth investigating", postText: "looked worth investigating.", shortText: "worth investigating", positive: true },
  ],
  books: [
    { key: "wrong_model", label: "Wrong ISBN / edition", postText: "were the wrong ISBN or edition.", shortText: "wrong ISBN/edition" },
    { key: "bundle", label: "Lot or bundle", postText: "were lots or bundles rather than one exact book.", shortText: "lots/bundles" },
    { key: "missing_detail", label: "Format unclear or wrong", postText: "had an unclear or incorrect format.", shortText: "wrong/unclear format" },
    { key: "condition", label: "Condition concern", postText: "had a condition concern.", shortText: "condition concerns" },
    { key: "parts", label: "Missing edition details", postText: "didn’t provide enough edition details to verify the match.", shortText: "missing edition details" },
    { key: "worth", label: "Worth investigating", postText: "looked worth investigating.", shortText: "worth investigating", positive: true },
  ],
  lego: [
    { key: "wrong_model", label: "Wrong set / set number", postText: "were the wrong set or set number.", shortText: "wrong set" },
    { key: "bundle", label: "Lot or bundle", postText: "were lots or bundles rather than the exact set.", shortText: "lots/bundles" },
    { key: "missing_detail", label: "Incomplete / minifigures missing", postText: "were incomplete or missing minifigures.", shortText: "incomplete/missing minifigures" },
    { key: "condition", label: "Condition concern", postText: "had a condition concern.", shortText: "condition concerns" },
    { key: "parts", label: "Box / manual / parts only", postText: "were box, manual, or parts-only listings.", shortText: "box/manual/parts only" },
    { key: "worth", label: "Worth investigating", postText: "looked worth investigating.", shortText: "worth investigating", positive: true },
  ],
};

function makeId(prefix: string): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return `${prefix}-${crypto.randomUUID()}`;
  }
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function makeListing(): ListingRow {
  return {
    id: makeId("listing"),
    title: "",
    price: "",
    url: "",
    condition: "",
    imageUrl: "",
    shipping: 0,
    totalPrice: 0,
    notes: "",
    flags: {},
  };
}

function makeAudit(category: CategoryKey = "cameras"): SearchAudit {
  const now = new Date().toISOString();
  return {
    id: makeId("audit"),
    category,
    query: "",
    marketplace: "eBay",
    resultCount: DEFAULT_RESULT_COUNT,
    condition: "Used",
    location: "US",
    purchaseFormat: "Buy It Now",
    sortOrder: "Best Match",
    status: "draft",
    scheduledFor: "",
    screenshotDone: false,
    videoDone: false,
    hashtags: CATEGORY_HASHTAGS[category],
    customIssues: [],
    listings: Array.from({ length: DEFAULT_RESULT_COUNT }, makeListing),
    createdAt: now,
    updatedAt: now,
  };
}

function parsePrice(value: string): number | null {
  const parsed = Number.parseFloat(value.replace(/[^0-9.]/g, ""));
  return Number.isFinite(parsed) ? parsed : null;
}

function formatMoney(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: value % 1 === 0 ? 0 : 2,
  }).format(value);
}

function shortDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Unknown";
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

function safeAudits(value: unknown): SearchAudit[] {
  if (!Array.isArray(value)) return [];
  return value.filter((item): item is SearchAudit => {
    return Boolean(item && typeof item === "object" && "id" in item && "listings" in item);
  });
}

function buildSearchUrl(query: string): string {
  const params = new URLSearchParams({
    _nkw: query,
    LH_ItemCondition: "3000",
    LH_BIN: "1",
    LH_PrefLoc: "1",
    _sop: "12",
  });
  return `https://www.ebay.com/sch/i.html?${params.toString()}`;
}

function buildDetailedPost(audit: SearchAudit, issues: IssueDefinition[], counts: Record<string, number>, priceRange: string, overlap: boolean): string {
  const lines = issues
    .filter((issue) => !issue.positive && counts[issue.key] > 0)
    .map((issue) => `${counts[issue.key]} ${issue.postText}`);
  const worth = issues.find((issue) => issue.positive);
  const worthCount = worth ? counts[worth.key] : 0;

  const sections = [
    `I checked the first ${audit.resultCount} ${audit.condition.toLowerCase()} ${audit.location} ${audit.marketplace} results for “${audit.query || "[search term]"}.”`,
    lines.join("\n"),
    priceRange ? `Prices ranged from ${priceRange}.` : "",
    worthCount > 0 ? `Only ${worthCount} looked worth investigating.` : "",
    overlap ? "Some categories overlap." : "",
    "Plenty of listings. Very few comparable options.",
    audit.hashtags.trim(),
  ].filter(Boolean);

  return sections.join("\n\n");
}

function buildCompactPost(audit: SearchAudit, issues: IssueDefinition[], counts: Record<string, number>, priceRange: string): string {
  const stats = issues
    .filter((issue) => !issue.positive && counts[issue.key] > 0)
    .map((issue) => `${counts[issue.key]} ${issue.shortText}.`);
  const worth = issues.find((issue) => issue.positive);
  const worthCount = worth ? counts[worth.key] : 0;
  if (priceRange) stats.push(`${priceRange}.`);
  if (worthCount > 0) stats.push(`Only ${worthCount} worth a closer look.`);

  return [
    `I checked ${audit.resultCount} used ${audit.marketplace} results for “${audit.query || "[search term]"}.”`,
    stats.join("\n"),
    "Plenty of listings. Few comparable options.",
    audit.hashtags.trim(),
  ]
    .filter(Boolean)
    .join("\n\n");
}

function buildUltraCompactPost(audit: SearchAudit, issues: IssueDefinition[], counts: Record<string, number>, priceRange: string): string {
  const query = (audit.query || "[search term]").slice(0, 72);
  const stats = issues
    .filter((issue) => !issue.positive && counts[issue.key] > 0)
    .slice(0, 5)
    .map((issue) => `${counts[issue.key]} ${issue.shortText}`);
  const worth = issues.find((issue) => issue.positive);
  const worthCount = worth ? counts[worth.key] : 0;
  if (priceRange) stats.push(priceRange);
  if (worthCount > 0) stats.push(`${worthCount} worth investigating`);

  const withoutTags = [
    `${audit.resultCount} used ${audit.marketplace} results for “${query}”:`,
    stats.join(" · "),
    "Many listings. Few clean comparisons.",
  ]
    .filter(Boolean)
    .join("\n\n");

  const withTags = [withoutTags, audit.hashtags.trim()].filter(Boolean).join("\n\n");
  const candidate = withTags.length <= 300 ? withTags : withoutTags;
  return candidate.length <= 300 ? candidate : `${candidate.slice(0, 299)}…`;
}

export function SearchAuditTool() {
  const [audits, setAudits] = useState<SearchAudit[]>([]);
  const [activeId, setActiveId] = useState("");
  const [ready, setReady] = useState(false);
  const [notice, setNotice] = useState("");
  const [loadingListings, setLoadingListings] = useState(false);
  const [customIssueLabel, setCustomIssueLabel] = useState("");
  const importRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    try {
      const stored = safeAudits(JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]"));
      if (stored.length > 0) {
        const selected = localStorage.getItem(SELECTED_KEY);
        const resolved = stored.some((audit) => audit.id === selected) ? selected || stored[0].id : stored[0].id;
        setAudits(stored);
        setActiveId(resolved);
      } else {
        const first = makeAudit();
        setAudits([first]);
        setActiveId(first.id);
        localStorage.setItem(STORAGE_KEY, JSON.stringify([first]));
        localStorage.setItem(SELECTED_KEY, first.id);
      }
    } catch {
      const first = makeAudit();
      setAudits([first]);
      setActiveId(first.id);
      setNotice("The saved audit list could not be read, so a fresh audit was opened.");
    } finally {
      setReady(true);
    }
  }, []);

  const active = audits.find((audit) => audit.id === activeId) || audits[0];
  const issueDefinitions = useMemo(() => {
    if (!active) return [];
    return [...CATEGORY_ISSUES[active.category], ...active.customIssues];
  }, [active]);

  const counts = useMemo(() => {
    const result: Record<string, number> = {};
    issueDefinitions.forEach((issue) => {
      result[issue.key] = active?.listings.filter((listing) => listing.flags[issue.key]).length || 0;
    });
    return result;
  }, [active, issueDefinitions]);

  const priceRange = useMemo(() => {
    if (!active) return "";
    const prices = active.listings.map((listing) => parsePrice(listing.price)).filter((value): value is number => value !== null);
    if (prices.length === 0) return "";
    const minimum = Math.min(...prices);
    const maximum = Math.max(...prices);
    return minimum === maximum ? formatMoney(minimum) : `${formatMoney(minimum)}–${formatMoney(maximum)}`;
  }, [active]);

  const overlap = useMemo(() => {
    if (!active) return false;
    const problemIssues = issueDefinitions.filter((issue) => !issue.positive);
    const totalFlags = problemIssues.reduce((sum, issue) => sum + (counts[issue.key] || 0), 0);
    const flaggedRows = active.listings.filter((listing) => problemIssues.some((issue) => listing.flags[issue.key])).length;
    return totalFlags > flaggedRows && flaggedRows > 0;
  }, [active, counts, issueDefinitions]);

  const detailedPost = active ? buildDetailedPost(active, issueDefinitions, counts, priceRange, overlap) : "";
  const compactPost = active ? buildCompactPost(active, issueDefinitions, counts, priceRange) : "";
  const ultraCompactPost = active ? buildUltraCompactPost(active, issueDefinitions, counts, priceRange) : "";
  const blueskyPost = detailedPost.length <= 300 ? detailedPost : compactPost.length <= 300 ? compactPost : ultraCompactPost;
  const detailedReply = active
    ? [
        `Here’s the same “${active.query || "[search term]"}” search in PriceSift.`,
        "The goal isn’t more listings—it’s a few cleaner, comparable options without the wrong matches and obvious junk.",
        CATEGORY_LINKS[active.category],
      ].join("\n\n")
    : "";
  const compactReply = active
    ? [
        `Same search in PriceSift: “${(active.query || "[search term]").slice(0, 80)}.”`,
        "Fewer results is the point: cleaner, more comparable options.",
        CATEGORY_LINKS[active.category],
      ].join("\n\n")
    : "";
  const replyPost = detailedReply.length <= 300 ? detailedReply : compactReply.length <= 300 ? compactReply : `${compactReply.slice(0, 299)}…`;

  function persist(next: SearchAudit[], selectedId = activeId) {
    setAudits(next);
    setActiveId(selectedId);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    localStorage.setItem(SELECTED_KEY, selectedId);
  }

  function updateActive(patch: Partial<SearchAudit>) {
    if (!active) return;
    const next = audits.map((audit) =>
      audit.id === active.id ? { ...audit, ...patch, updatedAt: new Date().toISOString() } : audit,
    );
    persist(next, active.id);
  }

  function updateListing(id: string, patch: Partial<ListingRow>) {
    if (!active) return;
    const listings = active.listings.map((listing) => (listing.id === id ? { ...listing, ...patch } : listing));
    updateActive({ listings });
  }

  async function loadRawEbayResults() {
    if (!active || loadingListings) return;
    const query = active.query.trim();
    if (!query) {
      setNotice("Enter an eBay search first.");
      return;
    }

    setLoadingListings(true);
    setNotice("");
    try {
      const params = new URLSearchParams({
        q: query,
        limit: String(active.resultCount),
        token: ADMIN_BROWSER_SESSION,
      });
      const response = await adminFetch(`/api/search-audit/ebay?${params.toString()}`, {
        cache: "no-store",
      });
      if (!response.ok) {
        const payload = await response.json().catch(() => null);
        throw new Error(payload?.detail || `eBay audit search failed (${response.status})`);
      }

      const payload = (await response.json()) as RawEbayResponse;
      const listings: ListingRow[] = payload.listings.map((listing, index) => ({
        id: active.listings[index]?.id || makeId("listing"),
        title: listing.title,
        price: String(listing.price),
        url: listing.url,
        condition: listing.condition,
        imageUrl: listing.image_url || "",
        shipping: listing.shipping,
        totalPrice: listing.total_price,
        notes: "",
        flags: {},
      }));
      while (listings.length < active.resultCount) listings.push(makeListing());

      updateActive({
        listings,
        marketplace: "eBay",
        condition: "Used",
        location: "US",
        purchaseFormat: "Buy It Now",
        sortOrder: "Best Match",
      });
      setNotice(
        `Loaded ${payload.returned} raw eBay result${payload.returned === 1 ? "" : "s"}. No PriceSift include/exclude filters were used.`,
      );
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "The raw eBay results could not be loaded.");
    } finally {
      setLoadingListings(false);
    }
  }

  function toggleFlag(listing: ListingRow, key: string) {
    updateListing(listing.id, {
      flags: { ...listing.flags, [key]: !listing.flags[key] },
    });
  }

  function changeResultCount(value: number) {
    if (!active) return;
    const resultCount = Math.max(1, Math.min(30, value || 1));
    const listings = active.listings.slice(0, resultCount);
    while (listings.length < resultCount) listings.push(makeListing());
    updateActive({ resultCount, listings });
  }

  function changeCategory(category: CategoryKey) {
    if (!active) return;
    updateActive({ category, hashtags: CATEGORY_HASHTAGS[category] });
  }

  function createNewAudit() {
    const nextAudit = makeAudit(active?.category || "cameras");
    persist([nextAudit, ...audits], nextAudit.id);
    setNotice("New audit created.");
  }

  function duplicateAudit() {
    if (!active) return;
    const now = new Date().toISOString();
    const duplicate: SearchAudit = {
      ...active,
      id: makeId("audit"),
      query: active.query ? `${active.query} copy` : "",
      status: "draft",
      scheduledFor: "",
      screenshotDone: false,
      videoDone: false,
      listings: active.listings.map((listing) => ({ ...listing, id: makeId("listing") })),
      createdAt: now,
      updatedAt: now,
    };
    persist([duplicate, ...audits], duplicate.id);
    setNotice("Audit duplicated.");
  }

  function deleteAudit() {
    if (!active || !window.confirm(`Delete the audit for “${active.query || "untitled search"}”?`)) return;
    const remaining = audits.filter((audit) => audit.id !== active.id);
    if (remaining.length === 0) {
      const replacement = makeAudit();
      persist([replacement], replacement.id);
    } else {
      persist(remaining, remaining[0].id);
    }
    setNotice("Audit deleted.");
  }

  async function copyText(text: string, label: string) {
    try {
      await navigator.clipboard.writeText(text);
      setNotice(`${label} copied.`);
    } catch {
      setNotice("Copy failed. Select the text manually instead.");
    }
  }

  function addCustomIssue() {
    if (!active) return;
    const label = customIssueLabel.trim();
    if (!label) return;
    const issue: IssueDefinition = {
      key: makeId("custom"),
      label,
      postText: `had ${label.toLowerCase()}.`,
      shortText: label.toLowerCase(),
    };
    updateActive({ customIssues: [...active.customIssues, issue] });
    setCustomIssueLabel("");
  }

  function removeCustomIssue(key: string) {
    if (!active) return;
    const customIssues = active.customIssues.filter((issue) => issue.key !== key);
    const listings = active.listings.map((listing) => {
      const flags = { ...listing.flags };
      delete flags[key];
      return { ...listing, flags };
    });
    updateActive({ customIssues, listings });
  }

  function downloadJson(filename: string, value: unknown) {
    const blob = new Blob([JSON.stringify(value, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  function exportActive() {
    if (!active) return;
    const slug = (active.query || "search-audit").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
    downloadJson(`${slug || "search-audit"}.json`, active);
  }

  function exportAll() {
    downloadJson("pricesift-search-audits-backup.json", audits);
  }

  function importBackup(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const parsed = JSON.parse(String(reader.result || ""));
        const imported = safeAudits(Array.isArray(parsed) ? parsed : [parsed]);
        if (imported.length === 0) throw new Error("No audits found");
        const merged = [...imported, ...audits.filter((audit) => !imported.some((item) => item.id === audit.id))];
        persist(merged, imported[0].id);
        setNotice(`${imported.length} audit${imported.length === 1 ? "" : "s"} imported.`);
      } catch {
        setNotice("That file did not contain a valid Search Audit backup.");
      }
    };
    reader.readAsText(file);
  }

  function fullResearchPacket(): string {
    if (!active) return "";
    const lines = active.listings.map((listing, index) => {
      const flags = issueDefinitions.filter((issue) => listing.flags[issue.key]).map((issue) => issue.label);
      return [
        `${index + 1}. ${listing.title || "Untitled listing"}`,
        listing.price ? `Price: ${listing.price}` : "",
        flags.length ? `Flags: ${flags.join(", ")}` : "Flags: none",
        listing.notes ? `Notes: ${listing.notes}` : "",
        listing.url ? `URL: ${listing.url}` : "",
      ]
        .filter(Boolean)
        .join(" | ");
    });
    return [
      `PriceSift Search Audit: ${active.query || "Untitled"}`,
      `Category: ${CATEGORY_LABELS[active.category]}`,
      `Method: first ${active.resultCount}; ${active.condition}; ${active.location}; ${active.purchaseFormat}; ${active.sortOrder}`,
      priceRange ? `Price range: ${priceRange}` : "",
      overlap ? "Some issue categories overlap." : "",
      "",
      blueskyPost,
      "",
      "Listing notes:",
      ...lines,
    ]
      .filter((value) => value !== "")
      .join("\n");
  }

  if (!ready || !active) {
    return <div className="rounded-3xl border border-white/10 bg-white/[0.05] p-8 text-slate-300">Loading saved audits…</div>;
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[280px_minmax(0,1fr)]">
      <aside className="h-fit rounded-3xl border border-white/10 bg-white/[0.05] p-4 xl:sticky xl:top-6">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-cyan-300">Saved locally</p>
            <h2 className="mt-1 text-xl font-black text-white">Audit queue</h2>
          </div>
          <button onClick={createNewAudit} className="rounded-xl bg-cyan-200 px-3 py-2 text-sm font-black text-slate-950 hover:bg-cyan-100">
            + New
          </button>
        </div>

        <div className="mt-4 max-h-[52vh] space-y-2 overflow-y-auto pr-1">
          {audits.map((audit) => (
            <button
              key={audit.id}
              onClick={() => persist(audits, audit.id)}
              className={`w-full rounded-2xl border p-3 text-left transition ${
                audit.id === active.id
                  ? "border-cyan-200/50 bg-cyan-200/10"
                  : "border-white/10 bg-black/10 hover:bg-white/[0.06]"
              }`}
            >
              <p className="truncate font-bold text-white">{audit.query || "Untitled search"}</p>
              <div className="mt-1 flex items-center justify-between gap-2 text-xs text-slate-400">
                <span>{CATEGORY_LABELS[audit.category]}</span>
                <span className="capitalize">{audit.status}</span>
              </div>
              <p className="mt-1 text-xs text-slate-500">{shortDate(audit.updatedAt)}</p>
            </button>
          ))}
        </div>

        <div className="mt-4 grid gap-2">
          <button onClick={duplicateAudit} className="rounded-xl border border-white/10 px-3 py-2 text-sm font-semibold text-slate-200 hover:bg-white/[0.06]">
            Duplicate current
          </button>
          <button onClick={exportAll} className="rounded-xl border border-white/10 px-3 py-2 text-sm font-semibold text-slate-200 hover:bg-white/[0.06]">
            Backup all audits
          </button>
          <button onClick={() => importRef.current?.click()} className="rounded-xl border border-white/10 px-3 py-2 text-sm font-semibold text-slate-200 hover:bg-white/[0.06]">
            Import backup
          </button>
          <input ref={importRef} type="file" accept="application/json,.json" onChange={importBackup} className="hidden" />
          <button onClick={deleteAudit} className="rounded-xl border border-rose-300/20 px-3 py-2 text-sm font-semibold text-rose-200 hover:bg-rose-300/10">
            Delete current
          </button>
        </div>
      </aside>

      <div className="min-w-0 space-y-6">
        {notice ? (
          <div className="flex items-center justify-between rounded-2xl border border-emerald-300/20 bg-emerald-300/10 px-4 py-3 text-sm text-emerald-100">
            <span>{notice}</span>
            <button onClick={() => setNotice("")} className="font-bold">×</button>
          </div>
        ) : null}

        <section className="rounded-3xl border border-white/10 bg-white/[0.05] p-5 sm:p-6">
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <label className="xl:col-span-2">
              <span className="text-sm font-semibold text-slate-300">Exact search</span>
              <input
                value={active.query}
                onChange={(event) => updateActive({ query: event.target.value })}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    event.preventDefault();
                    void loadRawEbayResults();
                  }
                }}
                placeholder="Sony a7 III body only"
                className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none focus:border-cyan-200/50"
              />
            </label>
            <label>
              <span className="text-sm font-semibold text-slate-300">PriceSift category</span>
              <select
                value={active.category}
                onChange={(event) => changeCategory(event.target.value as CategoryKey)}
                className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none focus:border-cyan-200/50"
              >
                {(Object.keys(CATEGORY_LABELS) as CategoryKey[]).map((key) => (
                  <option key={key} value={key}>{CATEGORY_LABELS[key]}</option>
                ))}
              </select>
            </label>
            <label>
              <span className="text-sm font-semibold text-slate-300">Listings reviewed</span>
              <input
                type="number"
                min={1}
                max={30}
                value={active.resultCount}
                onChange={(event) => changeResultCount(Number.parseInt(event.target.value, 10))}
                className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none focus:border-cyan-200/50"
              />
            </label>
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
            {[
              ["Condition", "condition", active.condition],
              ["Location", "location", active.location],
              ["Purchase format", "purchaseFormat", active.purchaseFormat],
              ["Sort", "sortOrder", active.sortOrder],
              ["Marketplace", "marketplace", active.marketplace],
            ].map(([label, key, value]) => (
              <label key={key}>
                <span className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">{label}</span>
                <input
                  value={value}
                  onChange={(event) => updateActive({ [key]: event.target.value } as Partial<SearchAudit>)}
                  className="mt-2 w-full rounded-xl border border-white/10 bg-slate-950 px-3 py-2 text-sm text-white outline-none focus:border-cyan-200/50"
                />
              </label>
            ))}
          </div>

          <div className="mt-5 flex flex-wrap gap-3">
            <button
              onClick={() => void loadRawEbayResults()}
              disabled={loadingListings || !active.query.trim()}
              className="rounded-2xl bg-cyan-200 px-4 py-3 font-black text-slate-950 hover:bg-cyan-100 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loadingListings ? "Loading raw eBay results…" : "Load raw eBay results"}
            </button>
            <a href={buildSearchUrl(active.query)} target="_blank" rel="noreferrer" className="rounded-2xl border border-white/15 bg-white/10 px-4 py-3 font-bold text-white hover:bg-white/15">
              Open eBay search ↗
            </a>
            <a href={CATEGORY_LINKS[active.category]} target="_blank" rel="noreferrer" className="rounded-2xl border border-cyan-200/30 bg-cyan-200/10 px-4 py-3 font-bold text-cyan-100 hover:bg-cyan-200/15">
              Open PriceSift category ↗
            </a>
            <button onClick={exportActive} className="rounded-2xl border border-white/10 px-4 py-3 font-bold text-slate-200 hover:bg-white/[0.06]">
              Export this audit
            </button>
          </div>
          <p className="mt-3 text-xs text-slate-400">
            Raw means the exact text above goes to eBay with Used, US, Buy It Now, and Best Match. PriceSift catalog terms, include/exclude rules, local filters, and ranking are skipped.
          </p>
        </section>

        <section className="rounded-3xl border border-white/10 bg-white/[0.05] p-5 sm:p-6">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-cyan-300">One row per listing</p>
              <h2 className="mt-1 text-2xl font-black text-white">Review the first {active.resultCount}</h2>
              <p className="mt-2 text-sm text-slate-400">The raw search fills the image, title, price, shipping, condition, and link. You mostly just inspect each listing and hit the tags.</p>
            </div>
            <div className="flex max-w-xl flex-1 gap-2 lg:justify-end">
              <input
                value={customIssueLabel}
                onChange={(event) => setCustomIssueLabel(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    event.preventDefault();
                    addCustomIssue();
                  }
                }}
                placeholder="Add a custom issue flag"
                className="min-w-0 flex-1 rounded-xl border border-white/10 bg-slate-950 px-3 py-2 text-sm text-white outline-none focus:border-cyan-200/50"
              />
              <button onClick={addCustomIssue} className="rounded-xl border border-white/10 px-3 py-2 text-sm font-bold text-slate-200 hover:bg-white/[0.06]">Add</button>
            </div>
          </div>

          {active.customIssues.length > 0 ? (
            <div className="mt-4 flex flex-wrap gap-2">
              {active.customIssues.map((issue) => (
                <button key={issue.key} onClick={() => removeCustomIssue(issue.key)} className="rounded-full border border-amber-200/20 bg-amber-200/10 px-3 py-1 text-xs text-amber-100 hover:bg-amber-200/15">
                  {issue.label} ×
                </button>
              ))}
            </div>
          ) : null}

          <div className="mt-5 space-y-4">
            {active.listings.map((listing, index) => (
              <article key={listing.id} className="rounded-2xl border border-white/10 bg-slate-950/70 p-4">
                <div className="grid gap-3 lg:grid-cols-[42px_88px_minmax(0,1fr)_150px]">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/[0.07] font-black text-slate-300">{index + 1}</div>
                  {listing.imageUrl ? (
                    <img src={listing.imageUrl} alt="" loading="lazy" className="h-20 w-20 rounded-xl bg-white object-contain" />
                  ) : (
                    <div className="flex h-20 w-20 items-center justify-center rounded-xl border border-white/10 bg-black/20 text-center text-[10px] text-slate-600">No image</div>
                  )}
                  <input
                    value={listing.title}
                    onChange={(event) => updateListing(listing.id, { title: event.target.value })}
                    placeholder="Listing title (optional)"
                    className="rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm text-white outline-none focus:border-cyan-200/50"
                  />
                  <input
                    value={listing.price}
                    onChange={(event) => updateListing(listing.id, { price: event.target.value })}
                    placeholder="$1,499"
                    inputMode="decimal"
                    className="rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm text-white outline-none focus:border-cyan-200/50"
                  />
                </div>

                {listing.condition || listing.url || listing.shipping ? (
                  <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-slate-400">
                    {listing.condition ? <span>Condition: <strong className="text-slate-200">{listing.condition}</strong></span> : null}
                    {listing.shipping ? <span>Shipping: <strong className="text-slate-200">{formatMoney(listing.shipping)}</strong></span> : null}
                    {listing.totalPrice ? <span>Total: <strong className="text-slate-200">{formatMoney(listing.totalPrice)}</strong></span> : null}
                    {listing.url ? (
                      <a href={listing.url} target="_blank" rel="noreferrer" className="font-bold text-cyan-200 hover:text-cyan-100">Inspect listing ↗</a>
                    ) : null}
                  </div>
                ) : null}

                <div className="mt-3 flex flex-wrap gap-2">
                  {issueDefinitions.map((issue) => {
                    const checked = Boolean(listing.flags[issue.key]);
                    return (
                      <button
                        type="button"
                        key={issue.key}
                        onClick={() => toggleFlag(listing, issue.key)}
                        className={`rounded-full border px-3 py-1.5 text-xs font-semibold transition ${
                          checked
                            ? issue.positive
                              ? "border-emerald-200/50 bg-emerald-200/20 text-emerald-100"
                              : "border-amber-200/50 bg-amber-200/20 text-amber-100"
                            : "border-white/10 text-slate-400 hover:bg-white/[0.06]"
                        }`}
                      >
                        {checked ? "✓ " : ""}{issue.label}
                      </button>
                    );
                  })}
                </div>

                <details className="mt-3">
                  <summary className="cursor-pointer text-xs font-semibold text-slate-500 hover:text-slate-300">Optional URL and notes</summary>
                  <div className="mt-3 grid gap-3 lg:grid-cols-2">
                    <input
                      value={listing.url}
                      onChange={(event) => updateListing(listing.id, { url: event.target.value })}
                      placeholder="Listing URL"
                      className="rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm text-white outline-none focus:border-cyan-200/50"
                    />
                    <input
                      value={listing.notes}
                      onChange={(event) => updateListing(listing.id, { notes: event.target.value })}
                      placeholder="Short note"
                      className="rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm text-white outline-none focus:border-cyan-200/50"
                    />
                  </div>
                </details>
              </article>
            ))}
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-3xl border border-white/10 bg-white/[0.05] p-5 sm:p-6">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-cyan-300">Automatic totals</p>
            <h2 className="mt-1 text-2xl font-black text-white">Audit summary</h2>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              {issueDefinitions.map((issue) => (
                <div key={issue.key} className="rounded-2xl border border-white/10 bg-black/15 p-4">
                  <p className="text-sm text-slate-400">{issue.label}</p>
                  <p className={`mt-1 text-3xl font-black ${issue.positive ? "text-emerald-200" : "text-white"}`}>{counts[issue.key] || 0}</p>
                </div>
              ))}
              <div className="rounded-2xl border border-white/10 bg-black/15 p-4 sm:col-span-2">
                <p className="text-sm text-slate-400">Observed price range</p>
                <p className="mt-1 text-2xl font-black text-white">{priceRange || "Add prices to calculate"}</p>
              </div>
            </div>
            {overlap ? <p className="mt-3 text-xs text-amber-200">Some issue categories overlap; the generated post notes that automatically.</p> : null}
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/[0.05] p-5 sm:p-6">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-fuchsia-300">Publishing queue</p>
            <h2 className="mt-1 text-2xl font-black text-white">Finish and track</h2>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <label>
                <span className="text-sm font-semibold text-slate-300">Status</span>
                <select value={active.status} onChange={(event) => updateActive({ status: event.target.value as AuditStatus })} className="mt-2 w-full rounded-xl border border-white/10 bg-slate-950 px-3 py-2 text-white">
                  <option value="draft">Draft</option>
                  <option value="scheduled">Scheduled</option>
                  <option value="posted">Posted</option>
                </select>
              </label>
              <label>
                <span className="text-sm font-semibold text-slate-300">Scheduled for</span>
                <input type="datetime-local" value={active.scheduledFor} onChange={(event) => updateActive({ scheduledFor: event.target.value })} className="mt-2 w-full rounded-xl border border-white/10 bg-slate-950 px-3 py-2 text-white" />
              </label>
            </div>
            <label className="mt-4 block">
              <span className="text-sm font-semibold text-slate-300">Hashtags</span>
              <input value={active.hashtags} onChange={(event) => updateActive({ hashtags: event.target.value })} className="mt-2 w-full rounded-xl border border-white/10 bg-slate-950 px-3 py-2 text-white" />
            </label>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <button onClick={() => updateActive({ screenshotDone: !active.screenshotDone })} className={`rounded-2xl border p-4 text-left ${active.screenshotDone ? "border-emerald-200/40 bg-emerald-200/10 text-emerald-100" : "border-white/10 text-slate-300"}`}>
                <span className="font-bold">{active.screenshotDone ? "✓ " : ""}Screenshot ready</span>
              </button>
              <button onClick={() => updateActive({ videoDone: !active.videoDone })} className={`rounded-2xl border p-4 text-left ${active.videoDone ? "border-emerald-200/40 bg-emerald-200/10 text-emerald-100" : "border-white/10 text-slate-300"}`}>
                <span className="font-bold">{active.videoDone ? "✓ " : ""}PriceSift video ready</span>
              </button>
            </div>
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-3xl border border-cyan-200/20 bg-cyan-200/[0.07] p-5 sm:p-6">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-cyan-300">Main post</p>
                <h2 className="mt-1 text-2xl font-black text-white">Pain-point audit</h2>
              </div>
              <span className={`rounded-full px-3 py-1 text-xs font-black ${blueskyPost.length <= 300 ? "bg-emerald-200/15 text-emerald-100" : "bg-rose-200/15 text-rose-100"}`}>
                {blueskyPost.length}/300
              </span>
            </div>
            <textarea readOnly value={blueskyPost} className="mt-4 min-h-72 w-full rounded-2xl border border-white/10 bg-slate-950 p-4 text-sm leading-6 text-slate-100" />
            {detailedPost.length > 300 ? <p className="mt-2 text-xs text-amber-200">The detailed draft was too long, so the tool switched to a compact version.</p> : null}
            <button onClick={() => copyText(blueskyPost, "Main post")} className="mt-4 w-full rounded-2xl bg-cyan-200 px-4 py-3 font-black text-slate-950 hover:bg-cyan-100">Copy main post</button>
          </div>

          <div className="rounded-3xl border border-fuchsia-200/20 bg-fuchsia-200/[0.07] p-5 sm:p-6">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-fuchsia-300">Thread reply</p>
                <h2 className="mt-1 text-2xl font-black text-white">PriceSift comparison</h2>
              </div>
              <span className={`rounded-full px-3 py-1 text-xs font-black ${replyPost.length <= 300 ? "bg-emerald-200/15 text-emerald-100" : "bg-rose-200/15 text-rose-100"}`}>
                {replyPost.length}/300
              </span>
            </div>
            <textarea readOnly value={replyPost} className="mt-4 min-h-72 w-full rounded-2xl border border-white/10 bg-slate-950 p-4 text-sm leading-6 text-slate-100" />
            <button onClick={() => copyText(replyPost, "Video reply")} className="mt-4 w-full rounded-2xl bg-fuchsia-200 px-4 py-3 font-black text-slate-950 hover:bg-fuchsia-100">Copy video reply</button>
          </div>
        </section>

        <section className="rounded-3xl border border-white/10 bg-white/[0.05] p-5 sm:p-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-slate-500">Reuse later</p>
              <h2 className="mt-1 text-2xl font-black text-white">Research packet</h2>
              <p className="mt-2 text-sm text-slate-400">Copies the method, generated post, listing flags, notes, and URLs for outreach or a future Used Market Notes page.</p>
            </div>
            <button onClick={() => copyText(fullResearchPacket(), "Research packet")} className="rounded-2xl border border-white/10 px-5 py-3 font-bold text-white hover:bg-white/[0.06]">Copy full packet</button>
          </div>
        </section>
      </div>
    </div>
  );
}
