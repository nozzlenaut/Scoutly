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
