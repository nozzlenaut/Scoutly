export type IndexedProduct = {
  slug: string;
  category: "cameras" | "consoles" | "gpus" | "lego";
  title: string;
  query: string;
  description: string;
  commonTraps: string[];
};

export const indexedProducts: IndexedProduct[] = [
  {
    slug: "sony-a7-iii",
    category: "cameras",
    title: "Sony A7 III Body",
    query: "Sony A7 III Body",
    description: "Current cleaner used listings for the Sony A7 III full-frame mirrorless camera body.",
    commonTraps: ["A7 II or A7R-series bodies", "body shells and repair parts", "battery grips or cages without the camera"],
  },
  {
    slug: "canon-eos-r6",
    category: "cameras",
    title: "Canon EOS R6 Body",
    query: "Canon EOS R6 Body",
    description: "Current cleaner used listings for the original Canon EOS R6 mirrorless camera body.",
    commonTraps: ["EOS R6 Mark II listings", "damaged or overheating bodies", "boxes, cages, and accessory-only listings"],
  },
  {
    slug: "canon-eos-5ds-r",
    category: "cameras",
    title: "Canon EOS 5DS R Body",
    query: "Canon EOS 5DS R Body",
    description: "Current cleaner used listings for the high-resolution Canon EOS 5DS R DSLR body.",
    commonTraps: ["standard EOS 5DS bodies", "5D-series models with similar titles", "parts, shells, and empty boxes"],
  },
  {
    slug: "canon-eos-1d-x-mark-iii",
    category: "cameras",
    title: "Canon EOS-1D X Mark III Body",
    query: "Canon EOS-1D X Mark III Body",
    description: "Current cleaner used listings for the Canon EOS-1D X Mark III professional DSLR body.",
    commonTraps: ["older 1D X generations", "high-wear or damaged professional bodies", "chargers, batteries, and boxes sold alone"],
  },
  {
    slug: "panasonic-lumix-g100",
    category: "cameras",
    title: "Panasonic Lumix G100 Body",
    query: "Panasonic Lumix G100 Body",
    description: "Current cleaner used listings for the Panasonic Lumix G100 Micro Four Thirds camera body.",
    commonTraps: ["G100D or unrelated Lumix models", "lens-only listings", "creator kits missing the camera body"],
  },
  {
    slug: "playstation-5",
    category: "consoles",
    title: "PlayStation 5",
    query: "PlayStation 5",
    description: "Current cleaner used listings for a working Sony PlayStation 5 console.",
    commonTraps: ["controllers, faceplates, stands, or boxes only", "broken HDMI ports and for-parts consoles", "digital and disc editions presented unclearly"],
  },
  {
    slug: "playstation-5-slim",
    category: "consoles",
    title: "PlayStation 5 Slim",
    query: "PlayStation 5 Slim",
    description: "Current cleaner used listings for the smaller PlayStation 5 Slim console family.",
    commonTraps: ["original launch-model PS5 consoles", "detachable disc drives without a console", "empty boxes, shells, and stands"],
  },
  {
    slug: "xbox-series-x",
    category: "consoles",
    title: "Xbox Series X",
    query: "Xbox Series X",
    description: "Current cleaner used listings for a working Microsoft Xbox Series X console.",
    commonTraps: ["Xbox One X systems", "expansion cards and controllers", "for-parts consoles or units with HDMI faults"],
  },
  {
    slug: "xbox-series-s",
    category: "consoles",
    title: "Xbox Series S",
    query: "Xbox Series S",
    description: "Current cleaner used listings for a working Microsoft Xbox Series S console.",
    commonTraps: ["Xbox One S systems", "controller-only bundles", "broken consoles and empty retail boxes"],
  },
  {
    slug: "nvidia-rtx-3060-12gb",
    category: "gpus",
    title: "NVIDIA RTX 3060 12GB",
    query: "NVIDIA RTX 3060 12GB",
    description: "Current cleaner used listings for desktop GeForce RTX 3060 graphics cards with 12GB of VRAM.",
    commonTraps: ["RTX 3060 Ti cards", "mobile/laptop GPUs", "coolers, water blocks, and non-working boards"],
  },
  {
    slug: "nvidia-rtx-3070",
    category: "gpus",
    title: "NVIDIA RTX 3070",
    query: "NVIDIA RTX 3070",
    description: "Current cleaner used listings for desktop GeForce RTX 3070 graphics cards.",
    commonTraps: ["RTX 3070 Ti cards", "gaming laptops", "replacement fans, heatsinks, and for-parts boards"],
  },
  {
    slug: "nvidia-rtx-a4000-16gb",
    category: "gpus",
    title: "NVIDIA RTX A4000 16GB",
    query: "NVIDIA RTX A4000 16GB",
    description: "Current cleaner used listings for the single-slot NVIDIA RTX A4000 workstation GPU with 16GB of VRAM.",
    commonTraps: ["older Quadro P4000 cards", "laptop/workstation systems containing the GPU", "heatsinks, shrouds, and damaged cards"],
  },
  {
    slug: "lego-75192-millennium-falcon",
    category: "lego",
    title: "LEGO 75192 Millennium Falcon",
    query: "LEGO 75192 Millennium Falcon",
    description: "Current cleaner used listings for LEGO Star Wars set 75192, with exact-set filtering.",
    commonTraps: ["instruction books or boxes only", "small replacement-part lots", "incomplete sets missing major sections or minifigures"],
  },
];

export function getIndexedProduct(slug: string): IndexedProduct | undefined {
  return indexedProducts.find((product) => product.slug === slug);
}
