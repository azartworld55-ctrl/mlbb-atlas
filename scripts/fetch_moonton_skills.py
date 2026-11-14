"""Fetch Moonton GMS hero/skill metadata into a local, untracked snapshot.

This intentionally stores descriptive metadata only. It does not infer damage
formulas, download images, or publish the response. The endpoint is undocumented
and may change; keep the response and retrieval metadata local for review.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_URL = "https://api.gms.moontontech.com/api/gms/source/2669606/2756564"
DEFAULT_OUTPUT = Path("data/imports/moonton/skills-latest.json")
USER_AGENT = "MLBB-Atlas-research/0.1 (non-commercial metadata comparison)"


def clean_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return html.unescape(re.sub(r"<[^>]*>", "", value)).strip()


def extract_records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    data = payload.get("data")
    records = data.get("records") if isinstance(data, dict) else None
    if not isinstance(records, list):
        raise ValueError("Moonton response does not contain data.records")
    return records


def normalize_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    heroes: list[dict[str, Any]] = []
    for record in records:
        raw = record.get("data") if isinstance(record, dict) else None
        if not isinstance(raw, dict):
            continue
        nested = raw.get("hero")
        hero_data = nested.get("data") if isinstance(nested, dict) else None
        if not isinstance(hero_data, dict):
            hero_data = raw

        hero_id = raw.get("hero_id") or hero_data.get("heroid")
        name = hero_data.get("name")
        if hero_id is None or not name:
            continue

        skills: list[dict[str, Any]] = []
        groups = hero_data.get("heroskilllist")
        if isinstance(groups, list):
            for group_index, group in enumerate(groups, start=1):
                skill_list = group.get("skilllist") if isinstance(group, dict) else None
                if not isinstance(skill_list, list):
                    continue
                for skill in skill_list:
                    if not isinstance(skill, dict) or not skill.get("skillname"):
                        continue
                    raw_description = skill.get("skilldesc") or ""
                    skills.append({
                        "skill_id": str(skill.get("skillid") or ""),
                        "group": group_index,
                        "name": str(skill["skillname"]).strip(),
                        "cooldown_cost": str(skill.get("skillcd&cost") or ""),
                        "description_raw": str(raw_description),
                        "description_clean": clean_text(raw_description),
                        "icon_url": str(skill.get("skillicon") or ""),
                    })

        heroes.append({
            "hero_id": str(hero_id),
            "name": str(name).strip(),
            "roles": hero_data.get("sortlabel") if isinstance(hero_data.get("sortlabel"), list) else [],
            "lanes": hero_data.get("roadsortlabel") if isinstance(hero_data.get("roadsortlabel"), list) else [],
            "skills": skills,
        })
    return heroes


def request_page(page_index: int, page_size: int, retries: int = 3) -> dict[str, Any]:
    body = {
        "pageSize": page_size,
        "pageIndex": page_index,
        "filters": [],
        "sorts": [{"data": {"field": "hero_id", "order": "desc"}, "type": "sequence"}],
        "fields": [],
        "object": [],
    }
    encoded = json.dumps(body).encode("utf-8")
    request = Request(
        API_URL,
        data=encoded,
        headers={
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
        method="POST",
    )
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with urlopen(request, timeout=35) as response:
                result = json.loads(response.read().decode("utf-8"))
            if not isinstance(result, dict):
                raise ValueError("Moonton API returned a non-object JSON response")
            return result
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"Moonton GMS request failed after {retries} attempts: {last_error}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--page-size", type=int, default=200)
    parser.add_argument("--max-pages", type=int, default=5)
    args = parser.parse_args()
    if not 1 <= args.page_size <= 200 or not 1 <= args.max_pages <= 20:
        parser.error("page-size must be 1..200 and max-pages must be 1..20")

    records: list[dict[str, Any]] = []
    page_counts: list[int] = []
    for page in range(1, args.max_pages + 1):
        payload = request_page(page, args.page_size)
        page_records = extract_records(payload)
        page_counts.append(len(page_records))
        records.extend(page_records)
        print(f"Moonton GMS page {page}: {len(page_records)} hero records")
        if len(page_records) < args.page_size:
            break
        time.sleep(0.5)

    heroes = normalize_records(records)
    if not heroes:
        print("No hero records were normalized; refusing to write an empty snapshot.", file=sys.stderr)
        return 1

    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    document = {
        "schema_version": 1,
        "source": {
            "name": "Moonton GMS",
            "endpoint": API_URL,
            "retrieved_at": timestamp,
            "request_page_size": args.page_size,
            "page_record_counts": page_counts,
            "raw_record_count": len(records),
            "normalized_hero_count": len(heroes),
            "confidence": "reported",
            "note": "Metadata snapshot only; not a patch confirmation and not a damage-formula dataset.",
        },
        "heroes": heroes,
    }
    serialized = json.dumps(document, ensure_ascii=False, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(serialized, encoding="utf-8")
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    print(f"Wrote {len(heroes)} heroes to {args.output}")
    print(f"SHA-256: {digest}")
    print("Snapshot is local and should not be committed or redistributed without reviewing Moonton terms.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
