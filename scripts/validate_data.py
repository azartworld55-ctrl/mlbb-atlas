"""Validate canonical catalogues and patch-versioned skill parameter records."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECTIONS = ("heroes", "items", "emblems", "spells")
ERRORS: list[str] = []


def fail(message: str) -> None:
    ERRORS.append(message)


def validate_skill_version_records(records: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(records, list):
        return ["skill_versions: top-level value must be an array"]

    seen: set[str] = set()
    allowed_kinds = {"base_damage", "scaling", "cooldown", "resource_cost",
                     "duration", "slow", "heal", "shield", "other"}
    for index, record in enumerate(records):
        label = f"skill_versions[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{label}: record must be an object")
            continue
        for field in ("record_id", "hero_id", "skill_id", "skill_name",
                      "patch", "parameters", "verification", "sources"):
            if field not in record:
                errors.append(f"{label}: missing {field!r}")
        record_id = record.get("record_id")
        if not isinstance(record_id, str) or not record_id:
            errors.append(f"{label}: record_id must be a non-empty string")
        elif record_id in seen:
            errors.append(f"{label}: duplicate record_id {record_id!r}")
        else:
            seen.add(record_id)

        patch = record.get("patch")
        if not isinstance(patch, dict):
            errors.append(f"{label}: patch must be an object")
        elif not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+[a-z]?", str(patch.get("version", ""))):
            errors.append(f"{label}: invalid patch version")
        elif patch.get("channel") not in {"original_server", "advanced_server", None}:
            errors.append(f"{label}: invalid patch channel")

        parameters = record.get("parameters")
        if not isinstance(parameters, list) or not parameters:
            errors.append(f"{label}: parameters must be a non-empty array")
            parameters = []
        for p_index, parameter in enumerate(parameters):
            p_label = f"{label}.parameters[{p_index}]"
            if not isinstance(parameter, dict):
                errors.append(f"{p_label}: parameter must be an object")
                continue
            for field in ("key", "kind", "values_by_skill_level", "value_semantics", "level_labels"):
                if field not in parameter:
                    errors.append(f"{p_label}: missing {field!r}")
            if parameter.get("kind") not in allowed_kinds:
                errors.append(f"{p_label}: invalid parameter kind")
            values = parameter.get("values_by_skill_level")
            labels = parameter.get("level_labels")
            if not isinstance(values, list) or not values or any(
                isinstance(value, bool) or not isinstance(value, (int, float)) for value in values
            ):
                errors.append(f"{p_label}: values_by_skill_level must be a non-empty numeric array")
                values = []
            if not isinstance(labels, list) or len(labels) != len(values):
                errors.append(f"{p_label}: level_labels must match the values array length")
            semantics = parameter.get("value_semantics")
            if semantics not in {"fixed", "endpoints", "per_level"}:
                errors.append(f"{p_label}: invalid value_semantics")
            elif semantics == "fixed" and len(values) != 1:
                errors.append(f"{p_label}: fixed values must contain exactly one value")
            elif semantics == "endpoints" and len(values) != 2:
                errors.append(f"{p_label}: endpoints must contain exactly two values")

        verification = record.get("verification")
        if not isinstance(verification, dict) or verification.get("status") not in {
            "reported", "experimental", "verified", "unverified"
        }:
            errors.append(f"{label}: invalid verification status")
        sources = record.get("sources")
        if not isinstance(sources, list) or not sources:
            errors.append(f"{label}: at least one source is required")
        elif any(not isinstance(source, dict) or not source.get("url") for source in sources):
            errors.append(f"{label}: every source must include a URL")
    return errors


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
            for required in ("source", "source_repository", "source_revision", "retrieved_at", "confidence"):
                if not provenance.get(required):
                    fail(f"{label}: provenance missing {required!r}")
            # A Git blob SHA exists only for files stored in a Git repository.
            # Web pages (for example Liquipedia and METAMMO) are identified by
            # their URL and retrieval metadata instead; do not invent a SHA.
            source_url = str(provenance.get("source", ""))
            if "github.com/" in source_url or "gitlab.com/" in source_url:
                if not provenance.get("source_commit_blob_sha"):
                    fail(f"{label}: Git provenance missing 'source_commit_blob_sha'")
            if provenance.get("confidence") not in {"verified", "reported", "experimental"}:
                fail(f"{label}: invalid confidence label")
            if collection == "heroes" and not isinstance(record.get("skills"), list):
                fail(f"{label}: skills must be an array")
            if collection == "items" and not isinstance(record.get("modifiers"), list):
                fail(f"{label}: modifiers must be an array")
        print(f"{collection}: {len(records)} records")

    skill_path = ROOT / "data" / "skill_versions" / "current.json"
    try:
        skill_records = json.loads(skill_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"data/skill_versions/current.json: cannot read valid JSON: {exc}")
    else:
        ERRORS.extend(validate_skill_version_records(skill_records))
        print(f"skill_versions: {len(skill_records) if isinstance(skill_records, list) else 0} records")

    if ERRORS:
        print("\nValidation errors:")
        for error in ERRORS:
            print(f"- {error}")
        return 1
    print("All canonical datasets passed validation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
