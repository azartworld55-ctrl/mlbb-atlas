# Data import workflow

The current initial import is from the MIT-licensed `p3hndrx/MLBB-API` repository. Original upstream JSON snapshots are preserved in `data/imports/p3hndrx/`; the normalized Atlas collections are in `data/heroes/current.json`, `data/items/current.json` and `data/emblems/current.json`.

1. Check the upstream repository license and terms before every new import.
2. Fetch the upstream files and record their blob SHAs and revision metadata in `data/sources/upstream-lock.json`.
3. Normalize into the canonical schema without silently coercing mixed values (for example, percentage strings).
4. Attach provenance to every record.
5. Run JSON validation and tests.
6. Review changes against the current game patch before changing confidence from `reported` to `verified`.

Do not import artwork binaries unless rights and hosting terms have been reviewed. Keep external asset references as references.
