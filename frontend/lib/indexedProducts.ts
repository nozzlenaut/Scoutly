export type IndexedProduct = {
  slug: string;
  category: "cameras" | "consoles" | "gpus" | "lego";
  title: string;
  query: string;
  brand: string;
  description: string;
  buyingSummary: string;
  buyingChecks: string[];
  commonTraps: string[];
};

export const indexedProducts: IndexedProduct[] = [
  {
    slug: "sony-a7-iii",
    category: "cameras",
    title: "Sony A7 III Body",
    query: "Sony A7 III Body",
    brand: "Sony",
    description: "Current cleaner used listings for the Sony A7 III full-frame mirrorless camera body.",
    buyingSummary: "The A7 III remains a sensible used buy when the body is fully functional and priced for its condition. Cosmetic wear matters far less than sensor, mount, stabilization, shutter, control, or corrosion problems.",
    buyingChecks: ["Check the sensor and lens mount for damage rather than normal dust or rub marks.", "Ask for shutter-count context when it is available, but do not treat one number as an expiration date.", "Confirm IBIS, autofocus, card slots, EVF, rear screen, buttons, and dials work normally.", "Inspect the battery compartment, hot shoe, ports, and screws for corrosion or impact damage."],
    commonTraps: ["A7 II or A7R-series bodies", "body shells and repair parts", "battery grips or cages without the camera"],
  },
  {
    slug: "canon-eos-r6",
    category: "cameras",
    title: "Canon EOS R6 Body",
    query: "Canon EOS R6 Body",
    brand: "Canon",
    description: "Current cleaner used listings for the original Canon EOS R6 mirrorless camera body.",
    buyingSummary: "The original EOS R6 can be a strong used option if you specifically want the first-generation body. The biggest listing-level mistake is paying for an R6 while assuming the listing is an R6 Mark II, or overlooking disclosed functional damage.",
    buyingChecks: ["Confirm the listing is the original EOS R6 and not the R6 Mark II.", "Inspect the sensor, RF mount, card slots, EVF, rear screen, and articulated-screen hinge.", "Confirm autofocus, IBIS, shutter, buttons, dials, ports, and both card slots behave normally.", "Treat vague heat-shutdown, power, liquid, or intermittent-control disclosures as real defects rather than cosmetic notes."],
    commonTraps: ["EOS R6 Mark II listings", "bodies with disclosed functional or heat-shutdown problems", "boxes, cages, and accessory-only listings"],
  },
  {
    slug: "canon-eos-5ds-r",
    category: "cameras",
    title: "Canon EOS 5DS R Body",
    query: "Canon EOS 5DS R Body",
    brand: "Canon",
    description: "Current cleaner used listings for the high-resolution Canon EOS 5DS R DSLR body.",
    buyingSummary: "The 5DS R is worth considering used when you specifically want this high-resolution DSLR and the price reflects its age and condition. Exact-model identification matters because 5DS, 5D-series, and accessory listings can look deceptively similar in search results.",
    buyingChecks: ["Confirm the badge and listing identify the EOS 5DS R, not the standard 5DS or another 5D-series body.", "Check the sensor, EF mount, mirror box, shutter operation, and viewfinder condition.", "Verify card slots, autofocus, rear display, buttons, dials, and ports.", "Use shutter count as condition context when available and inspect for professional-use wear around the mount and controls."],
    commonTraps: ["standard EOS 5DS bodies", "5D-series models with similar titles", "parts, shells, and empty boxes"],
  },
  {
    slug: "canon-eos-1d-x-mark-iii",
    category: "cameras",
    title: "Canon EOS-1D X Mark III Body",
    query: "Canon EOS-1D X Mark III Body",
    brand: "Canon",
    description: "Current cleaner used listings for the Canon EOS-1D X Mark III professional DSLR body.",
    buyingSummary: "A used 1D X Mark III can represent a lot of camera for the money, but professional bodies may have seen heavy real-world use. Functional checks and honest wear history matter more than whether the exterior looks pristine.",
    buyingChecks: ["Confirm Mark III rather than an older 1D X generation.", "Check shutter count when available together with shutter, mirror, autofocus, and card-slot operation.", "Inspect the integrated grip controls, mount, ports, hot shoe, battery compartment, and body seams for impact or corrosion.", "Confirm the rear screen, viewfinder, buttons, dials, network/connection ports, and both card slots work normally."],
    commonTraps: ["older 1D X generations", "high-wear or damaged professional bodies", "chargers, batteries, and boxes sold alone"],
  },
  {
    slug: "panasonic-lumix-g100",
    category: "cameras",
    title: "Panasonic Lumix G100 Body",
    query: "Panasonic Lumix G100 Body",
    brand: "Panasonic",
    description: "Current cleaner used listings for the Panasonic Lumix G100 Micro Four Thirds camera body.",
    buyingSummary: "The G100 can make sense used when you want a small Micro Four Thirds body and the listing clearly identifies the exact model. Pay more attention to the screen hinge, mount, sensor, controls, and ports than light cosmetic wear.",
    buyingChecks: ["Confirm G100 versus G100D and make sure the listing actually includes the camera body.", "Inspect the Micro Four Thirds mount and sensor for damage.", "Check the articulated screen and hinge through their full range of motion.", "Verify autofocus, EVF, card slot, USB/HDMI ports, buttons, dials, and battery compartment."],
    commonTraps: ["G100D or unrelated Lumix models", "lens-only listings", "creator kits missing the camera body"],
  },
  {
    slug: "canon-eos-m50-mark-ii",
    category: "cameras",
    title: "Canon EOS M50 Mark II Body",
    query: "Canon EOS M50 Mark II Body",
    brand: "Canon",
    description: "Current cleaner used listings for the Canon EOS M50 Mark II mirrorless camera body.",
    buyingSummary: "The EOS M50 Mark II can still be a useful compact used camera when the price is right, but exact-model identification matters because original M50 bodies, kits, accessories, and damaged cameras often share nearly identical marketplace wording.",
    buyingChecks: ["Confirm the listing is the EOS M50 Mark II rather than the original EOS M50.", "Inspect the EF-M mount and sensor for impact, corrosion, or obvious damage.", "Check the articulated screen and hinge, autofocus, shutter, hot shoe, card slot, buttons, dials, and ports.", "Confirm what is included in kits and bundles instead of assuming the pictured lens, battery, charger, or accessories are part of the sale."],
    commonTraps: ["original EOS M50 bodies", "lens kits or accessories presented unclearly", "boxes, cages, batteries, chargers, and damaged bodies"],
  },
  {
    slug: "canon-eos-r10",
    category: "cameras",
    title: "Canon EOS R10 Body",
    query: "Canon EOS R10 Body",
    brand: "Canon",
    description: "Current cleaner used listings for the Canon EOS R10 APS-C mirrorless camera body.",
    buyingSummary: "A used EOS R10 is a straightforward target when the discount is worthwhile and the listing clearly identifies the body. Nearby Canon RF models, kits, lenses, cages, and damaged bodies can make broad searches noisier than the model name suggests.",
    buyingChecks: ["Confirm EOS R10 rather than another Canon RF body such as the R50 or R7.", "Inspect the RF mount and sensor for physical damage.", "Verify autofocus, EVF, articulated screen and hinge, shutter, card slot, buttons, dials, hot shoe, and ports.", "Check whether a lens, battery, charger, or other bundle item shown in the photos is explicitly included."],
    commonTraps: ["other Canon EOS R-series bodies", "lens-only or kit listings", "cages, accessories, boxes, and damaged bodies"],
  },
  {
    slug: "sony-zv-1",
    category: "cameras",
    title: "Sony ZV-1",
    query: "Sony ZV-1",
    brand: "Sony",
    description: "Current cleaner used listings for the original Sony ZV-1 compact camera.",
    buyingSummary: "The original ZV-1 can make sense used when you want a small fixed-lens camera and the listing is clearly for the camera itself. Similar ZV models and creator accessories frequently appear beside the actual ZV-1 in broad marketplace searches.",
    buyingChecks: ["Confirm the original ZV-1 rather than ZV-1F, ZV-1 II, or another Sony ZV model.", "Check the fixed lens for smooth zoom operation, impact damage, haze, or obvious optical problems.", "Verify autofocus, recording, screen and hinge, buttons, zoom controls, ports, hot shoe, and battery compartment.", "Make sure grips, microphones, cages, batteries, and creator-kit accessories are not being mistaken for the camera itself."],
    commonTraps: ["ZV-1F or ZV-1 II listings", "creator grips, microphones, cages, and accessory kits", "damaged lens mechanisms or camera-for-parts listings"],
  },
  {
    slug: "sony-a6600",
    category: "cameras",
    title: "Sony a6600 Body",
    query: "Sony a6600 Body",
    brand: "Sony",
    description: "Current cleaner used listings for the Sony a6600 APS-C mirrorless camera body.",
    buyingSummary: "The a6600 remains a capable used APS-C body when the price reflects its age and condition. Sony's nearby a6000-series names are easy to mix up, so exact model identification matters before comparing prices.",
    buyingChecks: ["Confirm a6600 rather than a6100, a6400, a6500, or another a6000-series body.", "Inspect the E mount and sensor, and verify stabilization, autofocus, shutter, EVF, card slot, screen, buttons, and dials.", "Check the screen hinge and ports for damage or looseness.", "Inspect the battery compartment, hot shoe, screws, and body seams for corrosion or impact damage."],
    commonTraps: ["other Sony a6000-series bodies", "battery grips, cages, and accessories", "damaged bodies, shells, and repair-part listings"],
  },
  {
    slug: "sony-a7s-iii",
    category: "cameras",
    title: "Sony A7S III Body",
    query: "Sony A7S III Body",
    brand: "Sony",
    description: "Current cleaner used listings for the Sony A7S III full-frame mirrorless camera body.",
    buyingSummary: "The A7S III is an expensive enough used purchase that model accuracy and functional testing matter more than cosmetic perfection. Similar A7-series names, cages, accessories, and heavily used video bodies can muddy marketplace searches.",
    buyingChecks: ["Confirm A7S III rather than A7 III, A7R III, A7S II, or another A7-series body.", "Inspect the sensor and E mount, then verify autofocus, stabilization, shutter, EVF, articulated screen, both card slots, buttons, dials, and ports.", "Check the screen hinge, HDMI and USB areas, hot shoe, battery compartment, and body seams for impact or corrosion.", "For a video-heavy body, ask for current evidence that recording, card writing, audio connections, and output behave normally."],
    commonTraps: ["other Sony A7-series bodies", "cages, handles, batteries, and video accessories", "high-wear, damaged, or for-parts bodies"],
  },
  {
    slug: "playstation-5",
    category: "consoles",
    title: "PlayStation 5",
    query: "PlayStation 5",
    brand: "Sony",
    description: "Current cleaner used listings for a working original Sony PlayStation 5 console.",
    buyingSummary: "A used original PS5 is attractive when it is meaningfully cheaper than a new or Slim system and the important hardware is confirmed working. HDMI faults, broken units, accessories, and unclear Disc/Digital listings are the main marketplace traps to slow down for.",
    buyingChecks: ["Confirm original PS5 versus PS5 Slim or PS5 Pro, and confirm Disc versus Digital if that matters to you.", "Verify clean HDMI output, USB ports, Wi-Fi/networking, storage, and normal startup without error messages.", "For a Disc Edition, test disc insertion, reading, installation, and ejection.", "Check what is actually included; controller, stand, HDMI cable, power cable, and retail box should never be assumed from a headline."],
    commonTraps: ["controllers, faceplates, stands, or boxes only", "broken HDMI ports and for-parts consoles", "digital and disc editions presented unclearly"],
  },
  {
    slug: "playstation-5-slim",
    category: "consoles",
    title: "PlayStation 5 Slim",
    query: "PlayStation 5 Slim",
    brand: "Sony",
    description: "Current cleaner used listings for the smaller PlayStation 5 Slim console family.",
    buyingSummary: "The PS5 Slim is a straightforward used target as long as the listing really is the Slim console and its included hardware is clear. Detachable drives, stands, shells, boxes, and original-generation PS5s can all pollute broad marketplace searches.",
    buyingChecks: ["Confirm the smaller Slim chassis rather than the original PS5 or PS5 Pro.", "If a disc drive is included, verify it is installed and reads/ejects discs normally.", "Test HDMI output, USB ports, networking, storage, startup, and fan behavior.", "Confirm the controller, cables, horizontal feet or stand accessories, and any detachable drive shown are actually included."],
    commonTraps: ["original launch-model PS5 consoles", "detachable disc drives without a console", "empty boxes, shells, and stands"],
  },
  {
    slug: "xbox-series-x",
    category: "consoles",
    title: "Xbox Series X",
    query: "Xbox Series X",
    brand: "Microsoft",
    description: "Current cleaner used listings for a working Microsoft Xbox Series X console.",
    buyingSummary: "The Series X is a good used target when the discount is worthwhile and the console has clean video output, a healthy disc drive, and no disclosed power or HDMI problems. The name remains easy to confuse with Xbox One X in marketplace titles.",
    buyingChecks: ["Confirm Xbox Series X rather than Xbox One X or a Series accessory.", "Verify HDMI output, startup, networking, USB ports, internal storage, and normal fan behavior.", "Test the optical drive with a known-good compatible disc.", "Confirm controller and cables are included only when the listing explicitly says so."],
    commonTraps: ["Xbox One X systems", "expansion cards and controllers", "for-parts consoles or units with HDMI faults"],
  },
  {
    slug: "xbox-series-s",
    category: "consoles",
    title: "Xbox Series S",
    query: "Xbox Series S",
    brand: "Microsoft",
    description: "Current cleaner used listings for a working Microsoft Xbox Series S console.",
    buyingSummary: "A used Series S can be inexpensive, but make sure the listing is a current Series console rather than an Xbox One S and check the storage version being sold. Because it is digital-only, healthy networking, HDMI output, and internal storage matter especially.",
    buyingChecks: ["Confirm Xbox Series S rather than Xbox One S.", "Check the stated storage capacity and make sure the price matches the version being sold.", "Verify HDMI output, startup, Wi-Fi/networking, USB ports, internal storage, and fan behavior.", "Confirm controller, power cable, and HDMI cable are actually included rather than pictured generically."],
    commonTraps: ["Xbox One S systems", "controller-only bundles", "broken consoles and empty retail boxes"],
  },
  {
    slug: "nintendo-switch",
    category: "consoles",
    title: "Nintendo Switch",
    query: "Nintendo Switch",
    brand: "Nintendo",
    description: "Current cleaner used listings for the original Nintendo Switch console family, excluding Switch Lite, OLED, and Switch 2 models.",
    buyingSummary: "The original Switch is still a useful used target when you specifically want the standard dockable system and the price reflects its age and accessories. Broad searches are especially messy because Lite, OLED, Switch 2, docks, Joy-Con, boxes, and broken tablets often share the same keywords.",
    buyingChecks: ["Confirm the standard Nintendo Switch rather than Switch Lite, OLED, or Switch 2.", "Check the screen, USB-C port, game-card reader, microSD slot, Wi-Fi, speakers, and battery behavior.", "Test both Joy-Con rails and confirm attached controllers connect, charge, and register inputs normally.", "If a dock and charger matter to you, make sure they are explicitly included and test TV output through the dock."],
    commonTraps: ["Switch Lite, Switch OLED, or Switch 2 systems", "tablet-only, dock-only, or Joy-Con-only listings", "broken USB-C ports, damaged screens, and for-parts systems"],
  },
  {
    slug: "nintendo-switch-2",
    category: "consoles",
    title: "Nintendo Switch 2",
    query: "Nintendo Switch 2",
    brand: "Nintendo",
    description: "Current cleaner used listings for the Nintendo Switch 2 console, filtered away from original Switch variants and accessory-only results.",
    buyingSummary: "Switch 2 is exactly the kind of used search where strict model matching helps: original Switch, OLED, Lite, cases, controllers, docks, boxes, and accessories can all appear beside the actual console. Focus on a complete, working system rather than the cheapest title containing the words ‘Switch 2.’",
    buyingChecks: ["Confirm the listing is the Switch 2 console rather than an original Switch-family product or accessory.", "Check the display, USB-C ports, game-card reader, storage, networking, speakers, and battery behavior.", "Test the controller attachment/charging system and verify all included controls register normally.", "Confirm any dock, charger, controllers, cables, or bundled game shown are actually included in the sale."],
    commonTraps: ["original Switch, OLED, or Lite systems", "cases, docks, controllers, boxes, and other accessories", "broken, incomplete, or tablet-only systems"],
  },
  {
    slug: "nvidia-rtx-3060-12gb",
    category: "gpus",
    title: "NVIDIA RTX 3060 12GB",
    query: "NVIDIA RTX 3060 12GB",
    brand: "NVIDIA",
    description: "Current cleaner used listings for desktop GeForce RTX 3060 graphics cards with 12GB of VRAM.",
    buyingSummary: "The 12GB RTX 3060 remains a straightforward used target when the exact VRAM version, desktop card, and condition are clear. Marketplace results commonly mix in 3060 Ti cards, laptop systems, 8GB variants, coolers, water blocks, and dead boards.",
    buyingChecks: ["Confirm GeForce RTX 3060 desktop hardware with 12GB of VRAM rather than a Ti, 8GB, or laptop variant.", "Ask for a working screenshot or test showing the GPU model/VRAM and a game or benchmark running without artifacts or crashes.", "Inspect the PCIe edge, power connector, PCB, video outputs, heatsink, and fans for damage or corrosion.", "Check that fan noise and temperatures look reasonable for that exact partner model instead of relying on one universal temperature number."],
    commonTraps: ["RTX 3060 Ti or 8GB variants", "mobile/laptop GPUs", "coolers, water blocks, and non-working boards"],
  },
  {
    slug: "nvidia-rtx-3070",
    category: "gpus",
    title: "NVIDIA RTX 3070",
    query: "NVIDIA RTX 3070",
    brand: "NVIDIA",
    description: "Current cleaner used listings for desktop GeForce RTX 3070 graphics cards.",
    buyingSummary: "The RTX 3070 can still be compelling used when the price makes sense for your workload and the card is proven stable. Mining history by itself is less useful than evidence of clean output, correct identification, stable load behavior, healthy fans, and undamaged power hardware.",
    buyingChecks: ["Confirm RTX 3070 rather than RTX 3070 Ti or a laptop containing a mobile 3070.", "Ask to see the card identified correctly and running a game or benchmark without crashes or visual artifacts.", "Inspect fans, power connectors, PCIe edge, outputs, heatsink, and PCB for burning, corrosion, bending, or rough repair work.", "Check dimensions and power requirements for the exact partner-board model before buying."],
    commonTraps: ["RTX 3070 Ti cards", "gaming laptops", "replacement fans, heatsinks, and for-parts boards"],
  },
  {
    slug: "nvidia-rtx-4060",
    category: "gpus",
    title: "NVIDIA RTX 4060",
    query: "NVIDIA RTX 4060",
    brand: "NVIDIA",
    description: "Current cleaner used listings for desktop GeForce RTX 4060 graphics cards.",
    buyingSummary: "A used RTX 4060 only makes sense when its discount versus readily available newer inventory is meaningful. Exact matching still matters because 4060 Ti cards, laptops, replacement coolers, and broken boards routinely share the same search terms.",
    buyingChecks: ["Confirm desktop RTX 4060 rather than RTX 4060 Ti or a mobile/laptop GPU.", "Verify the card identifies correctly and can sustain a game or benchmark without artifacts, driver resets, or crashes.", "Inspect fans, outputs, PCIe edge, PCB, heatsink, and power connector for physical or electrical damage.", "Check the exact partner card's dimensions and power connector before assuming it fits your case and PSU."],
    commonTraps: ["RTX 4060 Ti cards", "gaming laptops and mobile GPUs", "replacement fans, coolers, water blocks, and non-working boards"],
  },
  {
    slug: "nvidia-rtx-4070",
    category: "gpus",
    title: "NVIDIA RTX 4070",
    query: "NVIDIA RTX 4070",
    brand: "NVIDIA",
    description: "Current cleaner used listings for desktop GeForce RTX 4070 graphics cards.",
    buyingSummary: "The RTX 4070 is worth considering used when the seller can demonstrate a healthy card and the price clearly beats comparable current options. Search results need careful model separation because 4070 Super, Ti, Ti Super, laptops, and cooling parts often appear beside the base 4070.",
    buyingChecks: ["Confirm the base desktop RTX 4070 rather than Super, Ti, Ti Super, or laptop variants.", "Ask for correct GPU identification and a stable game or benchmark run without artifacts or crashes.", "Inspect the power connection, PCIe edge, PCB, video outputs, heatsink, and fans for damage or questionable repair work.", "Verify dimensions and power-connector requirements for the exact partner model."],
    commonTraps: ["RTX 4070 Super, Ti, or Ti Super cards", "gaming laptops and mobile GPUs", "coolers, fans, water blocks, and for-parts boards"],
  },
  {
    slug: "nvidia-rtx-a4000-16gb",
    category: "gpus",
    title: "NVIDIA RTX A4000 16GB",
    query: "NVIDIA RTX A4000 16GB",
    brand: "NVIDIA",
    description: "Current cleaner used listings for the single-slot NVIDIA RTX A4000 workstation GPU with 16GB of VRAM.",
    buyingSummary: "The RTX A4000 is a specialized used buy: its compact single-slot workstation design and 16GB capacity can be valuable, but search results easily mix in older P4000-class hardware, whole workstations, cooling parts, and damaged boards.",
    buyingChecks: ["Confirm RTX A4000 with 16GB rather than Quadro P4000 or another similarly named workstation card.", "Verify the card identifies correctly with the expected memory and runs a sustained workload without artifacts or crashes.", "Inspect the blower, power connector, PCIe edge, PCB, and display outputs for damage or corrosion.", "Check that any display adapters you need are included; accessory bundles vary widely on used workstation cards."],
    commonTraps: ["older Quadro P4000 cards", "laptop/workstation systems containing the GPU", "heatsinks, shrouds, and damaged cards"],
  },
  {
    slug: "lego-75192-millennium-falcon",
    category: "lego",
    title: "LEGO 75192 Millennium Falcon",
    query: "LEGO 75192 Millennium Falcon",
    brand: "LEGO",
    description: "Current cleaner used listings for LEGO Star Wars set 75192, with exact-set filtering.",
    buyingSummary: "A used 75192 can save real money, but ‘used’ and ‘complete’ are not the same promise. For a set this large, missing bags, structural pieces, minifigures, substituted parts, instruction books, or even a box-only listing can change the value dramatically.",
    buyingChecks: ["Confirm set number 75192 rather than another Millennium Falcon set or a parts lot.", "Ask how completeness was verified and whether all minifigures, major assemblies, and loose parts are included.", "Treat ‘99% complete’ as incomplete unless you know exactly what is missing and replacement cost is acceptable.", "Decide separately how much you care about the box and instructions; neither proves that the bricks themselves are complete."],
    commonTraps: ["instruction books or boxes only", "small replacement-part lots", "incomplete sets missing major sections or minifigures"],
  },
];

export function getIndexedProduct(slug: string): IndexedProduct | undefined {
  return indexedProducts.find((product) => product.slug === slug);
}

function normalizedProductName(value?: string | null): string {
  return (value || "")
    .toLowerCase()
    .replace(/\bbody\b/g, "")
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

export function findIndexedCameraProduct(
  catalogProductLabel?: string | null,
  modelName?: string | null,
): IndexedProduct | undefined {
  const names = new Set(
    [catalogProductLabel, modelName]
      .map(normalizedProductName)
      .filter(Boolean),
  );
  if (!names.size) return undefined;
  return indexedProducts.find(
    (product) =>
      product.category === "cameras" &&
      [product.title, product.query].some((value) => names.has(normalizedProductName(value))),
  );
}

export function getBuyingGuideHref(category: IndexedProduct["category"]): string {
  const slugByCategory: Record<IndexedProduct["category"], string> = {
    cameras: "used-cameras",
    consoles: "used-game-consoles",
    gpus: "used-gpus",
    lego: "used-lego",
  };
  return `/buying-guides/${slugByCategory[category]}`;
}
