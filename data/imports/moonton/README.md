# Local Moonton skill metadata snapshot

This folder contains the local-only workflow for comparing Moonton GMS skill metadata. Raw snapshots are ignored by Git because the endpoint is undocumented and the reuse/redistribution terms for game data and assets have not been established.

From the repository root:

```bash
python scripts/fetch_moonton_skills.py
python scripts/compare_skill_sources.py --achedon
```

The first command sends a small paginated metadata request to the Moonton GMS endpoint used by the public `warungerik/MLBB-Hero-Scraper` project. It writes `skills-latest.json` locally. It does not download images. If Moonton changes the endpoint, the request fails visibly rather than writing an empty catalogue.

The second command fetches Achedon's Wiki-derived skill-name index in memory and compares it with Atlas. The report stores only hero/skill names and counts, not Wiki skill descriptions. Achedon states that Wiki-derived game data is CC BY-SA; any later redistribution of Wiki-derived text must comply with that license and attribution requirements.

To compare a previously fetched Moonton snapshot too:

```bash
python scripts/compare_skill_sources.py --achedon --moonton data/imports/moonton/skills-latest.json
```

Important:
- This is metadata comparison, not damage formula extraction.
- Hero IDs are matched first; normalized names are a fallback only and require review.
- A mismatch can mean a rename, grouping difference, revamp, or stale source. It is not automatically a correction.
- Do not publish raw Moonton snapshots or game assets until their applicable terms are reviewed.
