import json

import bcrypt
import jwt

from app import auth


def test_authenticate_valid_user(monkeypatch):
    password = "TestPassword123!"

    password_hash = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt(),
    ).decode()

    users = {
        "john": {
            "password_hash": password_hash,
            "department": "Finance",
            "roles": ["Manager"],
        }
    }

    monkeypatch.setenv(
        "CHATBOT_USERS_JSON",
        json.dumps(users),
    )

    result = auth.authenticate(
        "john",
        password,
    )

    assert result["username"] == "john"
    assert result["department"] == "Finance"
    assert result["roles"] == ["Manager"]
    assert "password_hash" not in result


def test_authenticate_invalid_password(monkeypatch):
    password_hash = bcrypt.hashpw(
        b"CorrectPassword",
        bcrypt.gensalt(),
    ).decode()

    users = {
        "john": {
            "password_hash": password_hash,
            "department": "Finance",
            "roles": [],
        }
    }

    monkeypatch.setenv(
        "CHATBOT_USERS_JSON",
        json.dumps(users),
    )

    assert auth.authenticate(
        "john",
        "WrongPassword",
    ) is None


def test_authenticate_unknown_user(monkeypatch):
    monkeypatch.setenv(
        "CHATBOT_USERS_JSON",
        "{}",
    )

    assert auth.authenticate(
        "unknown",
        "password",
    ) is None


def test_token_uses_identity_only(monkeypatch):
    monkeypatch.setattr(
        auth,
        "JWT_SECRET_KEY",
        "test-secret-key",
    )

    user = {
        "username": "john",
        "department": "Finance",
        "roles": ["Manager"],
    }

    token = auth.create_access_token(user)

    payload = jwt.decode(
        token,
        "test-secret-key",
        algorithms=["HS256"],
    )

    assert payload["sub"] == "john"
    assert "roles" not in payload