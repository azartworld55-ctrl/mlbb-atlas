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


## Concrete staleness checks

The inspected `data/heroes/layla.json` in Build Analyser declares `lastPatch: 1.8.80`, despite the repository having later commits. This is why its per-hero structure and formula DSL are useful, but its skill numbers cannot be assumed current for 2.2.23.


## First field-level comparison against the Atlas seed

A first automated-by-structure/manual-reviewed text comparison was completed for all 14 heroes named in the 2.2.23 community patch references. The report is [2.2.23-atlas-comparison.json](../data/research/patch-conflicts/2.2.23-atlas-comparison.json).

It found clear stale or conflicting records for Popol and Kupa, Xavier, Lunox, Masha and Lukas; missing/unclear numerical details for Freya, Gloo, Aldous, Atlas, Karrie and Kaja; a visual-only change for Kagura; a component-level damage-type question for Uranus; and missing structured transfer ratios for Melissa.

This is a first-pass text comparison of the Atlas seed (upstream revision 20260929) against community patch references. It is not a complete comparison against a fresh Moonton GMS response, nor a live-client verification. Conflicts are recorded as research findings and have **not** been silently applied to canonical hero data.


## Second-stage catalogue comparison (2026-11-14)

The current Atlas hero catalogue was compared against Achedon's `src/data/game/skills.json` on branch `develop`, using normalized hero names/slugs and skill-name matching. Results are recorded in [skill-source-comparison-achedon.json](../data/research/skill-source-comparison-achedon.json).

Observed counts:
- Atlas: 133 heroes, 590 skill records.
- Achedon: 134 hero keys, 627 skill records.
- 133 Atlas heroes matched to Achedon by slug/name.
- 117 heroes have equal skill-record counts.
- 20 heroes have skill-name or count differences.
- Achedon contains an additional `dori` key absent from Atlas.
- 586 skill names matched across the matched hero sets.

These are catalogue-structure differences, not confirmed gameplay changes. Multi-form heroes can be represented differently (e.g. separate forms, weapon modes, or sub-skills); never reconcile by array index alone. The report stores only names/counts, not Wiki descriptions. Achedon states Wiki-derived data is CC BY-SA; preserve attribution and share-alike terms if any adapted Wiki text is later redistributed.

## Moonton GMS snapshot tooling

A local-only fetcher is available at `scripts/fetch_moonton_skills.py`. It follows the request shape observed in the public warungerik scraper, extracts hero/skill metadata without downloading images, and writes a local snapshot under the ignored `data/imports/moonton/` directory. The endpoint is undocumented and may change. A live POST was successfully executed by GitHub Actions on 2026-11-14: the response contained 133 heroes and 622 skill records. The first report found 15 heroes with catalogue count/name differences versus Atlas. The raw Moonton snapshot remains local to the runner and is not committed or uploaded. A follow-up comparator now emits skill IDs, group, cooldown/cost text and numeric tokens (not full descriptions) for the 15 conflict heroes, plus field-level numeric/cooldown differences where names match. This is a review aid only: the endpoint response does not expose a verified Original Server patch identifier, and numeric tokens are not interpreted as verified damage formulas.

Run:
```bash
python scripts/fetch_moonton_skills.py
python scripts/compare_skill_sources.py --achedon --moonton data/imports/moonton/skills-latest.json
```

The comparison tool does not copy full Wiki descriptions or infer damage formulas. It reports only metadata identity/name/count differences. Raw Moonton snapshots remain local pending a clear redistribution permission review.
