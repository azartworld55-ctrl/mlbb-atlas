# Upstream skill-source audit

Audit date: 2026-11-14.

## Decision

Use Linconius/MLBB-Build-Analyser as the **data-model and patch-history reference**, not as an unquestioned source of current values. Combine metadata from the Moonton GMS endpoint exposed by warungerik/MLBB-Hero-Scraper with achedon12/mlbb's wiki/stats synchronization approach, then compare each field against independent patch notes and controlled in-game observations.

No source is automatically authoritative for every field:
- Moonton GMS metadata is the preferred candidate for current skill identifiers, names, icons, descriptions and cooldown/resource text. The observed endpoint and scraper are community tooling; endpoint terms and stable access are not yet confirmed.
- Wiki/community datasets are useful for numerical descriptions and historical context, but must retain their own license and attribution.
- Build Analyser provides a useful per-hero JSON shape, formula DSL and Git-based patch history. Its README says formulas are manually authored and only five heroes were complete at the time inspected. A repository LICENSE file was not found at the expected path in this audit, so do not copy its code or data until licensing is confirmed.
- achedon12/mlbb is MIT-licensed as code; its README says Wiki-derived game data is CC BY-SA and visual assets remain Moonton property. Keep data licensing separate from code licensing.

## Comparison rules

1. Match heroes by stable Moonton hero ID where available, not display name alone.
2. Match skills by Moonton skill ID first; retain group/slot and raw source labels because IDs or group ordering can change after a revamp.
3. Keep raw values from each source. Normalize into Atlas fields only after recording the original text and source revision.
4. Compare field-by-field: skill identity, description, cooldown, resource cost, level count, damage type, base damage, scaling attribute/basis, duration, CC, healing, shields and conditions.
5. A mismatch creates a conflict record. Do not average values or select the newest timestamp blindly.
6. Resolve conflicts in this order: official live-server patch notes; repeatable Original Server in-game test under documented conditions; current official-client metadata for identity/text fields; independently maintained wiki/community references. Community sources can corroborate but do not by themselves prove a value is current.
7. Distinguish Original Server from Advanced Server. Never merge their values.
8. Store formulas as reviewed structured expressions; never execute formula strings imported from a source.

## Patch 2.2.23 (2026-11-11)

Three community patch references agree that Original Server patch 2.2.23 was released on 2026-11-11:
- https://liquipedia.net/mobilelegends/Patch_2.2.23
- https://mlbb.tools/patch-notes/2.2.23
- https://mlbbhub.com/patch-notes/original/2.2.23

This establishes a strong community-reported patch date, but the references are not an official Moonton publication. The structured numerical values presently transcribed are partial and labelled `reported`. See [data/patches/2.2.23.json](../data/patches/2.2.23.json). Do not tag all existing hero skill records as 2.2.23 merely because this patch is the current target.

## Import/licensing guardrails

See [skill-source-lock.json](../data/sources/skill-source-lock.json). Do not bulk-copy third-party code, text, images or datasets until the exact license and endpoint terms are confirmed. Preserve CC BY-SA attribution and share-alike requirements where applicable. Keep Moonton assets as references unless redistribution permission is clear.

## Current implementation status

This audit records source capabilities and policy. It does not claim that all hero skills have been imported, compared or verified. The next technical step is a permitted metadata snapshot from the Moonton endpoint, then a field-level diff against the existing Atlas hero catalog and the reviewed community datasets.
