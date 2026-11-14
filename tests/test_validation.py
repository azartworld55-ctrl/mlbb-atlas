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
