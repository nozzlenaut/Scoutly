export type SearchCategory = {
  id: string;
  label: string;
  group: string;
  status: "active" | "lab" | "planned";
  description: string;
  placeholder: string;
  defaultQuery: string;
};

export const searchCategories: SearchCategory[] = [
  {
    id: "cameras",
    label: "Cameras",
    group: "Photography",
    status: "active",
    description: "Used camera bodies with accessory and parts-only filtering.",
    placeholder: "Try Sony A7 III, Canon R6, Fuji X-T4...",
    defaultQuery: "Sony A7 III Body",
  },
  {
    id: "lenses",
    label: "Lenses",
    group: "Photography",
    status: "active",
    description: "Used lenses with cap, hood, fungus, haze, and parts-only filtering.",
    placeholder: "Try Sony 24-70 2.8, Canon RF 50 1.8...",
    defaultQuery: "Sony FE 24-70mm f/2.8 GM",
  },
  {
    id: "gpus",
    label: "GPUs",
    group: "PC Parts",
    status: "lab",
    description: "Catalog matching is built, but live marketplace pricing is waiting on eBay API access.",
    placeholder: "Try RTX 3060, RX 6700 XT, Arc A770...",
    defaultQuery: "RTX 3060 12GB",
  },
];

export function getCategory(id?: string | null) {
  return searchCategories.find((category) => category.id === id) ?? searchCategories[0];
}
