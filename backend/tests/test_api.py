from fastapi.testclient import TestClient

from app.main import app


def test_liveness():
    with TestClient(app) as client:
        response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_chat_requires_authentication():
    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json={"question": "What is the school policy?"},
        )

    assert response.status_code == 401


def test_me_requires_authentication():
    with TestClient(app) as client:
        response = client.get("/auth/me")

    assert response.status_code == 401