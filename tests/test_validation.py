from scripts.validate_data import validate_provenance


def test_web_source_does_not_require_git_blob_sha():
    provenance = {
        "source": "https://metammo.com/mobile-legends-guide/battle-spells",
        "source_repository": "METAMMO battle spell guide",
        "source_revision": "2026-10-30",
        "retrieved_at": "2026-11-14",
        "confidence": "reported",
    }
    assert validate_provenance(provenance, "spells[0]") == []


def test_git_source_requires_blob_sha():
    provenance = {
        "source": "https://github.com/example/project/blob/main/data.json",
        "source_repository": "example/project",
        "source_revision": "main",
        "retrieved_at": "2026-11-14",
        "confidence": "reported",
    }
    errors = validate_provenance(provenance, "heroes[0]")
    assert "heroes[0]: Git provenance missing 'source_commit_blob_sha'" in errors


def test_git_source_with_blob_sha_passes():
    provenance = {
        "source": "https://github.com/example/project/blob/main/data.json",
        "source_repository": "example/project",
        "source_commit_blob_sha": "abc123",
        "source_revision": "main",
        "retrieved_at": "2026-11-14",
        "confidence": "reported",
    }
    assert validate_provenance(provenance, "heroes[0]") == []


def test_patch_2_2_23_updates_are_reflected_in_catalogues():
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    items = json.loads((root / "data/items/current.json").read_text(encoding="utf-8"))
    spells = json.loads((root / "data/spells/current.json").read_text(encoding="utf-8"))
    skills = json.loads((root / "data/skill_versions/current.json").read_text(encoding="utf-8"))
    patch = json.loads((root / "data/patches/2.2.23.json").read_text(encoding="utf-8"))

    antique = next(item for item in items if item["slug"] == "antique-cuirass")
    chastise = next(item for item in items if item["slug"] == "chastise-pauldron")
    assert "8%" in next(p for p in antique["unique_passive"] if p["unique_passive_name"] == "Deter")["description"]
    assert "80%" in next(p for p in chastise["unique_passive"] if p["unique_passive_name"] == "Chastise")["description"]
    assert antique["patch_updates"][0]["patch_version"] == "2.2.23"
    assert chastise["patch_updates"][0]["patch_version"] == "2.2.23"

    sprint = next(spell for spell in spells if spell["slug"] == "sprint")
    assert sprint["cooldown_seconds"] == 75
    assert sprint["patch_updates"][0]["before"] == 100
    assert sprint["patch_updates"][0]["after"] == 75

    masha_passive = next(record for record in skills if record["record_id"] == "masha-masha-1-2.2.23-original")
    assert next(p for p in masha_passive["parameters"] if p["key"] == "feral_claw_bonus_damage_base_percent")["values_by_skill_level"] == [2]
    assert next(p for p in masha_passive["parameters"] if p["key"] == "feral_state_hp_regen")["values_by_skill_level"] == [3, 6]

    melissa = next(record for record in skills if record["record_id"] == "melissa-melissa-3-2.2.23-original")
    assert next(p for p in melissa["parameters"] if p["key"] == "muddles_damage_transfer_ratio")["values_by_skill_level"] == [50, 60]
    assert next(p for p in melissa["parameters"] if p["key"] == "attack_effect_inheritance_ratio")["values_by_skill_level"] == [50, 60]

    assert patch["status"] == "community_reported_pending_official_confirmation"
    assert any(change.get("entity_type") == "item" and change.get("entity_id") == "d001" for change in patch["numeric_changes"])
    assert any(change.get("entity_type") == "emblem_talent" and change.get("entity_id") == "concussive-blast" for change in patch["numeric_changes"])
