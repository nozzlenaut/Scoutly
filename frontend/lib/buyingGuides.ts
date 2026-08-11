export type GuideTable = {
  headers: string[];
  rows: string[][];
};

export type GuideSection = {
  title: string;
  paragraphs?: string[];
  bullets?: string[];
  table?: GuideTable;
  note?: string;
};

export type GuideSource = {
  label: string;
  organization: string;
  url: string;
  note: string;
};

export type BuyingGuide = {
  slug: string;
  categoryId: string;
  categoryLabel: string;
  eyebrow: string;
  title: string;
  description: string;
  intro: string[];
  categoryHref: string;
  categoryLinkLabel: string;
  sections: GuideSection[];
  sources: GuideSource[];
  relatedSlugs: string[];
};

export const buyingGuides: BuyingGuide[] = [
  {
    slug: "used-cameras",
    categoryId: "cameras",
    categoryLabel: "Cameras",
    eyebrow: "Used camera buying guide",
    title: "Buying a used camera: what actually matters",
    description:
      "A practical used-camera guide to shutter count, cosmetic wear, meaningful damage, battery condition, and vague listing language.",
    intro: [
      "Used cameras can look rough and still have years of life left. They can also look almost new and have a problem buried three paragraphs into the listing.",
      "The trick is figuring out which is which. A scratched corner may mean almost nothing. A damaged sensor, corroded battery compartment, bent mount, or flaky control is a different story.",
    ],
    categoryHref: "/cameras",
    categoryLinkLabel: "Browse used cameras",
    sections: [
      {
        title: "Start with the exact model",
        paragraphs: [
          "Before worrying about condition, make sure the listing is actually for the camera you want. Camera names can be annoyingly similar, and a small suffix or generation change can mean a different body.",
          "Check the full model name and the photos instead of trusting the first few words of the title.",
        ],
      },
      {
        title: "How much shutter count is too much?",
        paragraphs: [
          "There is not one magic number. Mechanical shutters wear, but manufacturer test figures vary quite a bit by model.",
          "Nikon publishes tested figures ranging from 100,000 cycles on some models to 400,000 on some professional bodies. Sony has published about 200,000 cycles for the APS-C α6500 and more than 500,000 for the full-frame α7R III. That is exactly why a blanket rule like “100,000 is bad” does not hold up.",
          "Treat a manufacturer figure as context, not an expiration date. Nikon explicitly notes that the actual number of cycles can be higher or lower than its test estimate.",
        ],
        table: {
          headers: ["Example", "Manufacturer test figure"],
          rows: [
            ["Nikon Z50 / Z30 / Z fc", "100,000 cycles"],
            ["Nikon D750 / D780 / D7500", "150,000 cycles"],
            ["Nikon Z6 / Z7 / D850", "200,000 cycles"],
            ["Sony α6500", "About 200,000 cycles"],
            ["Nikon D4 / D5 / D6", "400,000 cycles"],
            ["Sony α7R III", "More than 500,000 cycles"],
          ],
        },
        note:
          "These are durability-test figures, not guarantees. Check the exact model whenever possible.",
      },
      {
        title: "Cosmetic damage that usually does not bother us much",
        paragraphs: [
          "Paint wear, rubbed corners, a shiny grip, and small scratches on the body are normal used-camera stuff. They should affect the price, but they do not automatically mean the camera is unhealthy.",
          "A scratch on the rear LCD may be annoying without affecting the photo at all. A cracked display, dead section, or broken touch function is different.",
        ],
      },
      {
        title: "Damage worth taking seriously",
        bullets: [
          "Sensor damage: dust is common and cleanable; a scratch or mark that will not clean off deserves a lot more caution.",
          "Lens mount damage: normal rub marks are fine. Bent metal, looseness, missing screws, or obvious impact damage are not cosmetic.",
          "Corrosion or liquid exposure: check the battery compartment, card slot, hot shoe, and ports.",
          "Intermittent controls: a dial that “sometimes skips” or a card slot that “usually works” is still a defect.",
          "Major cracks or dents: especially around the mount, tripod socket, battery door, or controls.",
        ],
      },
      {
        title: "Used batteries: old is normal, damaged is not",
        paragraphs: [
          "Battery capacity drops with age and use, so an older battery lasting less time than a new one is not surprising.",
          "A swollen, leaking, cracked, deformed, or abnormally hot lithium-ion battery is a different issue. Do not count a questionable battery as a useful part of the deal. Replacing a battery is cheap compared with replacing the camera.",
        ],
      },
      {
        title: "Listing phrases worth slowing down for",
        bullets: [
          "“Untested” means untested. It does not mean probably works.",
          "“Powers on” proves exactly one thing: it powers on.",
          "“READ” or “see description” is not automatically bad, but actually read the description. That is often where the important bit lives.",
          "“As-is” means you should price the uncertainty as part of the purchase.",
        ],
      },
      {
        title: "Before you buy",
        bullets: [
          "Confirm the exact model.",
          "Check shutter count when it is available and useful for that model.",
          "Look at sensor and lens-mount condition.",
          "Check the battery compartment and card slot.",
          "Confirm autofocus, shutter, screen, viewfinder, buttons, and dials work.",
          "Check what battery, charger, and other useful accessories are actually included.",
        ],
        note:
          "Do not overthink a scuffed corner while ignoring a real functional problem. A scratched camera that works properly is usually a better buy than a spotless mystery camera.",
      },
    ],
    sources: [
      {
        label: "How many pictures has my camera taken? How many will it take?",
        organization: "Nikon Support",
        url: "https://www.nikonimgsupport.com/eu/BV_article?articleNo=000044853&ctry=IL&lang=en_GB&setRedirect=true",
        note: "Model-specific shutter test figures and Nikon's qualification that actual life can be higher or lower.",
      },
      {
        label: "α6500 specifications",
        organization: "Sony",
        url: "https://www.sony.com/lr/electronics/interchangeable-lens-cameras/ilce-6500-body-kit/specifications",
        note: "Sony's approximately 200,000-cycle shutter durability test.",
      },
      {
        label: "α7R III product information",
        organization: "Sony",
        url: "https://www.sony.com/en-bh/electronics/interchangeable-lens-cameras/ilce-7rm3",
        note: "Sony's more-than-500,000-cycle shutter durability test.",
      },
      {
        label: "Frequent questions on lithium-ion batteries",
        organization: "U.S. EPA",
        url: "https://www.epa.gov/recycle/frequent-questions-lithium-ion-batteries",
        note: "Damaged and swollen lithium-ion battery safety and disposal guidance.",
      },
    ],
    relatedSlugs: ["used-lenses", "used-game-consoles"],
  },
  {
    slug: "used-lenses",
    categoryId: "lenses",
    categoryLabel: "Lenses",
    eyebrow: "Used lens buying guide",
    title: "Buying a used lens: fungus, haze, dust, and what actually matters",
    description:
      "What to check on a used camera lens, including fungus, haze, dust, scratches, autofocus, stabilization, and mount condition.",
    intro: [
      "Used lenses are a little different from camera bodies. There is no shutter count to glance at.",
      "A lens can look beat up outside and work perfectly. It can also look spotless and have fungus or haze inside. The glass and mechanics matter more than whether the barrel has a few scars.",
    ],
    categoryHref: "/lenses",
    categoryLinkLabel: "Browse used lenses",
    sections: [
      {
        title: "A little internal dust is not the same thing as fungus",
        paragraphs: [
          "A few tiny dust particles inside a used lens are common. That is very different from web-like fungal growth.",
          "Sony describes lens fungus as growth that can develop when moisture and dust containing spores are present inside a lens, and warns that it can reduce optical performance. If a listing says fungus, do not translate that in your head to “just needs a wipe.”",
        ],
      },
      {
        title: "Haze is annoyingly vague",
        paragraphs: [
          "“Haze” can cover several kinds of internal optical contamination or aging. It is not a precise diagnosis.",
          "If a seller mentions haze, I would want clear photos through the lens and, for an expensive lens, sample images. The effect can range from barely noticeable to obvious loss of contrast depending on what is actually going on.",
        ],
      },
      {
        title: "Scratches are not all equal",
        paragraphs: [
          "A tiny front-element mark may have little visible effect in normal photos. A deep scratch, damaged coating, or rear-element damage deserves more attention.",
          "There is no honest universal rule where a scratch of a certain size is always fine. Location, depth, aperture, lighting, and the lens design all matter.",
        ],
      },
      {
        title: "Check the mechanics",
        bullets: [
          "Mount: look for bent metal, loose screws, damaged contacts, cracks, or impact damage.",
          "Autofocus: make sure it actually focuses. Grinding, repeated failure, or an AF error is a defect, even if manual focus works.",
          "Stabilization: if the lens has it, check that it engages normally without errors or obviously abnormal behavior.",
          "Zoom and focus rings: some resistance is normal on some lenses; grinding, sticking, huge dead spots, or serious wobble is worth investigating.",
          "Aperture: confirm it stops down and returns normally when the camera commands it.",
        ],
      },
      {
        title: "Cosmetic wear",
        paragraphs: [
          "Paint wear, scuffs, and faded lettering do not bother me much on a lens I plan to use.",
          "Cracks, a bent filter ring from an impact, or a mount that no longer sits correctly are a different conversation.",
        ],
      },
      {
        title: "Before you buy",
        bullets: [
          "Confirm the exact lens and correct mount.",
          "Inspect front and rear glass.",
          "Ask specifically about fungus and haze.",
          "Check autofocus, stabilization, focus ring, zoom ring, and aperture.",
          "Check mount and electronic contacts.",
          "Treat caps, hood, case, and box as nice extras rather than proof of condition.",
        ],
      },
    ],
    sources: [
      {
        label: "What is lens fungus and will it damage my camera lens?",
        organization: "Sony Support",
        url: "https://www.sony.com/electronics/support/articles/00062800",
        note: "Fungus causes, appearance, performance risk, and inspection guidance.",
      },
      {
        label: "How should interchangeable lens cameras be stored?",
        organization: "Sony Support",
        url: "https://www.sony.com/electronics/support/lenses-e-mount-lenses/selp1650/articles/00160168",
        note: "Dust and humidity guidance for cameras and lenses.",
      },
      {
        label: "Lens maintenance guidance",
        organization: "Tamron",
        url: "https://www.tamron.com/global/consumer/support/help/maintenance/",
        note: "Manufacturer guidance on lens moisture, condensation, cleaning, and storage.",
      },
    ],
    relatedSlugs: ["used-cameras"],
  },
  {
    slug: "used-gpus",
    categoryId: "gpus",
    categoryLabel: "GPUs",
    eyebrow: "Used GPU buying guide",
    title: "Buying a used GPU: what to check before you buy",
    description:
      "A practical used-graphics-card guide to exact model, VRAM, power requirements, prior workload, physical condition, and testing.",
    intro: [
      "Used GPUs can be an excellent deal, but model names alone do not tell the whole story.",
      "The same GPU family can show up with different VRAM amounts, coolers, physical dimensions, outputs, and power requirements. Start by making sure the card is actually the one you think it is.",
    ],
    categoryHref: "/search?category=gpus&q=",
    categoryLinkLabel: "Search used GPUs",
    sections: [
      {
        title: "Confirm the exact card",
        bullets: [
          "GPU model and generation.",
          "VRAM capacity.",
          "Board manufacturer and specific model when possible.",
          "Physical length and slot thickness.",
          "Power connectors.",
          "Video outputs.",
        ],
        note:
          "Manufacturer specs matter here. NVIDIA's own comparison tables show different power, connector, thermal, and size requirements even across nearby models.",
      },
      {
        title: "Make sure it fits your PC",
        paragraphs: [
          "Check case clearance, slot thickness, power-supply capacity, and the exact connectors your card needs.",
          "Do not assume a card fits because another GPU with the same chip fit. Partner-board dimensions can vary.",
        ],
      },
      {
        title: "Mining history is not a magic condition test",
        paragraphs: [
          "A card having mined cryptocurrency does not tell you its current condition by itself. A gaming card is not automatically healthy either.",
          "Previous workload, cooling, age, fan wear, voltage settings, storage, and maintenance all matter, and a marketplace listing usually cannot give you a trustworthy remaining-life number. I would rather see the actual card tested than argue about the word “mining.”",
        ],
      },
      {
        title: "Ask to see it running",
        bullets: [
          "Clean video output.",
          "Correct GPU and VRAM reported by the system.",
          "A game or benchmark running without crashes.",
          "No obvious visual artifacts.",
          "Fans operating normally.",
          "Temperatures that make sense for that exact model under the test being shown.",
        ],
      },
      {
        title: "Look at the physical card",
        bullets: [
          "Burned or discolored power connectors.",
          "Bent PCB.",
          "Corrosion.",
          "Broken fan blades.",
          "Damaged PCIe edge connector.",
          "Missing components or obviously sloppy repair work.",
        ],
        note:
          "Dust can be cleaned. Physical or electrical damage is a different problem.",
      },
      {
        title: "There is no single good GPU temperature",
        paragraphs: [
          "Different GPUs have different thermal limits, power targets, coolers, fan curves, and hotspot behavior.",
          "Compare a card with normal behavior for that exact model. A random temperature number from a different GPU is not much help.",
        ],
      },
    ],
    sources: [
      {
        label: "GeForce graphics card comparison",
        organization: "NVIDIA",
        url: "https://www.nvidia.com/en-us/geforce/graphics-cards/compare/?section=compare-specs",
        note: "Official card dimensions, thermal limits, power requirements, and connector specifications.",
      },
      {
        label: "Graphics specifications",
        organization: "AMD",
        url: "https://www.amd.com/en/products/specifications/graphics.html",
        note: "Official AMD graphics specifications for checking model, memory, power, and platform details.",
      },
      {
        label: "Should you buy a used graphics card?",
        organization: "Tom's Hardware",
        url: "https://www.tomshardware.com/pc-components/gpus/should-you-buy-a-used-graphics-card",
        note: "Practical used-GPU testing and prior-workload caveats. Used as secondary buying guidance, not as a manufacturer specification.",
      },
    ],
    relatedSlugs: ["used-ram", "used-cpus"],
  },
  {
    slug: "used-ram",
    categoryId: "ram",
    categoryLabel: "RAM",
    eyebrow: "Used RAM buying guide",
    title: "Buying RAM: compatibility matters more than cosmetic condition",
    description:
      "Check DDR generation, DIMM type, capacity, speed, ECC, and platform compatibility before buying used RAM.",
    intro: [
      "RAM is one of the less dramatic things to buy used, which is honestly nice.",
      "The bigger risk is usually not hidden wear. It is buying perfectly good memory that your computer cannot use.",
    ],
    categoryHref: "/search?category=ram&q=",
    categoryLinkLabel: "Build a RAM search",
    sections: [
      {
        title: "Start with DDR generation",
        paragraphs: [
          "DDR3, DDR4, and DDR5 are different standards. They are not interchangeable just because they are all called RAM.",
          "Crucial explicitly notes that memory is not forward or backward compatible across DDR generations.",
        ],
      },
      {
        title: "Desktop or laptop memory?",
        paragraphs: [
          "Desktop systems generally use DIMMs. Laptops with replaceable memory generally use smaller SO-DIMMs.",
          "Do not buy from a listing that only says something vague like “16GB DDR4” without checking the actual module type and part number.",
        ],
      },
      {
        title: "Capacity and kit layout matter",
        paragraphs: [
          "“32GB RAM” might mean one 32GB module or two 16GB modules. That matters for available slots and how you want the memory configured.",
          "Matched kits are the easy option when starting fresh, but mixed modules can work in many systems. There is no universal guarantee. The motherboard, CPU, BIOS, memory ranks, and profiles all get a vote.",
        ],
      },
      {
        title: "What if the speeds do not match?",
        paragraphs: [
          "Compatible memory within the same DDR generation can often run at a lower common speed. Crucial notes that systems generally operate based on the slowest installed compatible module.",
          "That does not mean every random combination will be stable, and advertised XMP or EXPO speeds depend on the complete platform.",
        ],
      },
      {
        title: "ECC, registered, and unbuffered are not interchangeable labels",
        paragraphs: [
          "Server and workstation memory introduces more ways to buy the wrong thing. Check whether your platform needs ECC or non-ECC and registered or unbuffered memory.",
          "If you do not already know that your machine accepts registered ECC memory, do not assume a cheap server kit is a clever desktop upgrade.",
        ],
      },
      {
        title: "Used RAM condition",
        bullets: [
          "Avoid broken PCBs, damaged contacts, corrosion, missing components, or burn damage.",
          "Normal insertion marks on the contacts are not interesting by themselves.",
          "After installation, run a proper memory diagnostic. Passing a test is useful evidence that the current configuration is stable, not a lifetime guarantee.",
        ],
      },
    ],
    sources: [
      {
        label: "DDR memory speeds and compatibility",
        organization: "Crucial",
        url: "https://www.crucial.com/support/memory-speeds-compatability",
        note: "DDR-generation compatibility and mixed-speed behavior.",
      },
      {
        label: "Desktop and laptop memory",
        organization: "Kingston",
        url: "https://www.kingston.com/en/memory/desktop-laptop",
        note: "DIMM/SO-DIMM form factors and memory compatibility guidance.",
      },
      {
        label: "Memory resources",
        organization: "Kingston",
        url: "https://www.kingston.com/en/memory",
        note: "ECC, non-ECC, registered, unbuffered, and platform-oriented memory information.",
      },
    ],
    relatedSlugs: ["used-cpus", "used-gpus"],
  },
  {
    slug: "used-cpus",
    categoryId: "cpus",
    categoryLabel: "CPUs",
    eyebrow: "Used CPU buying guide",
    title: "Buying a used CPU: socket alone is not enough",
    description:
      "Check exact CPU model, socket, chipset, BIOS support, memory platform, pins or contacts, and seller testing before buying used.",
    intro: [
      "Used CPUs can be great upgrades because processors do not have fans or other obvious wear items built into the package.",
      "The annoying part is compatibility. Two processors can physically use the same socket and still not work with the same motherboard or BIOS.",
    ],
    categoryHref: "/search?category=cpus&q=",
    categoryLinkLabel: "Build a CPU search",
    sections: [
      {
        title: "Confirm the exact CPU",
        bullets: [
          "Full model name and suffix.",
          "Socket.",
          "Generation.",
          "Integrated-graphics status if that matters to your build.",
          "Supported memory generation.",
        ],
      },
      {
        title: "Socket alone does not prove compatibility",
        paragraphs: [
          "Intel documents processor generations that share a socket but require specific chipset families. AMD likewise publishes chipset compatibility tables, and some supported combinations still require a BIOS update.",
          "The safest check is the motherboard manufacturer's CPU-support list for your exact board and BIOS revision.",
        ],
      },
      {
        title: "Inspect the contacts or pins",
        paragraphs: [
          "Depending on the platform, pins may be on the CPU or in the motherboard socket.",
          "For a used processor, look for bent or missing pins where applicable, damaged contact pads, corrosion, cracked substrate, or obvious burn marks. A little old thermal-paste residue is much less interesting than physical damage.",
        ],
      },
      {
        title: "Ask what was actually tested",
        paragraphs: [
          "“Pulled from working system” is useful context, but a current boot or stress-test screenshot is better.",
          "If the seller cannot test it, that uncertainty should be part of the price rather than something you pretend is not there.",
        ],
      },
      {
        title: "OEM and tray chips can be fine",
        paragraphs: [
          "A processor does not need a retail box to work. What matters is that the exact part is genuine, compatible, physically sound, and functioning.",
          "Warranty coverage and included cooler can vary by how the chip was originally sold, so check those separately if they matter to you.",
        ],
      },
    ],
    sources: [
      {
        label: "Compatibility of 13th Generation Intel Desktop Processors",
        organization: "Intel Support",
        url: "https://www.intel.com/content/www/us/en/support/articles/000092293/processors.html",
        note: "Example of socket, chipset, generation, and memory compatibility limits.",
      },
      {
        label: "AMD Socket AM4 chipsets",
        organization: "AMD",
        url: "https://www.amd.com/en/products/processors/chipsets/am4.html",
        note: "Official CPU/chipset compatibility table and BIOS qualifications.",
      },
      {
        label: "AMD Socket AM5 chipsets",
        organization: "AMD",
        url: "https://www.amd.com/en/products/processors/chipsets/am5.html",
        note: "Official AM5 platform and BIOS compatibility guidance.",
      },
    ],
    relatedSlugs: ["used-ram", "used-gpus"],
  },
  {
    slug: "used-game-consoles",
    categoryId: "consoles",
    categoryLabel: "Consoles",
    eyebrow: "Used console buying guide",
    title: "Buying a used game console: check the exact version first",
    description:
      "Check model revision, disc drive, HDMI, controllers, storage, battery condition, and online access before buying a used console.",
    intro: [
      "Used consoles are usually pretty straightforward. Listings are not always.",
      "A seller says “Nintendo Switch” and the photos show a Switch Lite. Another says “Series X” without making the disc-drive version clear. Start by identifying exactly what is being sold.",
    ],
    categoryHref: "/search?category=consoles&q=",
    categoryLinkLabel: "Search used consoles",
    sections: [
      {
        title: "Make sure it is the exact console",
        paragraphs: [
          "Model numbers are useful when names get sloppy. Nintendo, for example, identifies Switch 2 as BEE-001, the original Switch family as HAC-001, Switch OLED as HEG-001, and Switch Lite as HDH-001.",
          "Storage capacity and hardware revision can matter too. Do not rely on a broad title when the photos or model label can answer the question.",
        ],
      },
      {
        title: "Does it actually have a disc drive?",
        paragraphs: [
          "Xbox Series X has been sold in disc and all-digital configurations, while Series S is all-digital. PS5 hardware has also been sold in disc and digital configurations.",
          "Sony's detachable PS5 disc drive only works with specified newer model groups. If physical games matter to you, confirm the exact hardware before buying.",
        ],
      },
      {
        title: "Test the boring stuff",
        bullets: [
          "Stable HDMI output.",
          "Disc drive reads and ejects if present.",
          "USB ports.",
          "Wi-Fi and network connection.",
          "Storage capacity.",
          "Power supply and required cables.",
          "Controller sticks, buttons, triggers, charging, and wireless connection.",
        ],
      },
      {
        title: "Handheld battery condition",
        paragraphs: [
          "Reduced battery life with age is normal. Swelling, deformation, overheating, or a damaged battery is not normal wear.",
          "For handheld systems, battery condition should affect the price even when the console otherwise works.",
        ],
      },
      {
        title: "Online access is worth checking",
        paragraphs: [
          "For a console with a weird modification history or an expensive used purchase, confirm that it can connect to the platform's online services normally.",
          "Do not assume a factory reset fixes every possible account, service, or console-level restriction.",
        ],
      },
    ],
    sources: [
      {
        label: "Where can I find my system serial number?",
        organization: "Nintendo Support",
        url: "https://en-americas-support.nintendo.com/app/answers/detail/a_id/58879/p/1095/c/190",
        note: "Official Switch-family model identifiers.",
      },
      {
        label: "Compare Xbox Series X and Series S",
        organization: "Xbox",
        url: "https://www.xbox.com/en-US/consoles/compare",
        note: "Current disc, all-digital, storage, port, and hardware configuration differences.",
      },
      {
        label: "Set up a disc drive for PS5 consoles",
        organization: "PlayStation Support",
        url: "https://www.playstation.com/en-us/support/hardware/ps5-disc-drive-set-up/",
        note: "PS5 detachable-disc-drive compatibility by model group.",
      },
    ],
    relatedSlugs: ["used-gpus"],
  },
  {
    slug: "used-books",
    categoryId: "books",
    categoryLabel: "Books",
    eyebrow: "Used book buying guide",
    title: "Buying a used book: edition first, condition second",
    description:
      "Use ISBNs to match the right edition and understand used-book condition, ex-library copies, annotations, water damage, and dust jackets.",
    intro: [
      "Used books are probably the simplest category on PriceSift, right up until you buy the wrong edition.",
      "If the exact version matters, identify it first. Then decide how much condition actually matters for what you plan to do with the book.",
    ],
    categoryHref: "/search?category=books&q=",
    categoryLinkLabel: "Search by ISBN",
    sections: [
      {
        title: "Use the ISBN when the exact edition matters",
        paragraphs: [
          "The International ISBN Agency says the publication element identifies a particular edition and format of a title, and different formats or editions need separate ISBNs.",
          "That makes ISBN much safer than title-only searching when you need a particular textbook edition, translation, hardcover, or other specific version.",
        ],
      },
      {
        title: "Condition words help, but read the description",
        paragraphs: [
          "Used-book grades such as Fine, Very Good, Good, Fair, and Poor are useful shorthand, but sellers can vary at the edges.",
          "Both AbeBooks and Biblio tell buyers to pay attention to the detailed description and disclosed defects, not just the grade.",
        ],
      },
      {
        title: "Ex-library does not automatically mean bad",
        paragraphs: [
          "An ex-library copy may have stamps, labels, protective covering, or other library markings.",
          "For a book you just want to read, that can be perfectly fine. For a collectible copy, those markings may matter a lot more. Your goal changes the answer.",
        ],
      },
      {
        title: "Writing, water damage, and missing jackets",
        bullets: [
          "Highlighting or notes might be irrelevant for a cheap reading copy and a deal breaker for a collectible one.",
          "Water staining can be cosmetic or come with warping, odor, or more serious damage. Read the actual description.",
          "A missing dust jacket may mean very little for a reading copy and quite a lot for a collectible hardcover.",
          "Missing text pages are different. A readable used book and an incomplete book are not the same thing.",
        ],
      },
      {
        title: "Textbooks need one extra check",
        paragraphs: [
          "Do not assume a used textbook includes a valid access code, online subscription, workbook, disc, or other supplement unless the seller explicitly says it does.",
        ],
      },
    ],
    sources: [
      {
        label: "What is an ISBN?",
        organization: "International ISBN Agency",
        url: "https://www.isbn-international.org/index.php/content/what-isbn/10",
        note: "How ISBN identifies a specific edition and format.",
      },
      {
        label: "A guide to used book conditions",
        organization: "AbeBooks",
        url: "https://www.abebooks.com/books/rarebooks/collecting-guide/understanding-rare-books/guide-book-conditions.shtml",
        note: "Used-book condition vocabulary, ex-library markings, and seller-description guidance.",
      },
      {
        label: "Guide to Biblio's book conditions",
        organization: "Biblio",
        url: "https://help.biblio.com/en/support/solutions/articles/70000635394-guide-to-biblio-s-book-conditions",
        note: "Independent used-book condition definitions and defect guidance.",
      },
    ],
    relatedSlugs: ["used-lego"],
  },
  {
    slug: "used-lego",
    categoryId: "lego",
    categoryLabel: "LEGO",
    eyebrow: "Used LEGO buying guide",
    title: "Buying used LEGO: complete means more than “the build looks finished”",
    description:
      "Check set number, completeness, minifigures, replacement pieces, instructions, stickers, and box value before buying used LEGO.",
    intro: [
      "Used LEGO can be a great deal.",
      "It can also turn into “99% complete” followed by three evenings figuring out which 1% is missing. The important question is not just how many pieces are gone. It is which pieces are gone.",
    ],
    categoryHref: "/search?category=lego&q=",
    categoryLinkLabel: "Search used LEGO",
    sections: [
      {
        title: "Start with the set number",
        paragraphs: [
          "Names get abbreviated and reused. Set numbers are much harder to argue with.",
          "LEGO itself uses the set name or number when locating replacement pieces and building instructions, so confirm that number before comparing listings.",
        ],
      },
      {
        title: "“Complete build” is not necessarily a complete set",
        paragraphs: [
          "A seller may have every piece needed for the main model while still missing minifigures, alternate-build parts, accessories, or other original contents.",
          "If completeness matters, ask what the seller means rather than assuming everyone uses the word the same way.",
        ],
      },
      {
        title: "Missing pieces are not all equally annoying",
        paragraphs: [
          "LEGO sells individual pieces through its parts service, so common missing bricks can sometimes be easy to replace.",
          "Rare printed pieces, retired elements, unusual colors, stickers, and minifigure parts can be a different story. “Only five pieces missing” tells you almost nothing without knowing which five.",
        ],
      },
      {
        title: "Instructions and box",
        paragraphs: [
          "LEGO provides free downloadable instructions for thousands of sets, so missing paper instructions are often not a problem for somebody who just wants to build.",
          "Original instructions and packaging can matter more to collectors. That is a value question, not a requirement for the bricks to work.",
        ],
      },
      {
        title: "Check actual piece condition",
        bullets: [
          "Cracked pieces or clips.",
          "Heavy discoloration.",
          "Marker, paint, or bite marks.",
          "Damaged or badly placed stickers.",
          "Loose hinges.",
          "Smoke or odor claims only if the seller can actually speak to the set's history.",
        ],
      },
      {
        title: "Our preferred translation of “99% complete”",
        paragraphs: [
          "Not complete.",
          "That does not make it a bad deal. It just means the missing inventory belongs in the price calculation.",
        ],
      },
    ],
    sources: [
      {
        label: "Replacement pieces",
        organization: "LEGO",
        url: "https://www.lego.com/en-us/service/replacement-parts",
        note: "Official missing, broken, and purchasable-parts options.",
      },
      {
        label: "Replace missing or damaged building instructions",
        organization: "LEGO",
        url: "https://www.lego.com/en-us/service/help/DUPLO/replace-missing-or-damaged-building-instructions-kA009000001dbm1CAA",
        note: "Official free downloadable building-instruction guidance.",
      },
      {
        label: "Catalog inventories",
        organization: "BrickLink",
        url: "https://www.bricklink.com/catalogInv.asp",
        note: "Detailed secondary-market set inventories used to check pieces and minifigures.",
      },
    ],
    relatedSlugs: ["used-books"],
  },
];

export const buyingGuideSlugs = buyingGuides.map((guide) => guide.slug);

export function getBuyingGuide(slug: string) {
  return buyingGuides.find((guide) => guide.slug === slug) ?? null;
}

export function getBuyingGuideForCategory(categoryId: string) {
  return buyingGuides.find((guide) => guide.categoryId === categoryId) ?? null;
}
