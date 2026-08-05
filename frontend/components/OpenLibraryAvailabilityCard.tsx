import type { OpenLibraryAvailability } from "@/lib/openLibraryTypes";

function actionCopy(availability: OpenLibraryAvailability): {
  button: string;
  headline: string;
  detail: string;
} {
  const similar = availability.match === "similar";
  const edition = similar ? "A similar edition" : "This edition";

  if (availability.status === "full access") {
    return {
      button: "Open readable edition",
      headline: `${edition} is readable free online.`,
      detail: similar
        ? "Open Library found a readable edition of the same work, but not necessarily this exact ISBN."
        : "Open Library reports full online access for the exact edition match.",
    };
  }

  if (availability.status === "lendable") {
    return {
      button: "Open borrowable edition",
      headline: `${edition} can be borrowed through Open Library.`,
      detail: similar
        ? "The borrowable copy is another edition of the same work. An Open Library account may be required."
        : "The exact edition match is currently lendable. An Open Library account may be required.",
    };
  }

  if (availability.status === "checked out") {
    return {
      button: "Open edition page",
      headline: `${edition} is currently checked out.`,
      detail: "Open Library may offer a waitlist or show when the digital copy becomes available again.",
    };
  }

  if (availability.lookup_state === "record" || availability.status === "restricted") {
    return {
      button: "View Open Library record",
      headline: "Open Library has a catalog record for this ISBN.",
      detail: "A readable or borrowable digital copy was not reported in this lookup.",
    };
  }

  if (availability.lookup_state === "none") {
    return {
      button: "Check Open Library",
      headline: "No readable copy was reported for this ISBN.",
      detail: "Open Library may still have another edition or a record worth checking.",
    };
  }

  return {
    button: "Check Open Library",
    headline: "Check for a free read or borrow option.",
    detail: "The live availability check did not finish, so this opens the ISBN page directly.",
  };
}

export function OpenLibraryAvailabilityCard({
  availability,
  theme = "dark",
}: {
  availability: OpenLibraryAvailability;
  theme?: "dark" | "light";
}) {
  const copy = actionCopy(availability);
  const url =
    availability.record_url ||
    `https://openlibrary.org/isbn/${encodeURIComponent(availability.isbn)}`;
  const editionLabel =
    availability.match === "exact"
      ? "Exact edition"
      : availability.match === "similar"
        ? "Similar edition"
        : "ISBN lookup";

  return (
    <section
      className={theme === "light" ? "mt-4 rounded-2xl border border-ps-border bg-ps-surface p-4 sm:p-5" : "mt-4 rounded-2xl border border-sky-300/20 bg-sky-300/[0.055] p-4 sm:p-5"}
      aria-label="Open Library availability"
    >
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div className="max-w-3xl">
          <div className="flex flex-wrap items-center gap-2">
            <p className={theme === "light" ? "text-xs font-bold uppercase tracking-[0.2em] text-ps-info" : "text-xs font-bold uppercase tracking-[0.2em] text-sky-200"}>
              Check Open Library · free option
            </p>
            <span className={theme === "light" ? "rounded-full border border-ps-border bg-ps-control px-2.5 py-1 text-[11px] font-semibold text-ps-info" : "rounded-full border border-sky-200/20 bg-sky-200/10 px-2.5 py-1 text-[11px] font-semibold text-sky-100"}>
              {editionLabel}
            </span>
          </div>
          <h2 className="mt-2 text-xl font-black">{copy.headline}</h2>
          <p className={theme === "light" ? "mt-2 text-sm leading-6 text-ps-text-secondary" : "mt-2 text-sm leading-6 text-slate-300"}>
            {copy.detail} The button opens the specific Open Library edition page, where any read or borrow action is shown.
          </p>
          {availability.publish_date ? (
            <p className={theme === "light" ? "mt-1 text-xs text-ps-neutral" : "mt-1 text-xs text-slate-500"}>Digital edition date: {availability.publish_date}</p>
          ) : null}
        </div>
        <a
          href={url}
          target="_blank"
          rel="noreferrer"
          className={theme === "light" ? "w-fit shrink-0 rounded-2xl bg-ps-accent-strong px-5 py-3 text-sm font-bold text-white transition hover:bg-ps-accent-hover" : "w-fit shrink-0 rounded-2xl bg-sky-200 px-5 py-3 text-sm font-bold text-slate-950 transition hover:bg-sky-100"}
        >
          {copy.button}
        </a>
      </div>
    </section>
  );
}
