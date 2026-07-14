# Scoutly v0.6.5 / PriceSift precision pass

- Preserves PlayStation Digital Edition through builder parsing, product resolution, headings, marketplace queries, and result filtering.
- Rejects Disc Edition results from Digital Edition searches and keeps standard, slim, and pro PlayStation identities separate.
- Tightens LEGO full-set filtering for missing parts, near/almost/mostly complete listings, completeness below 100%, minifigure/component-only listings, and mismatched set numbers.
- Rejects older-console shells, frames, heat sinks, drives, manuals/boxes, games, MixAmp/headset accessories, and listings without positive hardware evidence.
- Enforces exact GPU suffix conflicts for XT, Super, Ti, and Ti Super, plus explicit parts/failure language.
- Rejects mixed-brand RAM kits when the shopper selected a brand.
- Converts `read`, `read desc`, `read description`, `see description`, and `please read` into visible review warnings instead of automatic rejection when the listing otherwise matches.
- Keeps internal Scoutly infrastructure unchanged.
