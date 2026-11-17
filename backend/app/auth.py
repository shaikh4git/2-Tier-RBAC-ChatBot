import os
import json
import bcrypt
import jwt

from datetime import datetime, timedelta, timezone


JWT_ALGORITHM = "HS256"
DEFAULT_TOKEN_EXPIRY_MINUTES = 30


def load_users():
    """Load users from the Kubernetes Secret environment variable."""

    users_json = os.getenv("CHATBOT_USERS_JSON", "{}")

    try:
        users = json.loads(users_json)

        if not isinstance(users, dict):
            raise ValueError("User configuration must be a JSON object")

        return users

    except (json.JSONDecodeError, ValueError) as exc:
        print(f"User configuration error: {exc}")
        return {}


def authenticate(username, password):
    """
    Authenticate a user using bcrypt.

    Returns authenticated user identity or None.
    """

    if not username or not password:
        return None

    users = load_users()

    username = username.strip().lower()
    user_record = users.get(username)

    if not isinstance(user_record, dict):
        return None

    password_hash = user_record.get("password_hash")

    if not isinstance(password_hash, str) or not password_hash:
        return None

    try:
        valid_password = bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )

    except (ValueError, TypeError):
        return None

    if not valid_password:
        return None

    return {
        "username": username,
        "department": user_record.get("department", ""),
        "roles": user_record.get("roles", []),
    }


def create_access_token(user, expires_delta=None):
    """
    Create a signed JWT for an authenticated user.

    The JWT signing secret must be supplied through JWT_SECRET_KEY.
    """

    secret_key = os.getenv("JWT_SECRET_KEY")

    if not secret_key:
        raise RuntimeError("JWT_SECRET_KEY is not configured")

    if not user or not user.get("username"):
        raise ValueError("A valid authenticated user is required")

    if expires_delta is None:
        expiry_minutes = int(
            os.getenv(
                "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
                DEFAULT_TOKEN_EXPIRY_MINUTES,
            )
        )
        expires_delta = timedelta(minutes=expiry_minutes)

    now = datetime.now(timezone.utc)

    payload = {
        "sub": user["username"],
        "department": user.get("department", ""),
        "roles": user.get("roles", []),
        "iat": now,
        "exp": now + expires_delta,
    }

    return jwt.encode(
        payload,
        secret_key,
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(token):
    """
    Verify JWT signature and expiry.

    Returns verified claims or None if the token is invalid.
    """

    secret_key = os.getenv("JWT_SECRET_KEY")

    if not secret_key or not token:
        return None

    try:
        return jwt.decode(
            token,
            secret_key,
            algorithms=[JWT_ALGORITHM],
        )

    except jwt.InvalidTokenError:
        return None
