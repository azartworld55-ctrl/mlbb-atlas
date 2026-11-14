"""Normalize the pinned p3hndrx source snapshots into Atlas collections.

Run from the repository root:
    python scripts/normalize_p3hndrx.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "imports" / "p3hndrx"
LOCK_PATH = ROOT / "data" / "sources" / "upstream-lock.json"
SOURCE_REPO = "p3hndrx/MLBB-API"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def slugify(value: str) -> str:
    return re.sub(r"(^-|-$)", "", re.sub(r"[^a-z0-9]+", "-", value.lower()))


def provenance(lock: dict[str, Any], key: str) -> dict[str, str]:
    source = lock["upstream_files"][key]
    return {
        "source": f"https://github.com/{SOURCE_REPO}/blob/main/{source['path']}",
        "source_repository": SOURCE_REPO,
        "source_commit_blob_sha": source["blob_sha"],
        "source_revision": str(source["revision"]),
        "retrieved_at": lock["imported_at"],
        "confidence": "reported",
        "notes": (
            "Imported from the upstream MIT-licensed dataset. Not independently "
            "verified against the live game; check patch applicability."
        ),
    }


def normalize_heroes(payload: dict[str, Any], lock: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for hero in payload.get("data", []):
        name = hero.get("hero_name")
        if not name or name == "None":
            continue
        slug = slugify(str(hero.get("uid") or name))
        skills = []
        for index, skill in enumerate(hero.get("skills") or [], start=1):
            skills.append({
                "id": str(skill.get("id") or f"{slug}-{index}"),
                "name": skill.get("skill_name"),
                "type": skill.get("type"),
                "icon_url": skill.get("skill_icon"),
                "cooldown": skill.get("cooldown"),
                "resource_cost": skill.get("manacost"),
                "description": skill.get("description"),
                "tags": skill.get("tags") or [],
            })
        result.append({
            "id": str(hero.get("mlid") or hero.get("id") or hero.get("uid")),
            "slug": slug,
            "name": name,
            "roles": [hero["class"]] if hero.get("class") else [],
            "lanes": [lane for lane in (hero.get("laning") or []) if lane],
            "assets": {
                "icon_reference": hero.get("hero_icon"),
                "portrait_url": hero.get("portrait"),
            },
            "release_year": hero.get("release_year") or None,
            "skills": skills,
            "provenance": provenance(lock, "heroes"),
        })
    return result


def normalize_items(payload: dict[str, Any], lock: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for item in payload.get("data", []):
        if not item.get("item_name"):
            continue
        details = (item.get("data") or [{}])[0]
        result.append({
            "id": str(item.get("id") or slugify(item["item_name"])),
            "slug": slugify(item["item_name"]),
            "name": item["item_name"],
            "category": item.get("item_category"),
            "tier": item.get("item_tier"),
            "icon_reference": item.get("icon"),
            "cost": details.get("cost"),
            "summary": details.get("summary"),
            "modifiers": details.get("modifiers") or [],
            "active": details.get("active") or [],
            "passive": details.get("passive") or [],
            "unique_passive": details.get("unique_passive") or [],
            "build_path": details.get("build_path") or [],
            "provenance": provenance(lock, "items"),
        })
    return result


def normalize_emblems(payload: dict[str, Any], lock: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for emblem in payload.get("data", []):
        if not emblem.get("emblem_name"):
            continue
        result.append({
            "id": str(emblem.get("id")),
            "slug": slugify(str(emblem.get("emblem_role") or emblem["emblem_name"])),
            "name": emblem["emblem_name"],
            "role": emblem.get("emblem_role"),
            "icon_reference": emblem.get("icon"),
            "modifiers": emblem.get("modifiers") or [],
            "provenance": provenance(lock, "emblems"),
        })
    return result


def write_collection(name: str, records: list[dict[str, Any]]) -> None:
    path = ROOT / "data" / name / "current.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{name}: wrote {len(records)} records")


def main() -> None:
    lock = read_json(LOCK_PATH)
    heroes = read_json(RAW_DIR / "hero-meta-final.json")
    items = read_json(RAW_DIR / "item-meta-final.json")
    emblems = read_json(RAW_DIR / "emblem-meta-final.json")
    write_collection("heroes", normalize_heroes(heroes, lock))
    write_collection("items", normalize_items(items, lock))
    write_collection("emblems", normalize_emblems(emblems, lock))


if __name__ == "__main__":
    main()
