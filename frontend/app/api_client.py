import requests
import streamlit as st


def get_api_url():
    """
    Read the backend URL from Streamlit secrets or environment.
    """
    try:
        api_url = st.secrets["BACKEND_API_URL"]
    except Exception:
        import os
        api_url = os.getenv("BACKEND_API_URL", "")

    return api_url.rstrip("/")


def login(username, password):
    api_url = get_api_url()

    if not api_url:
        raise RuntimeError("Backend API URL is not configured")

    response = requests.post(
        f"{api_url}/auth/login",
        json={
            "username": username,
            "password": password,
        },
        timeout=30,
    )

    if response.status_code == 401:
        return None

    response.raise_for_status()

    return response.json()


def get_current_user(token):
    api_url = get_api_url()

    response = requests.get(
        f"{api_url}/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
        timeout=30,
    )

    if response.status_code == 401:
        return None

    response.raise_for_status()

    return response.json()


def ask_question(token, question):
    api_url = get_api_url()

    response = requests.post(
        f"{api_url}/chat",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "question": question,
        },
        timeout=120,
    )

    if response.status_code == 401:
        return None

    response.raise_for_status()

    return response.json()