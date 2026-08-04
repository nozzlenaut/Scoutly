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
      "Find the right used camera without sorting through wrong bodies, empty boxes, broken gear, and accessory bait.",
    placeholder: "Search by camera model",
    defaultQuery: "",
  },
  {
    id: "lenses",
    label: "Lenses",
    group: "Photography",
    status: "beta",
    description:
      "Give good glass another life with cleaner used lens inventory matched by mount, focal range, type, and brand.",
    placeholder: "Browse current KEH lenses",
    defaultQuery: "",
  },
  {
    id: "gpus",
    label: "GPUs",
    group: "PC Parts",
    status: "active",
    description:
      "Reuse capable graphics hardware without wading through laptop chips, coolers, broken cards, and complete-PC listings.",
    placeholder: "Search by GPU model",
    defaultQuery: "",
  },
  {
    id: "ram",
    label: "RAM",
    group: "PC Parts",
    status: "active",
    description:
      "Match the exact used memory kit your system needs instead of gambling on a near-match that will not fit or work.",
    placeholder: "Build a RAM configuration",
    defaultQuery: "",
  },
  {
    id: "cpus",
    label: "CPUs",
    group: "PC Parts",
    status: "active",
    description:
      "Keep a working PC useful longer with the exact compatible used processor—not a nearby generation or suffix.",
    placeholder: "Build an exact CPU search",
    defaultQuery: "",
  },
  {
    id: "consoles",
    label: "Consoles",
    group: "Gaming",
    status: "active",
    description:
      "Find a complete used system—not a box, controller, shell, accessory bundle, or broken parts console.",
    placeholder: "Search by console model",
    defaultQuery: "",
  },
  {
    id: "books",
    label: "Books",
    group: "Books & Media",
    status: "beta",
    description:
      "Find the exact used edition by ISBN and keep another physical copy in circulation.",
    placeholder: "Search by ISBN-10 or ISBN-13",
    defaultQuery: "",
  },
  {
    id: "lego",
    label: "LEGO",
    group: "Collectibles",
    status: "beta",
    description:
      "Find the exact used set and keep a complete build out of the parts bin.",
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
