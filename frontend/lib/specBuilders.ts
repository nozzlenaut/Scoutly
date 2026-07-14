export type SpecOption = {
  id: string;
  label: string;
};

export type RamBuilderSelection = {
  formFactor: "desktop" | "laptop" | "";
  generation: "ddr3" | "ddr4" | "ddr5" | "";
  totalCapacity: string;
  configuration: string;
  speed: string;
  brand: string;
};

export const emptyRamSelection: RamBuilderSelection = {
  formFactor: "",
  generation: "",
  totalCapacity: "",
  configuration: "",
  speed: "",
  brand: "",
};

export const ramFormFactors: SpecOption[] = [
  { id: "desktop", label: "Desktop" },
  { id: "laptop", label: "Laptop" },
];

export const ramGenerations: SpecOption[] = [
  { id: "ddr3", label: "DDR3" },
  { id: "ddr4", label: "DDR4" },
  { id: "ddr5", label: "DDR5" },
];

const capacityMap: Record<string, number[]> = {
  "desktop:ddr3": [8, 16, 32, 64],
  "laptop:ddr3": [8, 16, 32],
  "desktop:ddr4": [8, 16, 32, 64, 128],
  "laptop:ddr4": [8, 16, 32, 64],
  "desktop:ddr5": [16, 32, 48, 64, 96, 128],
  "laptop:ddr5": [16, 32, 48, 64, 96],
};

const configurationMap: Record<string, string[]> = {
  "desktop:ddr3:8": ["2x4", "1x8"],
  "desktop:ddr3:16": ["2x8", "4x4", "1x16"],
  "desktop:ddr3:32": ["4x8", "2x16"],
  "desktop:ddr3:64": ["4x16"],
  "laptop:ddr3:8": ["2x4", "1x8"],
  "laptop:ddr3:16": ["2x8", "1x16"],
  "laptop:ddr3:32": ["2x16"],

  "desktop:ddr4:8": ["1x8", "2x4"],
  "desktop:ddr4:16": ["2x8", "1x16", "4x4"],
  "desktop:ddr4:32": ["2x16", "4x8", "1x32"],
  "desktop:ddr4:64": ["2x32", "4x16"],
  "desktop:ddr4:128": ["4x32"],
  "laptop:ddr4:8": ["1x8", "2x4"],
  "laptop:ddr4:16": ["2x8", "1x16"],
  "laptop:ddr4:32": ["2x16", "1x32"],
  "laptop:ddr4:64": ["2x32"],

  "desktop:ddr5:16": ["1x16"],
  "desktop:ddr5:32": ["2x16", "1x32"],
  "desktop:ddr5:48": ["2x24"],
  "desktop:ddr5:64": ["2x32", "4x16"],
  "desktop:ddr5:96": ["2x48"],
  "desktop:ddr5:128": ["2x64", "4x32"],
  "laptop:ddr5:16": ["1x16"],
  "laptop:ddr5:32": ["2x16", "1x32"],
  "laptop:ddr5:48": ["2x24"],
  "laptop:ddr5:64": ["2x32"],
  "laptop:ddr5:96": ["2x48"],
};

const speedMap: Record<string, number[]> = {
  ddr3: [1066, 1333, 1600, 1866, 2133],
  ddr4: [2133, 2400, 2666, 2933, 3000, 3200, 3600, 4000],
  ddr5: [4800, 5200, 5600, 6000, 6400, 6800, 7200, 7600, 8000],
};

export const ramBrands: SpecOption[] = [
  { id: "", label: "Any brand" },
  { id: "Corsair", label: "Corsair" },
  { id: "G.Skill", label: "G.Skill" },
  { id: "Kingston", label: "Kingston" },
  { id: "Crucial", label: "Crucial" },
  { id: "TeamGroup", label: "TeamGroup" },
  { id: "Samsung", label: "Samsung" },
  { id: "SK Hynix", label: "SK Hynix" },
  { id: "Micron", label: "Micron" },
  { id: "Patriot", label: "Patriot" },
  { id: "ADATA", label: "ADATA / XPG" },
];

export function ramCapacityOptions(
  selection: RamBuilderSelection,
): SpecOption[] {
  if (!selection.formFactor || !selection.generation) return [];
  const values =
    capacityMap[`${selection.formFactor}:${selection.generation}`] || [];
  return values.map((value) => ({
    id: String(value),
    label: `${value}GB total`,
  }));
}

export function ramConfigurationOptions(
  selection: RamBuilderSelection,
): SpecOption[] {
  if (
    !selection.formFactor ||
    !selection.generation ||
    !selection.totalCapacity
  )
    return [];
  const values =
    configurationMap[
      `${selection.formFactor}:${selection.generation}:${selection.totalCapacity}`
    ] || [];
  return values.map((value) => {
    const [count, capacity] = value.split("x");
    return { id: value, label: `${count} × ${capacity}GB` };
  });
}

