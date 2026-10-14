from app.storage import JsonStorage


def test_create_pin(client, pin_payload):
    r = client.post("/api/v1/pins/", json=pin_payload)
    assert r.status_code == 201
    assert r.json()["id"] == 1 and r.json()["user_id"] == pin_payload["user_id"]


def test_create_pin_unknown_user(client, pin_payload):
    pin_payload["user_id"] = 99
    assert client.post("/api/v1/pins/", json=pin_payload).status_code == 404


def test_create_pin_invalid_coordinates(client, pin_payload):
    pin_payload["latitude"] = 123
    assert client.post("/api/v1/pins/", json=pin_payload).status_code == 422


def test_create_pin_invalid_audio_url(client, pin_payload):
    pin_payload["audio_url"] = "not a url"
    assert client.post("/api/v1/pins/", json=pin_payload).status_code == 422


def test_list_pins(client, pin_payload):
    assert client.get("/api/v1/pins/").json() == []
    client.post("/api/v1/pins/", json=pin_payload)
    assert len(client.get("/api/v1/pins/").json()) == 1


def test_get_pin(client, pin_payload):
    client.post("/api/v1/pins/", json=pin_payload)
    r = client.get("/api/v1/pins/1")
    assert r.status_code == 200 and r.json()["title"] == pin_payload["title"]


def test_get_pin_not_found(client):
    assert client.get("/api/v1/pins/999").status_code == 404


def test_update_pin_partial(client, pin_payload):
    client.post("/api/v1/pins/", json=pin_payload)
    r = client.put("/api/v1/pins/1", json={"title": "Nouveau titre"})
    assert r.status_code == 200
    assert r.json()["title"] == "Nouveau titre"
    assert r.json()["latitude"] == pin_payload["latitude"]


def test_update_pin_not_found(client):
    assert client.put("/api/v1/pins/42", json={"title": "x"}).status_code == 404


def test_delete_pin(client, pin_payload):
    client.post("/api/v1/pins/", json=pin_payload)
    assert client.delete("/api/v1/pins/1").status_code == 204
    assert client.get("/api/v1/pins/1").status_code == 404


def test_delete_pin_not_found(client):
    assert client.delete("/api/v1/pins/999").status_code == 404


def test_storage_persists_to_json_file(client, pin_payload, tmp_path):
    client.post("/api/v1/pins/", json=pin_payload)
    reloaded = JsonStorage(tmp_path / "test_db.json")
    assert reloaded.get_pin_by_id(1)["title"] == pin_payload["title"]
