from scripts.fetch_moonton_skills import extract_records, normalize_records
from scripts.compare_skill_sources import compare_achedon, normalize


def test_moonton_nested_response_normalizes_skill_metadata():
    payload = {
        "data": {
            "records": [{
                "data": {
                    "hero_id": 1,
                    "hero": {
                        "data": {
                            "heroid": 1,
                            "name": "Miya",
                            "sortlabel": ["Marksman"],
                            "roadsortlabel": ["Gold Lane"],
                            "heroskilllist": [{
                                "skilllist": [{
                                    "skillid": 101,
                                    "skillname": "Moon Blessing",
                                    "skillcd&cost": "",
                                    "skilldesc": "<b>5%</b> Attack Speed",
                                    "skillicon": "https://example.invalid/icon.png",
                                }]
                            }],
                        }
                    },
                }
            }]
        }
    }
    records = extract_records(payload)
    heroes = normalize_records(records)
    assert len(heroes) == 1
    assert heroes[0]["hero_id"] == "1"
    assert heroes[0]["skills"][0]["skill_id"] == "101"
    assert heroes[0]["skills"][0]["description_clean"] == "5% Attack Speed"


def test_moonton_invalid_response_is_rejected():
    import pytest

    with pytest.raises(ValueError, match="data.records"):
        extract_records({"data": {}})


def test_achedon_comparison_reports_differences_without_descriptions():
    atlas = [{
        "slug": "miya",
        "name": "Miya",
        "skills": [{"name": "Moon Blessing"}, {"name": "Moon Arrow"}],
    }]
    source = {"miya": [{"name": "Moon Blessing", "description": "Do not copy this."}]}
    report = compare_achedon(atlas, source)
    assert report["matched_hero_count"] == 1
    assert report["matched_skill_name_count"] == 1
    assert report["heroes_with_differences"] == 1
    assert "Do not copy this." not in str(report)


def test_normalize_is_stable():
    assert normalize("Popol & Kupa") == "popol kupa"