export function ramSpeedOptions(selection: RamBuilderSelection): SpecOption[] {
  if (!selection.generation) return [];
  return [
    { id: "", label: "Any speed" },
    ...(speedMap[selection.generation] || []).map((value) => ({
      id: String(value),
      label: `${value} MT/s`,
    })),
  ];
}

export function ramSelectionIsComplete(
  selection: RamBuilderSelection,
): boolean {
  return Boolean(
    selection.formFactor &&
      selection.generation &&
      selection.totalCapacity &&
      selection.configuration,
  );
}

export function buildRamQuery(selection: RamBuilderSelection): string | null {
  if (!ramSelectionIsComplete(selection)) return null;
  const parts = [
    selection.generation.toUpperCase(),
    selection.formFactor === "desktop" ? "Desktop" : "Laptop",
    `${selection.totalCapacity}GB`,
    `${selection.configuration}GB`,
  ];
  if (selection.speed) parts.push(`${selection.speed} MT/s`);
  if (selection.brand) parts.push(selection.brand);
  return parts.join(" ");
}

export function parseRamQuery(query?: string | null): RamBuilderSelection {
  if (!query) return { ...emptyRamSelection };
  const lower = query.toLowerCase();
  const generation = (
    lower.match(/\bddr\s*([345])\b/)?.[1]
      ? `ddr${lower.match(/\bddr\s*([345])\b/)?.[1]}`
      : ""
  ) as RamBuilderSelection["generation"];
  const formFactor: RamBuilderSelection["formFactor"] =
    /\b(laptop|notebook|so-?dimm)\b/.test(lower)
      ? "laptop"
      : /\b(desktop|u-?dimm)\b/.test(lower)
        ? "desktop"
        : "";
  const config = lower.match(/\b(\d+)\s*[x×]\s*(\d+)\s*gb\b/);
  const configuration = config ? `${config[1]}x${config[2]}` : "";
  const totalCapacity = config
    ? String(Number(config[1]) * Number(config[2]))
    : "";
  const speedValues = generation ? speedMap[generation] || [] : [];
  const speed = String(
    speedValues.find((value) =>
      new RegExp(`(^|\\D)${value}(\\D|$)`).test(lower),
    ) || "",
  );
  const brand =
    ramBrands.find(
      (option) => option.id && lower.includes(option.id.toLowerCase()),
    )?.id || "";
  return { formFactor, generation, totalCapacity, configuration, speed, brand };
}

export type ConsoleBuilderSelection = {
  brand: "nintendo" | "playstation" | "xbox" | "";
  family: string;
  model: string;
  // Kept for backward-compatible parsing of old result-page URLs. Console
  // variants are grouped under the core model and are not active refinements.
  storage: string;
  edition: string;
};

export const emptyConsoleSelection: ConsoleBuilderSelection = {
  brand: "",
  family: "",
  model: "",
  storage: "",
  edition: "",
};

export const consoleBrands: SpecOption[] = [
  { id: "nintendo", label: "Nintendo" },
  { id: "playstation", label: "PlayStation" },
  { id: "xbox", label: "Xbox" },
];

const consoleFamilyMap: Record<string, SpecOption[]> = {
  nintendo: [
    { id: "nintendo-switch", label: "Nintendo Switch" },
    { id: "nintendo-wii-u", label: "Wii U" },
    { id: "nintendo-3ds", label: "Nintendo 3DS" },
  ],
  playstation: [
    { id: "playstation-4", label: "PlayStation 4" },
    { id: "playstation-5", label: "PlayStation 5" },
  ],
  xbox: [
    { id: "xbox-one", label: "Xbox One" },
    { id: "xbox-series", label: "Xbox Series" },
  ],
};

const consoleModelMap: Record<string, SpecOption[]> = {
  "nintendo-switch": [
    { id: "standard", label: "Nintendo Switch" },
    { id: "oled", label: "Switch OLED" },
    { id: "lite", label: "Switch Lite" },
    { id: "switch2", label: "Switch 2" },
  ],
  "nintendo-wii-u": [{ id: "wii-u", label: "Wii U" }],
  "nintendo-3ds": [{ id: "3ds-xl", label: "3DS XL" }],
  "playstation-4": [
    { id: "standard", label: "PlayStation 4" },
    { id: "slim", label: "PS4 Slim" },
    { id: "pro", label: "PS4 Pro" },
  ],
  "playstation-5": [
    { id: "standard", label: "PlayStation 5" },
    { id: "slim", label: "PS5 Slim" },
    { id: "pro", label: "PS5 Pro" },
  ],
  "xbox-one": [
    { id: "One S", label: "Xbox One S" },
    { id: "One X", label: "Xbox One X" },
  ],
  "xbox-series": [
    { id: "Series S", label: "Xbox Series S" },
    { id: "Series X", label: "Xbox Series X" },
  ],
};

