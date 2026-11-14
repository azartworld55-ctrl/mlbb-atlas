"""Validate canonical JSON catalogues and required provenance metadata."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECTIONS = ("heroes", "items", "emblems", "spells")
ERRORS: list[str] = []


def fail(message: str) -> None:
    ERRORS.append(message)


def main() -> int:
    for collection in COLLECTIONS:
        path = ROOT / "data" / collection / "current.json"
        try:
            records = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            fail(f"{path.relative_to(ROOT)}: cannot read valid JSON: {exc}")
            continue

        if not isinstance(records, list):
            fail(f"{path.relative_to(ROOT)}: top-level value must be an array")
            continue

        seen: set[str] = set()
        for index, record in enumerate(records):
            label = f"{collection}[{index}]"
            if not isinstance(record, dict):
                fail(f"{label}: record must be an object")
                continue

            for required in ("id", "name", "provenance"):
                if not record.get(required):
                    fail(f"{label}: missing required field {required!r}")

            record_id = str(record.get("id", ""))
            if record_id in seen:
                fail(f"{label}: duplicate id {record_id!r}")
            seen.add(record_id)

            provenance = record.get("provenance")
            if not isinstance(provenance, dict):
                fail(f"{label}: provenance must be an object")
                continue
            for required in ("source", "source_repository", "source_commit_blob_sha",
                             "source_revision", "retrieved_at", "confidence"):
                if not provenance.get(required):
                    fail(f"{label}: provenance missing {required!r}")
            if provenance.get("confidence") not in {"verified", "reported", "experimental"}:
                fail(f"{label}: invalid confidence label")

            if collection == "heroes" and not isinstance(record.get("skills"), list):
                fail(f"{label}: skills must be an array")
            if collection == "items" and not isinstance(record.get("modifiers"), list):
                fail(f"{label}: modifiers must be an array")

        print(f"{collection}: {len(records)} records")

    if ERRORS:
        print("\nValidation errors:")
        for error in ERRORS:
            print(f"- {error}")
        return 1

    print("All canonical datasets passed validation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
