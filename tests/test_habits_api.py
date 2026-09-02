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
    assert body["category"] == "General"
    assert body["target_per_week"] == 7
    assert body["completed_this_week"] == 0
    assert body["streak"] == 0
    assert body["completed_today"] is False
    assert body["completed_days"] == []


def test_create_habit_with_explicit_target_per_week(client):
    resp = client.post("/habits", json={"name": "Run", "target_per_week": 3})
    assert resp.status_code == 201
    assert resp.json()["target_per_week"] == 3


def test_create_habit_rejects_target_per_week_out_of_range(client):
    assert client.post("/habits", json={"name": "Run", "target_per_week": 0}).status_code == 422
    assert client.post("/habits", json={"name": "Run", "target_per_week": 8}).status_code == 422


def test_complete_habit_updates_completed_this_week(client):
    created = client.post("/habits", json={"name": "Run", "target_per_week": 3}).json()
    resp = client.post(f"/habits/{created['id']}/complete")
    assert resp.json()["completed_this_week"] == 1


def test_create_habit_with_explicit_category(client):
    resp = client.post("/habits", json={"name": "Run 5k", "category": "Health"})
    assert resp.status_code == 201
    assert resp.json()["category"] == "Health"


def test_create_habit_rejects_empty_name(client):
    resp = client.post("/habits", json={"name": ""})
    assert resp.status_code == 422


def test_create_habit_rejects_empty_category(client):
    resp = client.post("/habits", json={"name": "Read", "category": ""})
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


def test_list_habits_filters_by_category(client):
    client.post("/habits", json={"name": "Run 5k", "category": "Health"})
    client.post("/habits", json={"name": "Read", "category": "Learning"})

    resp = client.get("/habits", params={"category": "Health"})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["name"] == "Run 5k"


def test_list_categories_returns_distinct_sorted_categories(client):
    client.post("/habits", json={"name": "Run 5k", "category": "Health"})
    client.post("/habits", json={"name": "Stretch", "category": "Health"})
    client.post("/habits", json={"name": "Read", "category": "Learning"})

    resp = client.get("/habits/categories")
    assert resp.status_code == 200
    assert resp.json() == ["Health", "Learning"]


def test_list_categories_empty_when_no_habits(client):
    resp = client.get("/habits/categories")
    assert resp.status_code == 200
    assert resp.json() == []


def test_stats_empty_when_no_habits(client):
    resp = client.get("/habits/stats")
    assert resp.status_code == 200
    assert resp.json() == {
        "total_habits": 0,
        "completed_today": 0,
        "active_streaks": 0,
        "best_streak": 0,
        "total_completions": 0,
        "weekly_completion_rate": 0,
        "by_category": {},
    }


def test_stats_counts_habits_and_categories(client):
    client.post("/habits", json={"name": "Run 5k", "category": "Health"})
    client.post("/habits", json={"name": "Stretch", "category": "Health"})
    client.post("/habits", json={"name": "Read", "category": "Learning"})

    body = client.get("/habits/stats").json()

    assert body["total_habits"] == 3
    assert body["by_category"] == {"Health": 2, "Learning": 1}


def test_stats_reflects_completions_and_streaks(client):
    created = client.post("/habits", json={"name": "Run", "target_per_week": 2}).json()
    client.post(f"/habits/{created['id']}/complete")

    body = client.get("/habits/stats").json()

    assert body["completed_today"] == 1
    assert body["active_streaks"] == 1
    assert body["best_streak"] == 1
    assert body["total_completions"] == 1


def test_stats_weekly_completion_rate_is_a_percentage_of_targets(client):
    first = client.post("/habits", json={"name": "Run", "target_per_week": 2}).json()
    client.post("/habits", json={"name": "Read", "target_per_week": 2})
    client.post(f"/habits/{first['id']}/complete")

    body = client.get("/habits/stats").json()

    # 1 completion this week against a combined weekly target of 4.
    assert body["weekly_completion_rate"] == 25