export function consoleFamilyOptions(
  selection: ConsoleBuilderSelection,
): SpecOption[] {
  return selection.brand ? consoleFamilyMap[selection.brand] || [] : [];
}

export function consoleModelOptions(
  selection: ConsoleBuilderSelection,
): SpecOption[] {
  return selection.family ? consoleModelMap[selection.family] || [] : [];
}

// Reserved for a future narrowing update. Keeping the functions avoids
// breaking older imports while making the current model-first behavior clear.
export function consoleStorageOptions(
  _selection: ConsoleBuilderSelection,
): SpecOption[] {
  return [];
}

export function consoleEditionOptions(
  _selection: ConsoleBuilderSelection,
): SpecOption[] {
  return [];
}

export function consoleSelectionIsSearchable(
  selection: ConsoleBuilderSelection,
): boolean {
  return Boolean(selection.brand && selection.family && selection.model);
}

export function buildConsoleQuery(
  selection: ConsoleBuilderSelection,
): string | null {
  if (!consoleSelectionIsSearchable(selection)) return null;

  if (selection.family === "xbox-series") return `Xbox ${selection.model}`;
  if (selection.family === "xbox-one") return `Xbox ${selection.model}`;

  if (selection.family === "playstation-5") {
    if (selection.model === "slim") return "PlayStation 5 Slim";
    if (selection.model === "pro") return "PlayStation 5 Pro";
    return "PlayStation 5";
  }

  if (selection.family === "playstation-4") {
    if (selection.model === "slim") return "PlayStation 4 Slim";
    if (selection.model === "pro") return "PlayStation 4 Pro";
    return "PlayStation 4";
  }

  if (selection.family === "nintendo-switch") {
    if (selection.model === "oled") return "Nintendo Switch OLED";
    if (selection.model === "lite") return "Nintendo Switch Lite";
    if (selection.model === "switch2") return "Nintendo Switch 2";
    return "Nintendo Switch";
  }

  if (selection.family === "nintendo-wii-u") return "Nintendo Wii U";
  return "Nintendo 3DS XL";
}

export function parseConsoleQuery(
  query?: string | null,
): ConsoleBuilderSelection {
  if (!query) return { ...emptyConsoleSelection };
  const lower = query.toLowerCase();
  const compact = lower.replace(/[^a-z0-9]+/g, "");
  const selection: ConsoleBuilderSelection = { ...emptyConsoleSelection };

  if (compact.includes("xbox")) {
    selection.brand = "xbox";
    if (lower.includes("series") || compact.includes("seriesx") || compact.includes("seriess")) {
      selection.family = "xbox-series";
      if (lower.includes("series x") || compact.includes("seriesx")) selection.model = "Series X";
      if (lower.includes("series s") || compact.includes("seriess")) selection.model = "Series S";
    } else if (lower.includes("xbox one") || compact.includes("xboxone")) {
      selection.family = "xbox-one";
      if (lower.includes("one x") || compact.includes("onex")) selection.model = "One X";
      if (lower.includes("one s") || compact.includes("ones")) selection.model = "One S";
    }
  } else if (compact.includes("playstation") || compact.includes("ps5") || compact.includes("ps4")) {
    selection.brand = "playstation";
    selection.family = compact.includes("ps5") || compact.includes("playstation5") ? "playstation-5" : "playstation-4";
    if (lower.includes("slim")) selection.model = "slim";
    else if (lower.includes("pro")) selection.model = "pro";
    else selection.model = "standard";
    if (lower.includes("digital")) selection.edition = "digital";
    else if (lower.includes("disc") || lower.includes("disk")) selection.edition = "disc";
  } else if (compact.includes("wiiu")) {
    selection.brand = "nintendo";
    selection.family = "nintendo-wii-u";
    selection.model = "wii-u";
  } else if (compact.includes("3dsxl")) {
    selection.brand = "nintendo";
    selection.family = "nintendo-3ds";
    selection.model = "3ds-xl";
  } else if (compact.includes("switch")) {
    selection.brand = "nintendo";
    selection.family = "nintendo-switch";
    if (lower.includes("switch 2") || compact.includes("switch2")) selection.model = "switch2";
    else if (lower.includes("oled") || compact.includes("heg001")) selection.model = "oled";
    else if (lower.includes("lite") || compact.includes("hdh001")) selection.model = "lite";
    else selection.model = "standard";
  }

  const storage = lower.match(/\b(8\s*gb|32\s*gb|64\s*gb|500\s*gb|512\s*gb|825\s*gb|1\s*tb|2\s*tb)\b/i)?.[1];
  if (storage) selection.storage = storage.replace(/\s+/g, "").toUpperCase();
  return selection;
}


export type CpuBuilderSelection = {
  manufacturer: "amd" | "intel" | "";
  socket: string;
  generation: string;
  model: string;
};

export const emptyCpuSelection: CpuBuilderSelection = {
  manufacturer: "",
  socket: "",
  generation: "",
  model: "",
};

