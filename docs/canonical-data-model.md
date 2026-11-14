# Canonical data model

The canonical collections are JSON arrays under `data/<collection>/current.json`.

## Hero
`id`, `slug`, `name`, `roles[]`, `lanes[]`, `assets`, `skills[]`, `provenance`.

Each skill retains source-provided name, type, icon reference, cooldown, resource cost, description and tags. These values are reported upstream data, not exact level-by-level scaling.

Hero records may also contain `patch_updates[]`, an audit trail of explicitly applied patch-note changes. Each entry records the patch version, source URL, application date and changed fields. This audit trail does not replace the normalized versioned skill records defined by `schema/skill-version.schema.json`; create those only when skill rank, form, parameter kind and per-rank values have been mapped without ambiguity.

## Item
`id`, `slug`, `name`, `category`, `tier`, `cost`, `summary`, `modifiers[]`, passive/active effect arrays, build path and provenance.

## Emblem
`id`, `slug`, `name`, `role`, `modifiers[]`, `provenance`.

## Provenance
Every imported record includes source URL, source repository, source blob SHA, source revision, retrieval date, confidence and caveat notes. Keep confidence as `reported` until independently checked in-game or against a primary source.

## Important limitations
- Upstream item dataset revision is labelled `Current 2025`; do not assume it matches the November 2026 live patch.
- Hero skill descriptions are not a substitute for a verified skill formula or level scaling table.
- Values stored as strings are intentionally preserved where the source uses mixed numeric/percentage notation.
