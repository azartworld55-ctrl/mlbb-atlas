from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_heroes_collection_shape():
    response = client.get("/api/v1/heroes")
    assert response.status_code == 200
    assert set(response.json()) == {"count", "data"}
    assert isinstance(response.json()["data"], list)


def test_unknown_hero_is_404():
    assert client.get("/api/v1/heroes/not-a-real-hero").status_code == 404


def test_homepage_served():
    response = client.get("/")
    assert response.status_code == 200
    assert "MLBB Atlas" in response.text
