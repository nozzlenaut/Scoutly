export type ManualResource = {
  label: string;
  url: string;
  description: string;
  source: "official" | "third-party";
};

type ManualLookup = {
  query: string;
  category: string;
  productId?: string;
};

const exactProductResources: Record<string, ManualResource[]> = {
  "camera-sony-a7-iii-body": [
    {
      label: "Sony A7 III manuals",
      url: "https://www.sony.com/electronics/support/e-mount-body-ilce-7-series/ilce-7m3/manuals",
      description: "Official Sony manuals and warranty information for the ILCE-7M3.",
      source: "official",
    },
  ],
  "camera-canon-eos-5d-mark-iv-body": [
    {
      label: "Canon EOS 5D Mark IV support",
      url: "https://www.usa.canon.com/support/p/eos-5d-mark-iv",
      description: "Official Canon manuals, firmware, and support downloads.",
      source: "official",
    },
  ],
  "camera-nikon-d850-body": [
    {
      label: "Nikon D850 download center",
      url: "https://downloadcenter.nikonimglib.com/en/products/359/D850.html",
      description: "Official Nikon manuals, firmware, and reference downloads.",
      source: "official",
    },
  ],
};

const playStation5Ids = new Set([
  "console-playstation-5-disc-edition",
  "console-playstation-5-digital-edition",
  "console-playstation-5-slim-disc-edition",
  "console-playstation-5-slim-digital-edition",
  "console-playstation-5-pro-2tb",
]);

function manualsLibUrl(query: string): string {
  return `https://www.manualslib.com/search.html?q=${encodeURIComponent(query.trim())}`;
}

function extractLegoSetNumber(query: string, productId?: string): string | null {
  const fromQuery = query.match(/\b(\d{4,6})\b/);
  if (fromQuery) return fromQuery[1];
  const fromId = productId?.match(/lego-(\d{4,6})-/);
  return fromId?.[1] ?? null;
}

function genericOfficialResource(query: string, category: string): ManualResource | null {
  const normalized = query.toLowerCase();

  if (category === "cameras") {
    if (normalized.includes("canon")) {
      return {
        label: "Canon product support",
        url: "https://www.usa.canon.com/support",
        description: "Search Canon's official manuals, firmware, and support resources.",
        source: "official",
      };
    }
    if (normalized.includes("sony")) {
      return {
        label: "Sony camera support",
        url: "https://www.sony.com/electronics/support/cameras-camcorders",
        description: "Search Sony's official manuals, downloads, and support articles.",
        source: "official",
      };
    }
    if (normalized.includes("nikon")) {
      return {
        label: "Nikon download center",
        url: "https://downloadcenter.nikonimglib.com/en/index.html",
        description: "Search Nikon's official manual and firmware library.",
        source: "official",
      };
    }
    if (normalized.includes("fujifilm")) {
      return {
        label: "Fujifilm camera manuals",
        url: "https://fujifilm-dsc.com/en/manual/",
        description: "Browse official Fujifilm digital camera manuals.",
        source: "official",
      };
    }
    if (normalized.includes("panasonic") || normalized.includes("lumix")) {
      return {
        label: "Panasonic product support",
        url: "https://help.na.panasonic.com/",
        description: "Search Panasonic's official help and manual resources.",
        source: "official",
      };
    }
  }

  if (category === "consoles") {
    if (normalized.includes("playstation") || normalized.includes("ps5") || normalized.includes("ps4")) {
      return {
        label: "PlayStation manuals",
        url: "https://www.playstation.com/en-us/support/hardware/manuals/",
        description: "Official PlayStation console and accessory manuals.",
        source: "official",
      };
    }
    if (normalized.includes("xbox")) {
      return {
        label: "Xbox hardware support",
        url: "https://support.xbox.com/en-US/help/hardware-network/console",
        description: "Official Xbox setup, hardware, and troubleshooting guidance.",
        source: "official",
      };
    }
    if (normalized.includes("nintendo") || normalized.includes("switch")) {
      return {
        label: "Nintendo downloadable manuals",
        url: "https://en-americas-support.nintendo.com/app/answers/detail/a_id/16881/~/downloadable-manuals",
        description: "Official Nintendo manuals and system support resources.",
        source: "official",
      };
    }
  }

  if (category === "gpus") {
    if (normalized.includes("nvidia") || normalized.includes("geforce")) {
      return {
        label: "NVIDIA GeForce support",
        url: "https://www.nvidia.com/en-us/geforce/support/",
        description: "Official drivers, technical help, and product support.",
        source: "official",
      };
    }
    if (normalized.includes("amd") || normalized.includes("radeon")) {
      return {
        label: "AMD graphics support",
        url: "https://www.amd.com/en/support.html",
        description: "Official AMD drivers, documentation, and support resources.",
        source: "official",
      };
    }
  }

  if (category === "cpus") {
    if (normalized.includes("intel")) {
      return {
        label: "Intel product support",
        url: "https://www.intel.com/content/www/us/en/support.html",
        description: "Official Intel documentation, specifications, and support.",
        source: "official",
      };
    }
    if (normalized.includes("amd") || normalized.includes("ryzen")) {
      return {
        label: "AMD processor support",
        url: "https://www.amd.com/en/support.html",
        description: "Official AMD documentation, specifications, and support.",
        source: "official",
      };
    }
  }

  return null;
}

export function getManualResources({
  query,
  category,
  productId,
}: ManualLookup): ManualResource[] {
  if (!query.trim() || category === "books") return [];

  const resources: ManualResource[] = [
    ...(productId ? exactProductResources[productId] ?? [] : []),
  ];

  if (productId && playStation5Ids.has(productId)) {
    resources.push({
      label: "PlayStation 5 manuals",
      url: "https://www.playstation.com/en-us/support/hardware/manuals/",
      description: "Official PS5 instruction manuals and safety guides by model.",
      source: "official",
    });
  }

  if (category === "lego") {
    const setNumber = extractLegoSetNumber(query, productId);
    if (setNumber) {
      resources.push({
        label: `LEGO ${setNumber} building instructions`,
        url: `https://www.lego.com/en-us/service/building-instructions/${setNumber}`,
        description: "Official downloadable LEGO building instructions.",
        source: "official",
      });
    }
  }

  const hasExactProductResource = resources.length > 0;
  if (!hasExactProductResource) {
    const generic = genericOfficialResource(query, category);
    if (generic) resources.push(generic);

    resources.push({
      label: "Search ManualsLib",
      url: manualsLibUrl(query),
      description: `Search ManualsLib for “${query}”. Verify the exact model before using a manual.`,
      source: "third-party",
    });
  }

  return resources;
}