export const cpuManufacturers: SpecOption[] = [
  { id: "amd", label: "AMD" },
  { id: "intel", label: "Intel" },
];

const cpuTree: Record<string, Record<string, Record<string, Array<SpecOption & { query: string }>>>> = {
  "amd": {
    "AM4": {
      "Ryzen 3000": [
        {
          "id": "3100",
          "label": "Ryzen 3 3100",
          "query": "AMD Ryzen 3 3100"
        },
        {
          "id": "3300X",
          "label": "Ryzen 3 3300X",
          "query": "AMD Ryzen 3 3300X"
        },
        {
          "id": "3500X",
          "label": "Ryzen 5 3500X",
          "query": "AMD Ryzen 5 3500X"
        },
        {
          "id": "3600",
          "label": "Ryzen 5 3600",
          "query": "AMD Ryzen 5 3600"
        },
        {
          "id": "3600X",
          "label": "Ryzen 5 3600X",
          "query": "AMD Ryzen 5 3600X"
        },
        {
          "id": "3600XT",
          "label": "Ryzen 5 3600XT",
          "query": "AMD Ryzen 5 3600XT"
        },
        {
          "id": "3700X",
          "label": "Ryzen 7 3700X",
          "query": "AMD Ryzen 7 3700X"
        },
        {
          "id": "3800X",
          "label": "Ryzen 7 3800X",
          "query": "AMD Ryzen 7 3800X"
        },
        {
          "id": "3800XT",
          "label": "Ryzen 7 3800XT",
          "query": "AMD Ryzen 7 3800XT"
        },
        {
          "id": "3900X",
          "label": "Ryzen 9 3900X",
          "query": "AMD Ryzen 9 3900X"
        },
        {
          "id": "3900XT",
          "label": "Ryzen 9 3900XT",
          "query": "AMD Ryzen 9 3900XT"
        },
        {
          "id": "3950X",
          "label": "Ryzen 9 3950X",
          "query": "AMD Ryzen 9 3950X"
        }
      ],
      "Ryzen 4000G": [
        {
          "id": "4100",
          "label": "Ryzen 3 4100",
          "query": "AMD Ryzen 3 4100"
        },
        {
          "id": "4300G",
          "label": "Ryzen 3 4300G",
          "query": "AMD Ryzen 3 4300G"
        },
        {
          "id": "4500",
          "label": "Ryzen 5 4500",
          "query": "AMD Ryzen 5 4500"
        },
        {
          "id": "4600G",
          "label": "Ryzen 5 4600G",
          "query": "AMD Ryzen 5 4600G"
        },
        {
          "id": "4700G",
          "label": "Ryzen 7 4700G",
          "query": "AMD Ryzen 7 4700G"
        }
      ],
      "Ryzen 5000": [
        {
          "id": "5500",
          "label": "Ryzen 5 5500",
          "query": "AMD Ryzen 5 5500"
        },
        {
          "id": "5600",
          "label": "Ryzen 5 5600",
          "query": "AMD Ryzen 5 5600"
        },
        {
          "id": "5600G",
          "label": "Ryzen 5 5600G",
          "query": "AMD Ryzen 5 5600G"
        },
        {
          "id": "5600GT",
          "label": "Ryzen 5 5600GT",
          "query": "AMD Ryzen 5 5600GT"
        },
        {
          "id": "5600X",
          "label": "Ryzen 5 5600X",
          "query": "AMD Ryzen 5 5600X"
        },
        {
          "id": "5700",
          "label": "Ryzen 7 5700",
          "query": "AMD Ryzen 7 5700"
        },
        {
          "id": "5700G",
          "label": "Ryzen 7 5700G",
          "query": "AMD Ryzen 7 5700G"
        },
        {
          "id": "5700X",
          "label": "Ryzen 7 5700X",
          "query": "AMD Ryzen 7 5700X"
        },
        {
          "id": "5700X3D",
          "label": "Ryzen 7 5700X3D",
          "query": "AMD Ryzen 7 5700X3D"
        },
        {
          "id": "5800X",
          "label": "Ryzen 7 5800X",
          "query": "AMD Ryzen 7 5800X"
        },
        {
          "id": "5800XT",
          "label": "Ryzen 7 5800XT",
          "query": "AMD Ryzen 7 5800XT"
        },
        {
          "id": "5800X3D",
          "label": "Ryzen 7 5800X3D",
          "query": "AMD Ryzen 7 5800X3D"
        },
        {
          "id": "5900X",
          "label": "Ryzen 9 5900X",
          "query": "AMD Ryzen 9 5900X"
        },
        {
          "id": "5900XT",
          "label": "Ryzen 9 5900XT",
          "query": "AMD Ryzen 9 5900XT"
        },
        {
          "id": "5950X",
          "label": "Ryzen 9 5950X",
          "query": "AMD Ryzen 9 5950X"
        }
      ]
    },
    "AM5": {
      "Ryzen 7000": [
        {
          "id": "7500F",
          "label": "Ryzen 5 7500F",
          "query": "AMD Ryzen 5 7500F"
        },
        {
          "id": "7600",
          "label": "Ryzen 5 7600",
          "query": "AMD Ryzen 5 7600"
        },
        {
          "id": "7600X",
          "label": "Ryzen 5 7600X",
          "query": "AMD Ryzen 5 7600X"
        },
        {
          "id": "7700",
          "label": "Ryzen 7 7700",
          "query": "AMD Ryzen 7 7700"
        },
        {
          "id": "7700X",
          "label": "Ryzen 7 7700X",
          "query": "AMD Ryzen 7 7700X"
        },
        {
          "id": "7800X3D",
          "label": "Ryzen 7 7800X3D",
          "query": "AMD Ryzen 7 7800X3D"
        },
        {
          "id": "7900",
          "label": "Ryzen 9 7900",
          "query": "AMD Ryzen 9 7900"
        },
        {
          "id": "7900X",
          "label": "Ryzen 9 7900X",
          "query": "AMD Ryzen 9 7900X"
        },
        {
          "id": "7900X3D",
          "label": "Ryzen 9 7900X3D",
          "query": "AMD Ryzen 9 7900X3D"
        },
        {
          "id": "7950X",
          "label": "Ryzen 9 7950X",
          "query": "AMD Ryzen 9 7950X"
        },
        {
          "id": "7950X3D",
          "label": "Ryzen 9 7950X3D",
          "query": "AMD Ryzen 9 7950X3D"
        }
      ],
      "Ryzen 8000G": [
        {
          "id": "8300G",
          "label": "Ryzen 3 8300G",
          "query": "AMD Ryzen 3 8300G"
        },
        {
          "id": "8500G",
          "label": "Ryzen 5 8500G",
          "query": "AMD Ryzen 5 8500G"
        },
        {
          "id": "8600G",
          "label": "Ryzen 5 8600G",
          "query": "AMD Ryzen 5 8600G"
        },
        {
          "id": "8700G",
          "label": "Ryzen 7 8700G",
          "query": "AMD Ryzen 7 8700G"
        }
      ],
      "Ryzen 9000": [
        {
          "id": "9600X",
          "label": "Ryzen 5 9600X",
          "query": "AMD Ryzen 5 9600X"
        },
        {
          "id": "9700X",
          "label": "Ryzen 7 9700X",
          "query": "AMD Ryzen 7 9700X"
        },
        {
          "id": "9800X3D",
          "label": "Ryzen 7 9800X3D",
          "query": "AMD Ryzen 7 9800X3D"
        },
        {
          "id": "9900X",
          "label": "Ryzen 9 9900X",
          "query": "AMD Ryzen 9 9900X"
        },
        {
          "id": "9900X3D",
          "label": "Ryzen 9 9900X3D",
          "query": "AMD Ryzen 9 9900X3D"
        },
        {
          "id": "9950X",
          "label": "Ryzen 9 9950X",
          "query": "AMD Ryzen 9 9950X"
        },
        {
          "id": "9950X3D",
          "label": "Ryzen 9 9950X3D",
          "query": "AMD Ryzen 9 9950X3D"
        }
      ]
    }
  },
  "intel": {
    "LGA1151": {
      "8th Gen Core": [
        {
          "id": "8100",
          "label": "Core i3-8100",
          "query": "Intel Core i3-8100"
        },
        {
          "id": "8350K",
          "label": "Core i3-8350K",
          "query": "Intel Core i3-8350K"
        },
        {
          "id": "8400",
          "label": "Core i5-8400",
          "query": "Intel Core i5-8400"
        },
        {
          "id": "8500",
          "label": "Core i5-8500",
          "query": "Intel Core i5-8500"
        },
        {
          "id": "8600K",
          "label": "Core i5-8600K",
          "query": "Intel Core i5-8600K"
        },
        {
          "id": "8700",
          "label": "Core i7-8700",
          "query": "Intel Core i7-8700"
        },
        {
          "id": "8700K",
          "label": "Core i7-8700K",
          "query": "Intel Core i7-8700K"
        }
      ],
      "9th Gen Core": [
        {
          "id": "9100",
          "label": "Core i3-9100",
          "query": "Intel Core i3-9100"
        },
        {
          "id": "9100F",
          "label": "Core i3-9100F",
          "query": "Intel Core i3-9100F"
        },
        {
          "id": "9400",
          "label": "Core i5-9400",
          "query": "Intel Core i5-9400"
        },
        {
          "id": "9400F",
          "label": "Core i5-9400F",
          "query": "Intel Core i5-9400F"
        },
        {
          "id": "9600K",
          "label": "Core i5-9600K",
          "query": "Intel Core i5-9600K"
        },
        {
          "id": "9600KF",
          "label": "Core i5-9600KF",
          "query": "Intel Core i5-9600KF"
        },
        {
          "id": "9700",
          "label": "Core i7-9700",
          "query": "Intel Core i7-9700"
        },
        {
          "id": "9700F",
          "label": "Core i7-9700F",
          "query": "Intel Core i7-9700F"
        },
        {
          "id": "9700K",
          "label": "Core i7-9700K",
          "query": "Intel Core i7-9700K"
        },
        {
          "id": "9700KF",
          "label": "Core i7-9700KF",
          "query": "Intel Core i7-9700KF"
        },
        {
          "id": "9900",
          "label": "Core i9-9900",
          "query": "Intel Core i9-9900"
        },
        {
          "id": "9900K",
          "label": "Core i9-9900K",
          "query": "Intel Core i9-9900K"
        },
        {
          "id": "9900KF",
          "label": "Core i9-9900KF",
          "query": "Intel Core i9-9900KF"
        },
        {
          "id": "9900KS",
          "label": "Core i9-9900KS",
          "query": "Intel Core i9-9900KS"
        }
      ]
    },
    "LGA1200": {
      "10th Gen Core": [
        {
          "id": "10100",
          "label": "Core i3-10100",
          "query": "Intel Core i3-10100"
        },
        {
          "id": "10100F",
          "label": "Core i3-10100F",
          "query": "Intel Core i3-10100F"
        },
        {
          "id": "10400",
          "label": "Core i5-10400",
          "query": "Intel Core i5-10400"
        },
        {
          "id": "10400F",
          "label": "Core i5-10400F",
          "query": "Intel Core i5-10400F"
        },
        {
          "id": "10600K",
          "label": "Core i5-10600K",
          "query": "Intel Core i5-10600K"
        },
        {
          "id": "10600KF",
          "label": "Core i5-10600KF",
          "query": "Intel Core i5-10600KF"
        },
        {
          "id": "10700",
          "label": "Core i7-10700",
          "query": "Intel Core i7-10700"
        },
        {
          "id": "10700F",
          "label": "Core i7-10700F",
          "query": "Intel Core i7-10700F"
        },
        {
          "id": "10700K",
          "label": "Core i7-10700K",
          "query": "Intel Core i7-10700K"
        },
        {
          "id": "10700KF",
          "label": "Core i7-10700KF",
          "query": "Intel Core i7-10700KF"
        },
        {
          "id": "10850K",
          "label": "Core i9-10850K",
          "query": "Intel Core i9-10850K"
        },
        {
          "id": "10900",
          "label": "Core i9-10900",
          "query": "Intel Core i9-10900"
        },
        {
          "id": "10900F",
          "label": "Core i9-10900F",
          "query": "Intel Core i9-10900F"
        },
        {
          "id": "10900K",
          "label": "Core i9-10900K",
          "query": "Intel Core i9-10900K"
        },
        {
          "id": "10900KF",
          "label": "Core i9-10900KF",
          "query": "Intel Core i9-10900KF"
        }
      ],
      "11th Gen Core": [
        {
          "id": "11400",
          "label": "Core i5-11400",
          "query": "Intel Core i5-11400"
        },
        {
          "id": "11400F",
          "label": "Core i5-11400F",
          "query": "Intel Core i5-11400F"
        },
        {
          "id": "11600K",
          "label": "Core i5-11600K",
          "query": "Intel Core i5-11600K"
        },
        {
          "id": "11600KF",
          "label": "Core i5-11600KF",
          "query": "Intel Core i5-11600KF"
        },
        {
          "id": "11700",
          "label": "Core i7-11700",
          "query": "Intel Core i7-11700"
        },
        {
          "id": "11700F",
          "label": "Core i7-11700F",
          "query": "Intel Core i7-11700F"
        },
        {
          "id": "11700K",
          "label": "Core i7-11700K",
          "query": "Intel Core i7-11700K"
        },
        {
          "id": "11700KF",
          "label": "Core i7-11700KF",
          "query": "Intel Core i7-11700KF"
        },
        {
          "id": "11900",
          "label": "Core i9-11900",
          "query": "Intel Core i9-11900"
        },
        {
          "id": "11900F",
          "label": "Core i9-11900F",
          "query": "Intel Core i9-11900F"
        },
        {
          "id": "11900K",
          "label": "Core i9-11900K",
          "query": "Intel Core i9-11900K"
        },
        {
          "id": "11900KF",
          "label": "Core i9-11900KF",
          "query": "Intel Core i9-11900KF"
        }
      ]
    },
    "LGA1700": {
      "12th Gen Core": [
        {
          "id": "12100",
          "label": "Core i3-12100",
          "query": "Intel Core i3-12100"
        },
        {
          "id": "12100F",
          "label": "Core i3-12100F",
          "query": "Intel Core i3-12100F"
        },
        {
          "id": "12400",
          "label": "Core i5-12400",
          "query": "Intel Core i5-12400"
        },
        {
          "id": "12400F",
          "label": "Core i5-12400F",
          "query": "Intel Core i5-12400F"
        },
        {
          "id": "12600K",
          "label": "Core i5-12600K",
          "query": "Intel Core i5-12600K"
        },
        {
          "id": "12600KF",
          "label": "Core i5-12600KF",
          "query": "Intel Core i5-12600KF"
        },
        {
          "id": "12700",
          "label": "Core i7-12700",
          "query": "Intel Core i7-12700"
        },
        {
          "id": "12700F",
          "label": "Core i7-12700F",
          "query": "Intel Core i7-12700F"
        },
        {
          "id": "12700K",
          "label": "Core i7-12700K",
          "query": "Intel Core i7-12700K"
        },
        {
          "id": "12700KF",
          "label": "Core i7-12700KF",
          "query": "Intel Core i7-12700KF"
        },
        {
          "id": "12900",
          "label": "Core i9-12900",
          "query": "Intel Core i9-12900"
        },
        {
          "id": "12900F",
          "label": "Core i9-12900F",
          "query": "Intel Core i9-12900F"
        },
        {
          "id": "12900K",
          "label": "Core i9-12900K",
          "query": "Intel Core i9-12900K"
        },
        {
          "id": "12900KF",
          "label": "Core i9-12900KF",
          "query": "Intel Core i9-12900KF"
        },
        {
          "id": "12900KS",
          "label": "Core i9-12900KS",
          "query": "Intel Core i9-12900KS"
        }
      ],
      "13th Gen Core": [
        {
          "id": "13100",
          "label": "Core i3-13100",
          "query": "Intel Core i3-13100"
        },
        {
          "id": "13100F",
          "label": "Core i3-13100F",
          "query": "Intel Core i3-13100F"
        },
        {
          "id": "13400",
          "label": "Core i5-13400",
          "query": "Intel Core i5-13400"
        },
        {
          "id": "13400F",
          "label": "Core i5-13400F",
          "query": "Intel Core i5-13400F"
        },
        {
          "id": "13500",
          "label": "Core i5-13500",
          "query": "Intel Core i5-13500"
        },
        {
          "id": "13600K",
          "label": "Core i5-13600K",
          "query": "Intel Core i5-13600K"
        },
        {
          "id": "13600KF",
          "label": "Core i5-13600KF",
          "query": "Intel Core i5-13600KF"
        },
        {
          "id": "13700",
          "label": "Core i7-13700",
          "query": "Intel Core i7-13700"
        },
        {
          "id": "13700F",
          "label": "Core i7-13700F",
          "query": "Intel Core i7-13700F"
        },
        {
          "id": "13700K",
          "label": "Core i7-13700K",
          "query": "Intel Core i7-13700K"
        },
        {
          "id": "13700KF",
          "label": "Core i7-13700KF",
          "query": "Intel Core i7-13700KF"
        },
        {
          "id": "13900",
          "label": "Core i9-13900",
          "query": "Intel Core i9-13900"
        },
        {
          "id": "13900F",
          "label": "Core i9-13900F",
          "query": "Intel Core i9-13900F"
        },
        {
          "id": "13900K",
          "label": "Core i9-13900K",
          "query": "Intel Core i9-13900K"
        },
        {
          "id": "13900KF",
          "label": "Core i9-13900KF",
          "query": "Intel Core i9-13900KF"
        },
        {
          "id": "13900KS",
          "label": "Core i9-13900KS",
          "query": "Intel Core i9-13900KS"
        }
      ],
      "14th Gen Core": [
        {
          "id": "14100",
          "label": "Core i3-14100",
          "query": "Intel Core i3-14100"
        },
        {
          "id": "14100F",
          "label": "Core i3-14100F",
          "query": "Intel Core i3-14100F"
        },
        {
          "id": "14400",
          "label": "Core i5-14400",
          "query": "Intel Core i5-14400"
        },
        {
          "id": "14400F",
          "label": "Core i5-14400F",
          "query": "Intel Core i5-14400F"
        },
        {
          "id": "14500",
          "label": "Core i5-14500",
          "query": "Intel Core i5-14500"
        },
        {
          "id": "14600K",
          "label": "Core i5-14600K",
          "query": "Intel Core i5-14600K"
        },
        {
          "id": "14600KF",
          "label": "Core i5-14600KF",
          "query": "Intel Core i5-14600KF"
        },
        {
          "id": "14700",
          "label": "Core i7-14700",
          "query": "Intel Core i7-14700"
        },
        {
          "id": "14700F",
          "label": "Core i7-14700F",
          "query": "Intel Core i7-14700F"
        },
        {
          "id": "14700K",
          "label": "Core i7-14700K",
          "query": "Intel Core i7-14700K"
        },
        {
          "id": "14700KF",
          "label": "Core i7-14700KF",
          "query": "Intel Core i7-14700KF"
        },
        {
          "id": "14900",
          "label": "Core i9-14900",
          "query": "Intel Core i9-14900"
        },
        {
          "id": "14900F",
          "label": "Core i9-14900F",
          "query": "Intel Core i9-14900F"
        },
        {
          "id": "14900K",
          "label": "Core i9-14900K",
          "query": "Intel Core i9-14900K"
        },
        {
          "id": "14900KF",
          "label": "Core i9-14900KF",
          "query": "Intel Core i9-14900KF"
        },
        {
          "id": "14900KS",
          "label": "Core i9-14900KS",
          "query": "Intel Core i9-14900KS"
        }
      ]
    },
    "LGA1851": {
      "Core Ultra Series 2": [
        {
          "id": "225",
          "label": "Core Ultra 5 225",
          "query": "Intel Core Ultra 5 225"
        },
        {
          "id": "225F",
          "label": "Core Ultra 5 225F",
          "query": "Intel Core Ultra 5 225F"
        },
        {
          "id": "235",
          "label": "Core Ultra 5 235",
          "query": "Intel Core Ultra 5 235"
        },
        {
          "id": "245",
          "label": "Core Ultra 5 245",
          "query": "Intel Core Ultra 5 245"
        },
        {
          "id": "245K",
          "label": "Core Ultra 5 245K",
          "query": "Intel Core Ultra 5 245K"
        },
        {
          "id": "245KF",
          "label": "Core Ultra 5 245KF",
          "query": "Intel Core Ultra 5 245KF"
        },
        {
          "id": "265",
          "label": "Core Ultra 7 265",
          "query": "Intel Core Ultra 7 265"
        },
        {
          "id": "265F",
          "label": "Core Ultra 7 265F",
          "query": "Intel Core Ultra 7 265F"
        },
        {
          "id": "265K",
          "label": "Core Ultra 7 265K",
          "query": "Intel Core Ultra 7 265K"
        },
        {
          "id": "265KF",
          "label": "Core Ultra 7 265KF",
          "query": "Intel Core Ultra 7 265KF"
        },
        {
          "id": "285",
          "label": "Core Ultra 9 285",
          "query": "Intel Core Ultra 9 285"
        },
        {
          "id": "285K",
          "label": "Core Ultra 9 285K",
          "query": "Intel Core Ultra 9 285K"
        }
      ]
    }
  }
};

