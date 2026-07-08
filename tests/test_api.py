import math

from fastapi.testclient import TestClient

from exercise_store import exercise_store
from main import CACHE_CONTROL, app


client = TestClient(app)


def test_legacy_exercises_returns_full_dataset_with_cache_header():
    response = client.get("/exercises")

    assert response.status_code == 200
    assert response.headers["cache-control"] == CACHE_CONTROL
    exercises = response.json()
    assert len(exercises) == exercise_store.total_count
    assert "instructions" in exercises[0]


def test_legacy_exercise_by_id_returns_full_detail():
    expected = exercise_store.all()[0]

    response = client.get(f"/exercises/{expected['id']}")

    assert response.status_code == 200
    exercise = response.json()
    assert exercise["id"] == int(expected["id"])
    assert exercise["instructions"] == expected["instructions"]


def test_legacy_search_keeps_response_shape_and_pagination():
    response = client.get("/exercises/search/curl", params={"page": 1, "limit": 5})

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"exercises", "currentPage", "totalPages", "totalCount", "limit"}
    assert body["currentPage"] == 1
    assert body["limit"] == 5
    assert 0 < len(body["exercises"]) <= 5
    assert all("curl" in exercise["name"].lower() for exercise in body["exercises"])
    assert "instructions" in body["exercises"][0]


def test_v2_exercises_returns_paginated_summaries():
    response = client.get("/v2/exercises", params={"page": 1, "limit": 10})

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["limit"] == 10
    assert body["total"] == exercise_store.total_count
    assert body["totalPages"] == math.ceil(exercise_store.total_count / 10)
    assert len(body["items"]) == 10
    assert "instructions" not in body["items"][0]


def test_v2_exercises_clamps_page_and_limit():
    response = client.get("/v2/exercises", params={"page": 0, "limit": 0})

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["limit"] == 20

    response = client.get("/v2/exercises", params={"limit": 1000})
    body = response.json()
    assert body["limit"] == 100
    assert len(body["items"]) == 100


def test_v2_exercises_supports_search_and_combined_filters():
    sample = next(
        exercise
        for exercise in exercise_store.all()
        if "curl" in exercise["name"].lower()
    )

    response = client.get(
        "/v2/exercises",
        params={
            "q": "curl",
            "category": sample["category"].upper(),
            "level": sample["level"].upper(),
            "equipment": sample["equipment"].upper(),
            "muscle": sample["primaryMuscles"][0].upper(),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert all("curl" in exercise["name"].lower() for exercise in body["items"])
    assert all(exercise["category"] == sample["category"] for exercise in body["items"])
    assert all(exercise["level"] == sample["level"] for exercise in body["items"])
    assert all(exercise["equipment"] == sample["equipment"] for exercise in body["items"])
    assert all("instructions" not in exercise for exercise in body["items"])


def test_v2_exercises_empty_results_are_paginated():
    response = client.get("/v2/exercises", params={"q": "definitely-not-an-exercise"})

    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == 0
    assert body["totalPages"] == 1


def test_v2_exercise_detail_success_and_not_found():
    expected = exercise_store.all()[0]

    response = client.get(f"/v2/exercises/{expected['id']}")

    assert response.status_code == 200
    exercise = response.json()
    assert exercise["id"] == int(expected["id"])
    assert "instructions" in exercise

    response = client.get("/v2/exercises/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Exercise not found"}


def test_v2_meta_returns_filter_options():
    response = client.get("/v2/exercises/meta")

    assert response.status_code == 200
    body = response.json()
    assert body["totalCount"] == exercise_store.total_count
    assert body["levels"] == ["beginner", "expert", "intermediate"]
    assert "strength" in body["categories"]
    assert "dumbbell" in body["equipment"]
    assert "biceps" in body["muscles"]


def test_health_returns_count_and_data_hash():
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["exerciseCount"] == exercise_store.total_count
    assert len(body["dataHash"]) == 64
