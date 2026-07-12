# Scoutly v0.5.0 Console/LEGO cleanup

This update tightens marketplace filtering based on live testing:

- Rejects local-pickup-only listings globally.
- Rejects zero-feedback eBay sellers.
- Rejects console accessory/part listings such as heat shields, LCD replacements, console covers, WiFi boards/modules, disc-drive brackets, TPU covers, and game-only listings.
- Rejects trade/swap-style console listings.
- Improves Xbox Series X / Series S / Xbox One matching.
- Rejects LEGO bag-only listings.
- Reported results now trigger a refresh so the hidden item disappears cleanly instead of lingering beside newly loaded results.
- eBay seller feedback score is captured and shown on result cards.

Validation:

- Backend tests were run in split batches: 85 total passed.
- Frontend build was not run in this sandbox because node_modules is not installed here.
