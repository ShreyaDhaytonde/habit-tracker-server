def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_list_habits_empty(client):
    resp = client.get("/habits")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_habit(client):
    resp = client.post("/habits", json={"name": "Drink water"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Drink water"
    assert body["streak"] == 0
    assert body["completed_today"] is False
    assert body["completed_days"] == []


def test_create_habit_rejects_empty_name(client):
    resp = client.post("/habits", json={"name": ""})
    assert resp.status_code == 422


def test_complete_habit_marks_today_and_bumps_streak(client):
    created = client.post("/habits", json={"name": "Read"}).json()
    resp = client.post(f"/habits/{created['id']}/complete")
    assert resp.status_code == 200
    body = resp.json()
    assert body["completed_today"] is True
    assert body["streak"] == 1


def test_complete_habit_is_idempotent_same_day(client):
    created = client.post("/habits", json={"name": "Read"}).json()
    client.post(f"/habits/{created['id']}/complete")
    resp = client.post(f"/habits/{created['id']}/complete")
    assert resp.status_code == 200
    assert resp.json()["streak"] == 1


def test_complete_unknown_habit_404s(client):
    resp = client.post("/habits/999/complete")
    assert resp.status_code == 404


def test_list_habits_reflects_completion(client):
    created = client.post("/habits", json={"name": "Meditate"}).json()
    client.post(f"/habits/{created['id']}/complete")
    resp = client.get("/habits")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["completed_today"] is True


def test_delete_habit(client):
    created = client.post("/habits", json={"name": "Stretch"}).json()
    resp = client.delete(f"/habits/{created['id']}")
    assert resp.status_code == 204
    assert client.get("/habits").json() == []


def test_delete_unknown_habit_404s(client):
    resp = client.delete("/habits/999")
    assert resp.status_code == 404
