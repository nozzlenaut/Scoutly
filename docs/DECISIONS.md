# PriceSift decisions

These are settled product and process decisions. Revisit them only when real evidence gives us a good reason.

## Product identity

1. PriceSift is a **results site**, not a broad search, browsing, trend, or deal-feed site.
2. The core promise is: **Find the best price for what you already want.**
3. The goal is not to return the most listings. The goal is to return the few listings worth looking at.
4. Trust and exact identity matter more than result count.

## Search and result design

1. Search flows stay category-specific.
2. Direct identity is used for cameras, GPUs, consoles, LEGO, and other strong model identifiers.
3. Specification builders are used when compatibility is defined by attributes, such as RAM and CPUs.
4. ISBN identifies books.
5. Fixed-price results stay separate from optional ending-soon auctions.
6. Total price should include shipping when available.
7. Filters should remove wrong models, accessories, parts-only items, broken gear, incomplete listings, and misleading variations when detectable.

## Provider coverage

1. Catalog-matched cameras may use eBay and KEH.
2. Public lenses use KEH only for now.
3. Public eBay lens search stays disabled until matching is trustworthy.
4. KEH’s standardized camera titles are grouped into searchable models automatically.
5. A camera without a confident PriceSift catalog match is KEH-only and must never be sent to eBay.

## User experience and trust

1. No account is required for normal searching.
2. Affiliate relationships must be clearly disclosed.
3. Affiliate status does not change displayed prices or ranking rules.
4. Users should be able to report inaccurate, incomplete, broken, or unrelated results.
5. PriceSift should prefer an honest no-result over a convincing wrong result.
6. A delivery ZIP is optional, used only for the current exact-listing eBay estimate, and is never persisted in URLs, analytics, logs, or browser storage.

## Growth and scope

A new category should usually require at least one of these:

1. Repeated user demand
2. Search or feedback data showing demand
3. A strong community, partnership, or traffic opportunity
4. A meaningful new audience that can quickly understand PriceSift's value

Quiet traffic alone is not a reason to add another category.

## Development process

1. Discuss larger changes before building them.
2. Define the problem, user, scope, success data, risks, and smallest useful version first.
3. Default delivery is a ZIP with manual review, commit, and push.
4. Do not automatically commit or push unless explicitly requested.
5. PowerShell installers are not the default.
6. Tests are useful data; unrelated failures are reported and understood but do not automatically block every release.
7. The assistant should explain Git safety, warnings, failures, and expected output rather than assuming programming knowledge.
