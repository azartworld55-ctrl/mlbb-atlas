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

## Source comparison

The source roles, limitations, licensing notes and field-level conflict policy are documented in [upstream-source-audit.md](upstream-source-audit.md). Source snapshots must retain their original IDs, raw text, retrieval date and revision. Similar-looking values from projects that share a Wiki/API ancestor are not independent corroboration.

## Current patch target: Original Server 2.2.23

As of 2026-11-14, three community patch references agree that patch 2.2.23 was released on 2026-11-11. This is enough to register 2.2.23 as the **reported research target**, not enough to call every existing skill record current or verified. The numerical patch record is partial and labelled `reported` in [data/patches/2.2.23.json](../data/patches/2.2.23.json). Official Moonton confirmation and live-client checks remain outstanding.

## Verification

Do not mark a skill verified merely because a calculator output looks plausible. Special cases such as defense, shields, true damage, damage caps, buffs, attack effects and multi-hit timing require separate tests. Prefer official patch notes and repeatable in-game tests; community sources are useful leads, not automatic verification.
