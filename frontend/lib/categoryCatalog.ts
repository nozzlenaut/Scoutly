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
    description: "Used camera bodies with eBay Digital Cameras category filtering.",
    placeholder: "Try Sony A7R V, Canon R5 II, Nikon Z6 III...",
    defaultQuery: "Sony A7 III Body",
  },
  {
    id: "lenses",
    label: "Lenses",
    group: "Photography",
    status: "coming-soon",
    description: "Temporarily paused while we validate cleaner eBay lens-category results.",
    placeholder: "Coming soon",
    defaultQuery: "Sony FE 24-70mm f/2.8 GM",
  },
  {
    id: "gpus",
    label: "GPUs",
    group: "PC Parts",
    status: "lab",
    description: "Lab category with eBay Graphics/Video Cards category filtering.",
    placeholder: "Try RTX 5050, RX 480, RX 9070 XT, Arc A580...",
    defaultQuery: "RTX 3060 12GB",
  },
  {
    id: "lego",
    label: "LEGO",
    group: "Collectibles",
    status: "lab",
    description: "Prototype exact set-number search using eBay LEGO set category filtering.",
    placeholder: "Try 75192, 21325, 10316, 76269...",
    defaultQuery: "LEGO Millennium Falcon 75192",
  },
];

export const searchCategories = allCategories.filter((category) => category.status !== "coming-soon");

export function getCategory(id?: string | null) {
  return searchCategories.find((category) => category.id === id) ?? searchCategories[0];
}
