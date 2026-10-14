def test_create_user(client):
    r = client.post("/api/v1/users/", json={"username": "alice", "email": "alice@example.com"})
    assert r.status_code == 201
    assert r.json()["id"] == 1 and r.json()["username"] == "alice"


def test_create_user_duplicate_email(client, make_user):
    make_user("alice")
    r = client.post("/api/v1/users/", json={"username": "bob", "email": "alice@example.com"})
    assert r.status_code == 409


def test_create_user_duplicate_username(client, make_user):
    make_user("alice")
    r = client.post("/api/v1/users/", json={"username": "alice", "email": "x@example.com"})
    assert r.status_code == 409


def test_create_user_invalid_email(client):
    r = client.post("/api/v1/users/", json={"username": "alice", "email": "nope"})
    assert r.status_code == 422


def test_list_users(client, make_user):
    assert client.get("/api/v1/users/").json() == []
    make_user("alice")
    make_user("bob")
    assert len(client.get("/api/v1/users/").json()) == 2


def test_get_user(client, make_user):
    uid = make_user()
    assert client.get(f"/api/v1/users/{uid}").json()["email"] == "alice@example.com"


def test_get_user_not_found(client):
    assert client.get("/api/v1/users/99").status_code == 404


def test_update_user(client, make_user):
    uid = make_user()
    r = client.put(f"/api/v1/users/{uid}", json={"username": "alice2"})
    assert r.status_code == 200
    assert r.json()["username"] == "alice2" and r.json()["email"] == "alice@example.com"


def test_update_user_conflict(client, make_user):
    make_user("alice")
    bob = make_user("bob")
    assert client.put(f"/api/v1/users/{bob}", json={"username": "alice"}).status_code == 409


def test_update_user_not_found(client):
    assert client.put("/api/v1/users/99", json={"username": "abc"}).status_code == 404


def test_delete_user_cascades_pins(client, pin_payload):
    client.post("/api/v1/pins/", json=pin_payload)
    assert client.delete(f"/api/v1/users/{pin_payload['user_id']}").status_code == 204
    assert client.get("/api/v1/users/1").status_code == 404
    assert client.get("/api/v1/pins/").json() == []


def test_delete_user_not_found(client):
    assert client.delete("/api/v1/users/99").status_code == 404
