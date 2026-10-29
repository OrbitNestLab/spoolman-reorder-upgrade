**Is your feature request related to a problem? Please describe.**

The v2 frontend handles unopened spools well, as discussed in #882. The remaining use case is a shared reorder plan: a nearly empty spool should not produce a buying suggestion when sufficient unopened replacements already exist. The current low-stock threshold is a browser preference, so different clients can use different rules.

**Describe the solution you'd like**

A manufacturer-independent reorder view in v2 with policies stored through Spoolman's existing settings API:

- A configurable gram threshold, default 150 g, including a valid 0 g.
- Independent unopened minimum and order quantity, with per-profile overrides.
- Aggregation by manufacturer, material, name, colour and finish; archived spools excluded. Unknown weights should be flagged rather than treated as empty.
- One suggestion per profile, suppressed when reserve stock is sufficient.
- Read-only planning: no changes to usage, spool IDs, RFID tags or inventory.

For example, an opened spool at 10 g plus one unopened replacement should produce no suggestion when the reserve minimum is one. The same profile without a replacement should produce one suggestion.

**Describe alternatives you've considered**

An external Home Assistant/Node-RED calculation works for one installation, but duplicates Spoolman's inventory logic and does not share configuration across Spoolman clients. This proposal complements #882 rather than replacing how unopened spools are represented.

**Additional context**

There is an experimental implementation and an installable Home Assistant test package:

- [Beta repository and installation](https://github.com/OrbitNestLab/spoolman-reorder-upgrade)
- [Inspectable source patch](https://github.com/OrbitNestLab/spoolman-reorder-upgrade/blob/main/spoolman_reorder/upstream.patch)
- [Validation and remaining work](https://github.com/OrbitNestLab/spoolman-reorder-upgrade/blob/main/VALIDATION.md)

The package targets Spoolman 0.27.0, commit `bed3f14`. It has passed the 302-test backend suite, the existing 298-test frontend suite, two SQLite-copy tests, type checking and a production frontend build. Its settings and read-only planning endpoints were also checked on a running test app, including restart persistence and a 0 g threshold.

This is a beta, not a proposed merge-ready patch. Independent review, desktop/mobile screenshots, an isolated RFID-merge integration test and reconciliation with current upstream are still required.

Shop integration is optional. A Bambu EU catalog is kept separately from the stock calculation. The tested Bambu direct-cart routes do **not** work reliably with its current storefront, so the beta disables that cart and provides individual product links. No working Bambu one-click cart is claimed, and no purchase or payment is performed.

Would this shared policy/reorder-view design fit Spoolman's direction before a focused upstream PR is prepared?
