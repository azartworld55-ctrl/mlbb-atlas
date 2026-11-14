from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_meta_reports_imported_collections():
    response = client.get("/api/v1/meta")
    assert response.status_code == 200
    counts = response.json()["collections"]
    assert counts["heroes"] >= 100
    assert counts["items"] >= 50
    assert counts["emblems"] >= 1
    assert counts["spells"] == 12


def test_heroes_collection_and_search():
    response = client.get("/api/v1/heroes?search=miya")
    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert response.json()["data"][0]["name"] == "Miya"


def test_hero_role_and_lane_filters():
    assert client.get("/api/v1/heroes?role=Marksman").json()["count"] > 0
    assert client.get("/api/v1/heroes?lane=gold%20lane").json()["count"] > 0


def test_hero_detail_by_slug():
    response = client.get("/api/v1/heroes/miya")
    assert response.status_code == 200
    assert response.json()["name"] == "Miya"


def test_unknown_hero_is_404():
    assert client.get("/api/v1/heroes/not-a-real-hero").status_code == 404


def test_items_search_and_detail():
    response = client.get("/api/v1/items?search=Berserker")
    assert response.status_code == 200
    assert response.json()["count"] == 1
    item_id = response.json()["data"][0]["id"]
    assert client.get(f"/api/v1/items/{item_id}").status_code == 200


def test_emblems_endpoint():
    response = client.get("/api/v1/emblems")
    assert response.status_code == 200
    assert response.json()["count"] == 7


def test_spells_endpoint_returns_sourced_catalogue():
    response = client.get("/api/v1/spells")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 12
    assert {row["slug"] for row in payload["data"]} >= {"flicker", "execute", "retribution", "vengeance"}\n    sprint = next(row for row in payload["data"] if row["slug"] == "sprint")\n    assert sprint["cooldown_seconds"] == 75
    assert all(row["provenance"]["confidence"] == "reported" for row in payload["data"])


def test_homepage_served():
    response = client.get("/")
    assert response.status_code == 200
    assert "MLBB Atlas" in response.text



def test_calculator_evaluates_supplied_expression_only():
    response = client.post(
        "/api/v1/calculator/evaluate",
        json={
            "formula_id": "demo-skill",
            "game_patch": "2.2.23",
            "expression": {
                "op": "add",
                "args": [
                    {"const": 100},
                    {"op": "mul", "args": [{"stat": "physical_attack"}, {"const": 0.8}]},
                ],
            },
            "stats": {"physical_attack": 200},
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["value"] == 260
    assert payload["calculation_scope"] == "supplied_expression_only"
    assert payload["confidence"] == "user_supplied_unverified"
    assert "no in-game damage" in payload["note"]


def test_calculator_rejects_unknown_stat():
    response = client.post(
        "/api/v1/calculator/evaluate",
        json={"expression": {"stat": "unknown"}, "stats": {}},
    )
    assert response.status_code == 422


def test_calculator_rejects_invalid_operation_type():
    response = client.post(
        "/api/v1/calculator/evaluate",
        json={"expression": {"op": [], "args": [{"const": 1}, {"const": 2}]}, "stats": {}},
    )
    assert response.status_code == 422


def test_skill_versions_filter_by_hero_and_patch():
    response = client.get("/api/v1/skill-versions?hero_id=xavier&patch=2.2.23")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] >= 1
    assert all(row["hero_id"] == "xavier" for row in payload["data"])
    assert all(row["patch"]["version"] == "2.2.23" for row in payload["data"])


def test_skill_versions_filter_by_verification_status():
    response = client.get("/api/v1/skill-versions?verification_status=reported")
    assert response.status_code == 200
    assert response.json()["count"] >= 1
    assert all(row["verification"]["status"] == "reported" for row in response.json()["data"])


def test_skill_version_detail():
    records = client.get("/api/v1/skill-versions?hero_id=xavier").json()["data"]
    record_id = records[0]["record_id"]
    response = client.get(f"/api/v1/skill-versions/{record_id}")
    assert response.status_code == 200
    assert response.json()["record_id"] == record_id


def test_unknown_skill_version_is_404():
    assert client.get("/api/v1/skill-versions/not-a-record").status_code == 404

def test_matchup_preview_uses_selected_builds_and_sourced_skill_parameters():
    response = client.post(
        "/api/v1/calculator/matchup-preview",
        json={
            "attacker": {
                "hero_id": "xavier",
                "item_ids": ["a001"],
                "emblem_id": "mage",
                "spell_id": "flicker",
                "buffs": {"blue": True, "red": False},
                "total_magic_power": 100,
            },
            "defender": {
                "hero_id": "miya",
                "item_ids": ["a002"],
                "emblem_id": "tank",
                "spell_id": "aegis",
                "buffs": {"blue": False, "red": True},
                "physical_defense": 80,
                "magic_defense": 60,
            },
            "skill_record_id": "xavier-xavier-3-2.2.23-original",
            "endpoint": "high",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["attacker"]["hero"]["slug"] == "xavier"
    assert payload["attacker"]["items"][0]["slug"] == "berserker-s-fury"
    assert payload["attacker"]["spell"]["slug"] == "flicker"
    assert payload["attacker"]["buffs"] == {"blue": True, "red": False}
    assert payload["defender"]["hero"]["slug"] == "miya"
    assert payload["defender"]["spell"]["slug"] == "aegis"
    assert payload["defender"]["buffs"] == {"blue": False, "red": True}
    assert payload["damage_before_defense"] == 859
    assert payload["skill"]["patch"]["version"] == "2.2.23"
    assert payload["calculation_scope"] == "source_parameter_preview_before_defense"


def test_matchup_rejects_skill_from_other_attacker():
    response = client.post(
        "/api/v1/calculator/matchup-preview",
        json={
            "attacker": {"hero_id": "miya"},
            "defender": {"hero_id": "xavier"},
            "skill_record_id": "xavier-xavier-3-2.2.23-original",
        },
    )
    assert response.status_code == 422


def test_matchup_rejects_unknown_spell():
    response = client.post(
        "/api/v1/calculator/matchup-preview",
        json={
            "attacker": {"hero_id": "miya", "spell_id": "not-a-spell"},
            "defender": {"hero_id": "xavier"},
        },
    )
    assert response.status_code == 404
