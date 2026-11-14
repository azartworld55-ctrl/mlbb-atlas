# Data sources and attribution

## Imported datasets and research references

| Source | Role | License / terms | Status |
|---|---|---|---|
| [p3hndrx/MLBB-API](https://github.com/p3hndrx/MLBB-API) | Existing hero, item and emblem seed | MIT | Imported; records remain `reported` |
| [Linconius/MLBB-Build-Analyser](https://github.com/Linconius/MLBB-Build-Analyser) | Per-hero JSON structure, formula DSL and Git patch-history model | License not confirmed in this audit | Architecture reference only; do not copy code/data yet |
| [warungerik/MLBB-Hero-Scraper](https://github.com/warungerik/MLBB-Hero-Scraper) | Moonton GMS endpoint and skill metadata extraction workflow | Scraper code MIT; repository terms restrict use; endpoint/data redistribution terms unclear | Endpoint/schema reference only |
| [achedon12/mlbb](https://github.com/achedon12/mlbb) | Wiki/stats API synchronization approach and multilingual knowledge base | Code MIT; README identifies Wiki-derived game data as CC BY-SA; assets remain Moonton property | Schema/provenance reference; any data import needs CC BY-SA compliance |
| [MLBB Wiki](https://mobile-legends.fandom.com/wiki/MLBB_Wiki) | Skill descriptions and community-maintained historical details | CC BY-SA as stated by source project | Cross-check only; attribution/share-alike required |
| [Liquipedia MLBB patch notes](https://liquipedia.net/mobilelegends/Portal:Patches) | Patch chronology and community patch-note cross-check | Review source terms before copying content | Research reference |

## Skill-source audit

See [upstream-source-audit.md](../../docs/upstream-source-audit.md) for source capabilities, conflict resolution and licensing decisions. Exact retrieval notes and import status are in [skill-source-lock.json](skill-source-lock.json).

## Provenance

The exact upstream file paths, blob SHAs, revision labels and import date for the existing p3hndrx data are recorded in [upstream-lock.json](upstream-lock.json). Original upstream JSON snapshots are retained in `data/imports/p3hndrx/`. Attribution and the applicable MIT notice are in [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md).

Every canonical record includes its source URL, upstream blob SHA, source revision, retrieval date and confidence label. Imported data remains `reported` until independently checked against the relevant live-game patch.

## Important

A public repository or API is not automatically reusable. Do not copy material without checking its exact license and terms. Game trademarks, character art and other assets may remain the property of Moonton or other rights holders.
