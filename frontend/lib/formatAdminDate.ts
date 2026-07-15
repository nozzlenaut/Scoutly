const ADMIN_TIME_ZONE = "America/Detroit";

const adminDateFormatter = new Intl.DateTimeFormat("en-US", {
  timeZone: ADMIN_TIME_ZONE,
  year: "numeric",
  month: "short",
  day: "numeric",
  hour: "numeric",
  minute: "2-digit",
  timeZoneName: "short",
});

function normalizeTimestamp(value: string): string {
  const trimmed = value.trim();
  const hasExplicitTimeZone = /(?:Z|[+-]\d{2}:?\d{2})$/i.test(trimmed);

  // Older database/file records may contain a UTC timestamp without an offset.
  // Treat those as UTC instead of allowing the rendering server to guess.
  if (trimmed.includes("T") && !hasExplicitTimeZone) {
    return `${trimmed}Z`;
  }

  return trimmed;
}

export function formatAdminDate(value?: string | null): string {
  if (!value) return "â€”";
  const date = new Date(normalizeTimestamp(value));
  return Number.isNaN(date.getTime()) ? value : adminDateFormatter.format(date);
}
