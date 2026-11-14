# Data policy

## Confidence labels
- **verified** — confirmed against a primary source or repeatable documented test.
- **reported** — taken from a named secondary source, not independently confirmed.
- **experimental** — a hypothesis or measurement under limited test conditions.

Never publish an unlabelled estimate as an exact in-game value.

## Required metadata
Every hero, item, emblem, spell, skill or patch record needs a stable ID, name, game version and provenance (source, retrieval timestamp and confidence). Note mode, platform, level, equipment and test conditions where relevant.

## Scaling and damage
Store per-level values explicitly or represent formulas as structured terms. Never execute formula strings from dataset files. Implement evaluation in reviewed code with tests.

For damage experiments record attacker/target stats, skill level, equipment, emblem, spell, defenses, buffs/debuffs, mode, patch and repeatable procedure.

## Third-party material
Before importing code, datasets, text or images, inspect the exact license and terms, preserve notices, record upstream commit/release and retrieval date, and distinguish original Atlas code from imported material. Game trademarks and artwork are not covered by this repository's MIT license.
