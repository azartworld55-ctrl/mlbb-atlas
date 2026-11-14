"""Compare Atlas skills with local Moonton and/or Achedon skill snapshots.

Only names, counts and source identifiers are written to the report; full skill
descriptions from community datasets are never copied into Atlas by this tool.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ATLAS_PATH = ROOT / "data/heroes/current.json"
ACHEDON_SKILLS_URL = "https://raw.githubusercontent.com/achedon12/mlbb/develop/src/data/game/skills.json"
MOONTON_PATH = ROOT / "data/imports/moonton/skills-latest.json"


def normalize(value: Any) -> str:
    text = str(value or "").lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_achedon_skills() -> dict[str, Any]:
    request = urllib.request.Request(
        ACHEDON_SKILLS_URL,
        headers={"User-Agent": "MLBB-Atlas-research/0.1"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Achedon skills source is not a JSON object")
    return payload


def match_hero_key(hero: dict[str, Any], source: dict[str, Any]) -> str | None:
    wanted = {normalize(hero.get("slug")), normalize(hero.get("name"))}
    for key in source:
        if normalize(key) in wanted:
            return key
    return None


def compare_achedon(atlas: list[dict[str, Any]], skills: dict[str, Any]) -> dict[str, Any]:
    rows = []
    matched_heroes = 0
    matched_names = 0
    equal_skill_counts = 0
    atlas_total = sum(len(h.get("skills") or []) for h in atlas)
    source_total = sum(len(v) for v in skills.values() if isinstance(v, list))

    for hero in atlas:
        key = match_hero_key(hero, skills)
        atlas_skills = hero.get("skills") if isinstance(hero.get("skills"), list) else []
        if key is None:
            rows.append({
                "hero": hero.get("name"),
                "status": "missing_in_achedon",
                "atlas_skill_count": len(atlas_skills),
                "achedon_skill_count": 0,
                "atlas_only_skill_names": [s.get("name") for s in atlas_skills if isinstance(s, dict)],
                "achedon_only_skill_names": [],
            })
            continue

        matched_heroes += 1
        source_skills = skills.get(key) if isinstance(skills.get(key), list) else []
        atlas_names = {normalize(s.get("name")): s.get("name") for s in atlas_skills if isinstance(s, dict)}
        source_names = {normalize(s.get("name")): s.get("name") for s in source_skills if isinstance(s, dict)}
        common = set(atlas_names) & set(source_names)
        matched_names += len(common)
        if len(atlas_skills) == len(source_skills):
            equal_skill_counts += 1
        atlas_only = [atlas_names[n] for n in sorted(set(atlas_names) - set(source_names))]
        source_only = [source_names[n] for n in sorted(set(source_names) - set(atlas_names))]
        if atlas_only or source_only or len(atlas_skills) != len(source_skills):
            rows.append({
                "hero": hero.get("name"),
                "status": "skill_name_or_count_difference",
                "atlas_skill_count": len(atlas_skills),
                "achedon_skill_count": len(source_skills),
                "atlas_only_skill_names": atlas_only,
                "achedon_only_skill_names": source_only,
            })

    atlas_keys = {normalize(h.get("slug")) for h in atlas} | {normalize(h.get("name")) for h in atlas}
    source_only_heroes = [key for key in skills if normalize(key) not in atlas_keys]
    return {
        "source": "achedon12/mlbb src/data/game/skills.json",
        "source_url": ACHEDON_SKILLS_URL,
        "source_data_license": "CC BY-SA as stated by source repository README; descriptions are not copied into this report.",
        "atlas_hero_count": len(atlas),
        "source_hero_count": len(skills),
        "matched_hero_count": matched_heroes,
        "atlas_skill_record_count": atlas_total,
        "source_skill_record_count": source_total,
        "matched_skill_name_count": matched_names,
        "heroes_with_equal_skill_counts": equal_skill_counts,
        "heroes_with_differences": len(rows),
        "source_only_hero_keys": source_only_heroes,
        "differences": rows,
    }


def numeric_tokens(value: Any) -> list[str]:
    """Return numeric literals only; do not republish source descriptions."""
    if not isinstance(value, str):
        return []
    tokens = re.findall(r"(?<![A-Za-z])\d+(?:\.\d+)?\s*(?:%|s|ms|x)?", value, flags=re.I)
    return list(dict.fromkeys(re.sub(r"\s+", "", token) for token in tokens))


def parse_cooldown_cost(value: Any) -> tuple[str | None, str | None]:
    """Parse the GMS display string into comparable cooldown and mana-cost values."""
    if not isinstance(value, str):
        return None, None
    cooldown = re.search(r"\bCD\s*:\s*(\d+(?:\.\d+)?)", value, flags=re.I)
    mana = re.search(r"\bMana\s*Cost\s*:\s*(\d+(?:\.\d+)?)", value, flags=re.I)
    return (
        str(float(cooldown.group(1))).rstrip("0").rstrip(".") if cooldown else None,
        str(float(mana.group(1))).rstrip("0").rstrip(".") if mana else None,
    )


def comparable_number(value: Any) -> str | None:
    if value is None or str(value).strip().lower() in {"", "null", "none"}:
        return None
    try:
        return str(float(str(value).strip())).rstrip("0").rstrip(".")
    except ValueError:
        return str(value).strip()


def compare_moonton(atlas: list[dict[str, Any]], snapshot: dict[str, Any]) -> dict[str, Any]:
    source_heroes = snapshot.get("heroes")
    if not isinstance(source_heroes, list):
        raise ValueError("Moonton snapshot has no heroes array")
    by_id = {str(h.get("id")): h for h in atlas}
    by_name = {normalize(h.get("name")): h for h in atlas}
    matched = 0
    rows = []
    source_skill_total = 0
    for source_hero in source_heroes:
        atlas_hero = by_id.get(str(source_hero.get("hero_id"))) or by_name.get(normalize(source_hero.get("name")))
        source_skills = source_hero.get("skills") if isinstance(source_hero.get("skills"), list) else []
        source_skill_total += len(source_skills)
        if atlas_hero is None:
            rows.append({"hero": source_hero.get("name"), "status": "hero_not_matched_to_atlas"})
            continue
        matched += 1
        atlas_skills = [s for s in (atlas_hero.get("skills") or []) if isinstance(s, dict)]
        source_skills = [s for s in source_skills if isinstance(s, dict)]
        atlas_by_name: dict[str, list[dict[str, Any]]] = {}
        source_by_name: dict[str, list[dict[str, Any]]] = {}
        for skill in atlas_skills:
            atlas_by_name.setdefault(normalize(skill.get("name")), []).append(skill)
        for skill in source_skills:
            source_by_name.setdefault(normalize(skill.get("name")), []).append(skill)
        missing = sorted(set(atlas_by_name) - set(source_by_name))
        added = sorted(set(source_by_name) - set(atlas_by_name))
        matched_skill_fields = []
        for key in sorted(set(atlas_by_name) & set(source_by_name)):
            # Multi-form heroes may repeat a skill name across GMS groups. Do not
            # guess which form maps to the single Atlas row.
            if len(atlas_by_name[key]) != 1 or len(source_by_name[key]) != 1:
                continue
            a = atlas_by_name[key][0]
            m = source_by_name[key][0]
            a_nums = numeric_tokens(a.get("description"))
            m_nums = numeric_tokens(m.get("description_clean"))
            m_cd, m_mana = parse_cooldown_cost(m.get("cooldown_cost"))
            a_cd = comparable_number(a.get("cooldown"))
            a_mana = comparable_number(a.get("resource_cost"))
            cooldown_diff = a_cd != m_cd and (a_cd is not None or m_cd is not None)
            mana_diff = a_mana != m_mana and (a_mana is not None or m_mana is not None)
            if cooldown_diff or mana_diff or a_nums != m_nums:
                matched_skill_fields.append({
                    "skill_name": a.get("name"),
                    "atlas": {
                        "cooldown": a.get("cooldown"),
                        "resource_cost": a.get("resource_cost"),
                        "description_numeric_tokens": a_nums,
                    },
                    "moonton": {
                        "skill_id": m.get("skill_id"),
                        "group": m.get("group"),
                        "cooldown": m_cd,
                        "resource_cost": m_mana,
                        "description_numeric_tokens": m_nums,
                    },
                    "review_status": "numeric_or_cooldown_difference_needs_contextual_review",
                })
        if missing or added or len(atlas_skills) != len(source_skills) or matched_skill_fields:
            rows.append({
                "hero": atlas_hero.get("name"),
                "hero_id": source_hero.get("hero_id"),
                "status": "skill_name_count_or_field_difference",
                "atlas_skill_count": len(atlas_skills),
                "moonton_skill_count": len(source_skills),
                "atlas_only_skill_names": [atlas_by_name[k][0].get("name") for k in missing],
                "moonton_only_skill_names": [source_by_name[k][0].get("name") for k in added],
                "matched_skill_field_differences": matched_skill_fields,
                "moonton_skill_catalogue": [{
                    "skill_id": s.get("skill_id"),
                    "group": s.get("group"),
                    "name": s.get("name"),
                    "cooldown_cost": s.get("cooldown_cost"),
                    "description_numeric_tokens": numeric_tokens(s.get("description_clean")),
                } for s in source_skills],
            })
    return {
        "source": "Moonton GMS",
        "retrieved_at": (snapshot.get("source") or {}).get("retrieved_at"),
        "patch_version": None,
        "patch_version_note": "The GMS response does not expose a verified Original Server patch identifier.",
        "atlas_hero_count": len(atlas),
        "source_hero_count": len(source_heroes),
        "matched_hero_count": matched,
        "atlas_skill_record_count": sum(len(h.get("skills") or []) for h in atlas),
        "source_skill_record_count": source_skill_total,
        "heroes_with_differences": len(rows),
        "differences": rows,
        "note": "Detailed metadata diff for conflict heroes. Descriptions are not copied; numeric tokens are extracted for review and are not interpreted as verified damage formulas. Duplicate skill names across forms are not field-matched automatically.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--achedon", action="store_true", help="Fetch and compare Achedon wiki-derived skill names.")
    parser.add_argument("--moonton", type=Path, default=MOONTON_PATH, help="Optional local Moonton snapshot.")
    parser.add_argument("--output", type=Path, default=ROOT / "data/research/skill-source-comparison.json")
    args = parser.parse_args()

    atlas = read_json(ATLAS_PATH)
    report: dict[str, Any] = {
        "generated_from": str(ATLAS_PATH.relative_to(ROOT)),
        "atlas_hero_count": len(atlas),
        "comparisons": [],
        "warnings": [
            "A name/count mismatch is a review lead, not proof that either source is wrong.",
            "Achedon skill descriptions are Wiki-derived CC BY-SA; this report retains names/counts only.",
            "Moonton metadata is a live snapshot; the endpoint does not expose a verified Original Server patch identifier.",
        ],
    }

    if args.achedon:
        report["comparisons"].append(compare_achedon(atlas, fetch_achedon_skills()))
    if args.moonton.exists():
        report["comparisons"].append(compare_moonton(atlas, read_json(args.moonton)))

    if not report["comparisons"]:
        print("No source snapshot selected. Use --achedon and/or provide a Moonton snapshot.", file=sys.stderr)
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote comparison report: {args.output}")
    for comparison in report["comparisons"]:
        print(
            f"{comparison['source']}: matched heroes "
            f"{comparison['matched_hero_count']}/{comparison['atlas_hero_count']}; "
            f"heroes with differences: {comparison['heroes_with_differences']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
