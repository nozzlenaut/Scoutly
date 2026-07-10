export type CategoryStatus = "active" | "coming-soon" | "planned";

export type CategoryStatusItem = {
  id: string;
  label: string;
  shortLabel: string;
  status: CategoryStatus;
  tag: string;
  description: string;
};

export const categoryStatusItems: CategoryStatusItem[] = [
  {
    id: "gpus",
    label: "GPUs",
    shortLabel: "GPU",
    status: "active",
    tag: "GPU search added",
    description: "Catalog matching, mock marketplace results, and used-listing filtering are live.",
  },
  {
    id: "ebay-gpu",
    label: "eBay GPU pricing",
    shortLabel: "eBay",
    status: "coming-soon",
    tag: "eBay live pricing pending",
    description: "Ready for the official eBay Browse API once credentials are approved.",
  },
  {
    id: "cpus",
    label: "CPUs",
    shortLabel: "CPU",
    status: "planned",
    tag: "CPU search planned",
    description: "Planned after the GPU flow is stable.",
  },
  {
    id: "cameras",
    label: "Cameras",
    shortLabel: "Camera",
    status: "planned",
    tag: "Camera search planned",
    description: "A strong future category for used gear and lenses.",
  },
];

export function getActiveCategoryStatus() {
  return categoryStatusItems.find((item) => item.status === "active") ?? categoryStatusItems[0];
}
