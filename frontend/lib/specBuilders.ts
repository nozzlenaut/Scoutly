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
    { id: "nintendo-3ds-xl", label: "3DS XL" },
    { id: "nintendo-switch", label: "Switch" },
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
  "nintendo-3ds-xl": [{ id: "", label: "Any 3DS XL" }],
  "nintendo-switch": [
    { id: "", label: "Any Switch model" },
    { id: "standard", label: "Standard Switch" },
    { id: "oled", label: "Switch OLED" },
    { id: "lite", label: "Switch Lite" },
  ],
  "playstation-4": [
    { id: "", label: "Any PS4 model" },
    { id: "slim", label: "PS4 Slim" },
    { id: "pro", label: "PS4 Pro" },
  ],
  "playstation-5": [
    { id: "", label: "Any PS5 model" },
    { id: "standard", label: "Standard PS5" },
    { id: "slim", label: "PS5 Slim" },
    { id: "pro", label: "PS5 Pro" },
  ],
  "xbox-one": [
    { id: "", label: "Any Xbox One model" },
    { id: "One S", label: "Xbox One S" },
    { id: "One X", label: "Xbox One X" },
  ],
  "xbox-series": [
    { id: "", label: "Any Xbox Series model" },
    { id: "Series S", label: "Xbox Series S" },
    { id: "Series X", label: "Xbox Series X" },
  ],
};

const consoleStorageMap: Record<string, SpecOption[]> = {
  "playstation-5:": [
    { id: "", label: "Any storage" },
    { id: "825GB", label: "825GB" },
    { id: "1TB", label: "1TB" },
    { id: "2TB", label: "2TB" },
  ],
  "playstation-5:standard": [
    { id: "", label: "Any storage" },
    { id: "825GB", label: "825GB" },
  ],
  "playstation-5:slim": [
    { id: "", label: "Any storage" },
    { id: "1TB", label: "1TB" },
  ],
  "playstation-5:pro": [
    { id: "", label: "Any storage" },
    { id: "2TB", label: "2TB" },
  ],
  "xbox-series:": [
    { id: "", label: "Any storage" },
    { id: "512GB", label: "512GB" },
    { id: "1TB", label: "1TB" },
  ],
  "xbox-series:Series S": [
    { id: "", label: "Any storage" },
    { id: "512GB", label: "512GB" },
    { id: "1TB", label: "1TB" },
  ],
  "xbox-series:Series X": [
    { id: "", label: "Any storage" },
    { id: "1TB", label: "1TB" },
  ],
  "xbox-one:": [
    { id: "", label: "Any storage" },
    { id: "1TB", label: "1TB" },
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

export function consoleStorageOptions(
  selection: ConsoleBuilderSelection,
): SpecOption[] {
  const key = `${selection.family}:${selection.model}`;
  return consoleStorageMap[key] || [];
}

export function consoleEditionOptions(
  selection: ConsoleBuilderSelection,
): SpecOption[] {
  if (selection.family !== "playstation-5" || selection.model === "pro") {
    return [];
  }
  return [
    { id: "", label: "Any edition" },
    { id: "disc", label: "Disc Edition" },
    { id: "digital", label: "Digital Edition" },
  ];
}

export function consoleSelectionIsSearchable(
  selection: ConsoleBuilderSelection,
): boolean {
  return Boolean(selection.brand && selection.family);
}

export function buildConsoleQuery(
  selection: ConsoleBuilderSelection,
): string | null {
  if (!consoleSelectionIsSearchable(selection)) return null;

  let query = "";
  if (selection.family === "xbox-series") {
    query = selection.model ? `Xbox ${selection.model}` : "Xbox Series";
  } else if (selection.family === "xbox-one") {
    query = selection.model ? `Xbox ${selection.model}` : "Xbox One";
  } else if (selection.family === "playstation-5") {
    query = "PlayStation 5";
    if (selection.model) {
      query += ` ${selection.model === "standard" ? "Standard" : selection.model[0].toUpperCase() + selection.model.slice(1)}`;
    }
  } else if (selection.family === "playstation-4") {
    query = "PlayStation 4";
    if (selection.model) {
      query += ` ${selection.model[0].toUpperCase() + selection.model.slice(1)}`;
    }
  } else if (selection.family === "nintendo-switch") {
    query = "Nintendo Switch";
    if (selection.model === "standard") query += " Standard";
    if (selection.model === "oled") query += " OLED";
    if (selection.model === "lite") query += " Lite";
  } else {
    query = "Nintendo 3DS XL";
  }

  if (selection.storage) query += ` ${selection.storage}`;
  if (selection.edition === "disc") query += " Disc Edition";
  if (selection.edition === "digital") query += " Digital Edition";
  return query;
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
    else if (lower.includes("standard")) selection.model = "standard";
    if (lower.includes("digital")) selection.edition = "digital";
    else if (lower.includes("disc") || lower.includes("disk")) selection.edition = "disc";
  } else if (compact.includes("3dsxl")) {
    selection.brand = "nintendo";
    selection.family = "nintendo-3ds-xl";
  } else if (compact.includes("switch")) {
    selection.brand = "nintendo";
    selection.family = "nintendo-switch";
    if (lower.includes("oled")) selection.model = "oled";
    else if (lower.includes("lite")) selection.model = "lite";
    else if (lower.includes("standard") || lower.includes("v1") || lower.includes("v2")) selection.model = "standard";
  }

  const storage = lower.match(/\b(512\s*gb|825\s*gb|1\s*tb|2\s*tb)\b/i)?.[1];
  if (storage) selection.storage = storage.replace(/\s+/g, "").toUpperCase();
  return selection;
}
