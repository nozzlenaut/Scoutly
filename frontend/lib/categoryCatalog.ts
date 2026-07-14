export type SearchCategory = {
  id: string;
  label: string;
  group: string;
  status: "active" | "lab" | "planned" | "coming-soon";
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
    placeholder: "Try Sony A7R V, Canon R5 II, Nikon Z6 III...",
    defaultQuery: "Sony A7 III Body",
  },
  {
    id: "lenses",
    label: "Lenses",
    group: "Photography",
    status: "coming-soon",
    description:
      "Temporarily paused while we validate cleaner eBay lens-category results.",
    placeholder: "Coming soon",
    defaultQuery: "Sony FE 24-70mm f/2.8 GM",
  },
  {
    id: "gpus",
    label: "GPUs",
    group: "PC Parts",
    status: "active",
    description:
      "Used desktop graphics cards with strict model and form-factor filtering.",
    placeholder: "Try RTX 5050, RX 480, RX 9070 XT, Arc A580...",
    defaultQuery: "RTX 3060 12GB",
  },
  {
    id: "ram",
    label: "RAM",
    group: "PC Parts",
    status: "lab",
    description:
      "Specification-builder testing for strict DDR3, DDR4, and DDR5 memory-kit searches.",
    placeholder: "Build a RAM configuration",
    defaultQuery: "",
  },
  {
    id: "consoles",
    label: "Consoles",
    group: "Gaming",
    status: "active",
    description:
      "Complete Xbox, PlayStation, and Nintendo systems with accessory filtering.",
    placeholder: "Try PS5 Disc, Xbox Series X, Switch OLED...",
    defaultQuery: "Xbox Series X 1TB",
  },
  {
    id: "lego",
    label: "LEGO",
    group: "Collectibles",
    status: "lab",
    description: "Early lab prototype for exact LEGO set-number search.",
    placeholder: "Try 75192, 21325, 10316, 76269...",
    defaultQuery: "LEGO Millennium Falcon 75192",
  },
];

export const searchCategories = allCategories.filter(
  (category) => category.status !== "coming-soon",
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
