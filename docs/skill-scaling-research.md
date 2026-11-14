# Exact skill scaling research

The imported hero catalogue contains skill descriptions and metadata, but it does not provide a verified level-by-level formula set. Atlas must not present prose-derived estimates as exact values.

## Patch-scoped records

Skill values are versioned. Use `schema/skill-version.schema.json` for a complete skill snapshot and `data/research/skill-version-template.json` as its starting point. Keep the existing `skill-scaling-template.json` for raw controlled-test measurements.

A record applies only to its explicit game patch and server channel. Original Server and Advanced Server are separate tracks. When a balance patch changes a skill, add a new record; do not overwrite the old one. If patch applicability is unknown, leave the patch version null and do not label the values current.

## Capture procedure

For each skill, record the patch, hero level, skill level, attacker attributes, target attributes, equipment, emblem setup, battle spell, buffs/debuffs, mode, platform and a repeatable test procedure. Preserve raw observations before fitting a formula. Record base values separately from scaling coefficients and state whether scaling uses total or bonus attributes. Split multi-hit components when their values or conditions differ.

## Evidence states

- `reported`: transcribed from source text or a third-party dataset only.
- `experimental`: measured under stated conditions but not independently replicated.
- `verified`: replicated and checked against a primary source or controlled test.
- `unverified`: placeholder or insufficient evidence.

## Current source audit (2026-11-14)

The imported hero catalogue contains numeric text in skill descriptions, but it does not provide a reliable per-skill patch history or structured level-by-level values. Its upstream revision is dated 2026-09-29; that is not proof that every value matches the live client today.

A community patch tracker reports Original Server patch 2.2.23 dated 2026-11-11, while the official patch listing surfaced in this research still showed 2.2.16. Treat 2.2.23 as a candidate patch target only until confirmed against the live client or an official patch entry. Do not silently tag existing skill descriptions as 2.2.23.

## Verification

Do not mark a skill verified merely because a calculator output looks plausible. Special cases such as defense, shields, true damage, damage caps, buffs, attack effects and multi-hit timing require separate tests. Prefer official patch notes and repeatable in-game tests; community sources are useful leads, not automatic verification.
