# Data sources and attribution

## Imported datasets

| Source | Imported content | License | Status |
|---|---|---|---|
| [p3hndrx/MLBB-API](https://github.com/p3hndrx/MLBB-API) | 133 heroes, 89 items, 7 emblems | MIT | Imported and normalized; records labelled `reported` |
| [MLBB-Hero-Scraper](https://github.com/warungerik/MLBB-Hero-Scraper) | Candidate hero/skill metadata collection workflow | MIT | Reference only; scraper code not copied |
| [MLBB Wiki API](https://github.com/ervin-sungkono/MLBB-API) | Potential cross-check for heroes, equipment and emblems | No license file found during review | Reference only; do not import code or data until licensing is clarified |
| [MLBB community repositories](https://github.com/topics/mlbb) | Candidate structured data and tooling | Varies | Inspect each repository separately |

## Provenance

The exact upstream file paths, blob SHAs, revision labels and import date are recorded in [upstream-lock.json](upstream-lock.json). Original upstream JSON snapshots are retained in `data/imports/p3hndrx/`. Attribution and the applicable MIT notice are in [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md).

Every canonical record includes its source URL, upstream blob SHA, source revision, retrieval date and confidence label. Imported data remains `reported` until independently checked against the relevant live-game patch.

## Important

A public repository or API is not automatically reusable. Do not copy material without checking its exact license and terms. Game trademarks, character art and other assets may remain the property of Moonton or other rights holders.