export function cpuSocketOptions(selection: CpuBuilderSelection): SpecOption[] {
  if (!selection.manufacturer) return [];
  return Object.keys(cpuTree[selection.manufacturer] || {}).map((socket) => ({
    id: socket,
    label: socket,
  }));
}

export function cpuGenerationOptions(selection: CpuBuilderSelection): SpecOption[] {
  if (!selection.manufacturer || !selection.socket) return [];
  return Object.keys(cpuTree[selection.manufacturer]?.[selection.socket] || {}).map((generation) => ({
    id: generation,
    label: generation,
  }));
}

export function cpuModelOptions(selection: CpuBuilderSelection): SpecOption[] {
  if (!selection.manufacturer || !selection.socket || !selection.generation) return [];
  return cpuTree[selection.manufacturer]?.[selection.socket]?.[selection.generation] || [];
}

export function cpuSelectionIsComplete(selection: CpuBuilderSelection): boolean {
  return Boolean(selection.manufacturer && selection.socket && selection.generation && selection.model);
}

export function buildCpuQuery(selection: CpuBuilderSelection): string | null {
  if (!cpuSelectionIsComplete(selection)) return null;
  const option = cpuTree[selection.manufacturer]?.[selection.socket]?.[selection.generation]?.find(
    (model) => model.id === selection.model,
  );
  return option?.query || null;
}

export function parseCpuQuery(query?: string | null): CpuBuilderSelection {
  if (!query) return { ...emptyCpuSelection };
  const compact = query.toLowerCase().replace(/[^a-z0-9]+/g, "");
  const candidates: Array<{ manufacturer: string; socket: string; generation: string; model: string }> = [];
  for (const manufacturer of Object.keys(cpuTree)) {
    for (const socket of Object.keys(cpuTree[manufacturer] || {})) {
      for (const generation of Object.keys(cpuTree[manufacturer]?.[socket] || {})) {
        for (const option of cpuTree[manufacturer]?.[socket]?.[generation] || []) {
          candidates.push({ manufacturer, socket, generation, model: option.id });
        }
      }
    }
  }
  const match = candidates
    .sort((left, right) => right.model.length - left.model.length)
    .find((candidate) => compact.includes(candidate.model.toLowerCase()));
  if (!match) return { ...emptyCpuSelection };
  return {
    manufacturer: match.manufacturer as CpuBuilderSelection["manufacturer"],
    socket: match.socket,
    generation: match.generation,
    model: match.model,
  };
}
