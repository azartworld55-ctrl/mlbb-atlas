# Exact skill scaling research

The imported hero catalogue contains skill descriptions and metadata, but it does not provide a verified level-by-level formula set. Atlas must not present prose-derived estimates as exact values.

## Capture procedure

For each skill, record the patch, hero level, skill level, attacker attributes, target attributes, equipment, emblem setup, battle spell, buffs/debuffs, mode, platform and a repeatable test procedure. Preserve raw observations before fitting a formula.

## Evidence states

- `reported`: source text or third-party dataset only.
- `experimental`: measured under stated conditions but not independently replicated.
- `verified`: replicated and checked against a primary source or controlled test.

## Storage

Use the template in `data/research/skill-scaling-template.json`. Store exact per-level arrays when the game exposes them. If a formula is derived from observations, store it using the structured expression format in [formula-format.md](formula-format.md), plus measurement samples and uncertainty notes.

Do not mark a skill verified merely because a calculator output looks plausible. Special cases such as defense, shields, true damage, damage caps, buffs, attack effects and multi-hit timing require separate tests.
