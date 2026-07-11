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
    placeholder: "Try Sony A7 IV, Canon R6 II, Nikon Z8...",
    defaultQuery: "Sony A7 III Body",
  },
  {
    id: "lenses",
    label: "Lenses",
    group: "Photography",
    status: "active",
    description: "Used lenses with cap, hood, fungus, haze, and parts-only filtering.",
    placeholder: "Try Sony 85 1.8, Canon RF 70-200 2.8...",
    defaultQuery: "Sony FE 24-70mm f/2.8 GM",
  },
  {
    id: "gpus",
    label: "GPUs",
    group: "PC Parts",
    status: "lab",
    description: "Lab category with live eBay search and expanded NVIDIA, AMD, and Intel matching.",
    placeholder: "Try RTX 3060, RX 9070 XT, Arc B580...",
    defaultQuery: "RTX 3060 12GB",
  },
];

export function getCategory(id?: string | null) {
  return searchCategories.find((category) => category.id === id) ?? searchCategories[0];
}
