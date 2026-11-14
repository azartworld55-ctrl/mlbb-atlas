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
    assert counts["spells"] == 0


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


def test_spells_endpoint_is_empty_until_sourced():
    response = client.get("/api/v1/spells")
    assert response.status_code == 200
    assert response.json() == {"count": 0, "data": []}


def test_homepage_served():
    response = client.get("/")
    assert response.status_code == 200
    assert "MLBB Atlas" in response.text
