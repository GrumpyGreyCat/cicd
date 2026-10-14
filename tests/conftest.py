import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage import JsonStorage, get_storage


@pytest.fixture
def storage(tmp_path):
    """Base JSON vierge et isolée (fichier temporaire) pour chaque test."""
    return JsonStorage(tmp_path / "test_db.json")


@pytest.fixture
def client(storage):
    app.dependency_overrides[get_storage] = lambda: storage
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def make_user(client):
    def _make(username="alice"):
        r = client.post(
            "/api/v1/users/", json={"username": username, "email": f"{username}@example.com"}
        )
        return r.json()["id"]

    return _make


@pytest.fixture
def pin_payload(make_user):
    return {
        "title": "Chant des oiseaux",
        "description": "Enregistré au parc",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "audio_url": "https://example.com/audio/sample.mp3",
        "user_id": make_user(),
    }
