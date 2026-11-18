import json
import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from .config import (
    CHATBOT_USERS_JSON,
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
)


def load_users():
    """
    Load the user database from the CHATBOT_USERS_JSON environment variable.
    """
    raw_users = os.getenv(
        "CHATBOT_USERS_JSON",
        CHATBOT_USERS_JSON,
    )

    try:
        users = json.loads(raw_users)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "CHATBOT_USERS_JSON contains invalid JSON"
        ) from exc

    if not isinstance(users, dict):
        raise RuntimeError(
            "CHATBOT_USERS_JSON must contain a JSON object"
        )

    return {
        username.lower(): record
        for username, record in users.items()
    }


def authenticate(username, password):
    """
    Authenticate credentials against bcrypt password hashes.

    Returns a safe user object without the password hash.
    """
    if not username or not password:
        return None

    users = load_users()

    record = users.get(username.lower())

    if not record:
        return None

    password_hash = record.get("password_hash")

    if not password_hash:
        return None

    try:
        password_matches = bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return None

    if not password_matches:
        return None

    return {
        "username": username.lower(),
        "department": record.get("department", ""),
        "roles": record.get("roles", []),
    }


def create_access_token(user, expires_delta=None):
    """
    Create a signed JWT access token.
    """
    if not JWT_SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY is not configured")

    now = datetime.now(timezone.utc)

    expiry = expires_delta or timedelta(
        minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": user["username"],
        "iat": now,
        "exp": now + expiry,
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(token):
    """
    Validate and decode a JWT access token.
    """
    if not JWT_SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY is not configured")

    try:
        return jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
    except jwt.InvalidTokenError:
        return None


def get_current_user_from_token(token):
    """
    Validate the JWT and reload the user's current roles from the
    backend user database.

    The JWT is used only to establish identity. Role claims from the
    token are deliberately not trusted.
    """
    payload = decode_access_token(token)

    if not payload:
        return None

    username = payload.get("sub")

    if not username:
        return None

    users = load_users()

    record = users.get(username.lower())

    if not record:
        return None

    return {
        "username": username.lower(),
        "department": record.get("department", ""),
        "roles": record.get("roles", []),
    }