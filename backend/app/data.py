"""Read-only access to the versioned JSON datasets."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"


def load_collection(name: str) -> list[dict[str, Any]]:
    allowed = {"heroes", "items", "emblems", "spells"}
    if name not in allowed:
        raise ValueError(f"Unknown collection: {name}")
    path = DATA_DIR / name / "current.json"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as stream:
        payload = json.load(stream)
    if not isinstance(payload, list):
        raise ValueError(f"{path} must contain a JSON array")
    return payload


def find_record(name: str, record_id: str) -> dict[str, Any] | None:
    for record in load_collection(name):
        if str(record.get("id")) == record_id or record.get("slug") == record_id:
            return record
    return None
