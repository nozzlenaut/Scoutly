export type SearchCategory = {
  id: string;
  label: string;
  group: string;
  status: "active" | "beta" | "planned" | "coming-soon";
  description: string;
  placeholder: string;
  defaultQuery: string;
};

export const allCategories: SearchCategory[] = [
  {
    id: "cameras",
    label: "Cameras",
    group: "Photography",
    status: "active",
    description:
      "Used camera bodies with eBay Digital Cameras category filtering.",
    placeholder: "Search by camera model",
    defaultQuery: "",
  },
  {
    id: "lenses",
    label: "Lenses",
    group: "Photography",
    status: "beta",
    description:
      "Current used KEH lens inventory filtered by mount, prime or zoom type, focal range, and optional brand.",
    placeholder: "Browse current KEH lenses",
    defaultQuery: "",
  },
  {
    id: "gpus",
    label: "GPUs",
    group: "PC Parts",
    status: "active",
    description:
      "Used desktop graphics cards with strict model and form-factor filtering.",
    placeholder: "Search by GPU model",
    defaultQuery: "",
  },
  {
    id: "ram",
    label: "RAM",
    group: "PC Parts",
    status: "active",
    description:
      "Strict DDR3, DDR4, and DDR5 memory-kit searches built from exact specifications.",
    placeholder: "Build a RAM configuration",
    defaultQuery: "",
  },
  {
    id: "cpus",
    label: "CPUs",
    group: "PC Parts",
    status: "active",
    description:
      "Consumer desktop processors selected by manufacturer, socket, generation, and exact model.",
    placeholder: "Build an exact CPU search",
    defaultQuery: "",
  },
  {
    id: "consoles",
    label: "Consoles",
    group: "Gaming",
    status: "active",
    description:
      "Core-model searches for complete Xbox, PlayStation, and Nintendo systems, with variants grouped together.",
    placeholder: "Search by console model",
    defaultQuery: "",
  },
  {
    id: "books",
    label: "Books",
    group: "Books & Media",
    status: "beta",
    description:
      "Exact used-book edition search using ISBN-10 or ISBN-13.",
    placeholder: "Search by ISBN-10 or ISBN-13",
    defaultQuery: "",
  },
  {
    id: "lego",
    label: "LEGO",
    group: "Collectibles",
    status: "beta",
    description: "Beta exact-set search using set names or set numbers.",
    placeholder: "Search by set name or set number",
    defaultQuery: "",
  },
];

const statusOrder: Record<SearchCategory["status"], number> = {
  active: 0,
  beta: 1,
  planned: 2,
  "coming-soon": 3,
};

export const searchCategories = allCategories
  .filter((category) => category.status !== "coming-soon")
  .sort(
    (left, right) =>
      statusOrder[left.status] - statusOrder[right.status] ||
      left.label.localeCompare(right.label),
  );

export function getCategoryById(id?: string | null): SearchCategory | null {
  if (!id) return null;
  return allCategories.find((category) => category.id === id) ?? null;
}

export function getSearchCategoryById(
  id?: string | null,
): SearchCategory | null {
  const category = getCategoryById(id);
  if (
    !category ||
    category.status === "coming-soon" ||
    category.status === "planned"
  )
    return null;
  return category;
}

export function getCategory(id?: string | null) {
  return getSearchCategoryById(id) ?? searchCategories[0];
}
