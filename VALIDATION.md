# Validation · 2026-10-29

Spoolman base: bed3f14ee77a3a571d31b14215d54b0b88a7519c (0.27.0).

- Backend suite: 302 passed, including 24 reorder cases.
- Existing frontend suite: 298 passed across 24 files.
- SQLite import tests: 2 passed; source preserved, integrity verified,
  repeated startup does not overwrite an existing copy.
- Svelte/TypeScript check: 0 errors and 0 warnings.
- Static frontend production build: passed.
- Patch checked against the exact source with git apply --check.
- HA Supervisor: installation and startup of reorder.2 passed.
- Live reorder, settings and catalog APIs: HTTP 200.
- Live threshold change to 0 g and restore to 150 g: passed.
- Settings remained available after restarting only the test app.
- Catalog refreshed from public EU product APIs: 33 filament products,
  259 unique variants. Includes PETG and PA6-CF.

## Provider limitation

The legacy Shopify cart URL format is documented, but support must be
verified per merchant. Bambu EU's headless storefront returned HTTP 404
for the concrete multi-item cart path. The corresponding myshopify.com
cart page contains a JavaScript redirect to the headless storefront home
page. The checkout alternative was not verifiable over HTTP.

The broken Bambu cart is disabled. Product links and mappings are retained.
No successful Bambu cart or purchase has been claimed. No existing shop
session, login or payment was used in the anonymous HTTP checks.

## Still required before upstream submission

- Independent review and a review of current upstream changes.
- Visual desktop/mobile acceptance and screenshots.
- A real RFID-merge integration run on an isolated environment.
- A supported, independently verified Bambu multi-item route before
  re-enabling that provider's direct cart.

The included patch is an inspectable contribution starting point,
not an accepted upstream contribution. No PR was opened in Donkie/Spoolman.

Regenerate after editing an extracted upstream source tree:
`python prepare_package.py --upstream /path/to/Spoolman --modified /path/to/modified-source`.
Refresh the catalog separately using `python refresh_catalog.py`.
