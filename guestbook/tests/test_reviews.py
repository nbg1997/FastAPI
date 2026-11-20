import pytest
from fastapi.testclient import TestClient

from main import create_app


@pytest.fixture
def client(database_path):
    with TestClient(create_app(database_path)) as test_client:
        yield test_client


def test_create_and_list_reviews(client):
    assert client.get("/reviews").json() == []

    response = client.post(
        "/reviews",
        json={"author": "  Иван  ", "text": "  Очень полезное занятие!  "},
    )
    assert response.status_code == 201
    review = response.json()
    assert review == {
        "id": 1,
        "author": "Иван",
        "text": "Очень полезное занятие!",
    }
    assert client.get("/reviews").json() == [review]


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"author": "Иван"},
        {"text": "Хорошо"},
        {"author": "", "text": "Норм"},
        {"author": "   ", "text": "Норм"},
        {"author": "Иван", "text": ""},
        {"author": "Иван", "text": "\t\n  "},
        {"author": "x" * 61, "text": "Норм"},
        {"author": "Иван", "text": "x" * 501},
        {"author": 123, "text": "Норм"},
        {"author": "Иван", "text": None},
    ],
)
def test_invalid_review_is_rejected(client, payload):
    response = client.post("/reviews", json=payload)
    assert response.status_code == 422
    assert client.get("/reviews").json() == []


def test_filter_by_author_and_order(client):
    r1 = client.post("/reviews", json={"author": "Алиса", "text": "Первый отзыв"}).json()
    r2 = client.post("/reviews", json={"author": "Борис", "text": "Второй отзыв"}).json()
    r3 = client.post("/reviews", json={"author": "Алиса", "text": "Третий отзыв"}).json()

    assert client.get("/reviews").json() == [r3, r2, r1]
    assert client.get("/reviews?author=Алиса").json() == [r3, r1]
    assert client.get("/reviews?author=Борис").json() == [r2]
    assert client.get("/reviews?author=Неизвестный").json() == []


def test_get_single_and_delete_review(client):
    created = client.post("/reviews", json={"author": "Олег", "text": "Проверка"}).json()
    review_id = created["id"]

    assert client.get(f"/reviews/{review_id}").json() == created
    assert client.get("/reviews/999").status_code == 404

    delete_response = client.delete(f"/reviews/{review_id}")
    assert delete_response.status_code == 204
    assert delete_response.content == b""

    assert client.get(f"/reviews/{review_id}").status_code == 404
    assert client.delete(f"/reviews/{review_id}").status_code == 404
    assert client.get("/reviews").json() == []


@pytest.mark.parametrize("review_id", ["abc", "0", "-1"])
def test_review_id_validation(client, review_id):
    assert client.get(f"/reviews/{review_id}").status_code == 422
    assert client.delete(f"/reviews/{review_id}").status_code == 422


def test_database_survives_application_restart(database_path):
    with TestClient(create_app(database_path)) as first_client:
        saved = first_client.post(
            "/reviews",
            json={"author": "Мария", "text": "Сохраняется между запусками"},
        ).json()
    with TestClient(create_app(database_path)) as second_client:
        assert second_client.get("/reviews").json() == [saved]