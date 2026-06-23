import os
import time
import uuid

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8001")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "M34g4n123")
TEST_FULL_NAME = os.getenv("TEST_FULL_NAME", "Pytest User")
TIMEOUT = 20

def unique_email(prefix: str = "pytest") -> str:
    return f"automationfunding+{prefix}-{uuid.uuid4().hex[:10]}@gmail.com"

@pytest.fixture(scope="session")
def base_url() -> str:
    deadline = time.time() + 60
    last_error = None
    while time.time() < deadline:
        try:
            r = requests.get(f"{BASE_URL}/docs", timeout=5)
            if r.status_code == 200:
                return BASE_URL
        except Exception as exc:
            last_error = exc
        time.sleep(2)
    raise RuntimeError(f"API did not become ready at {BASE_URL}. Last error: {last_error}")

@pytest.fixture()
def registered_user(base_url: str):
    email = unique_email("registered")
    payload = {
        "email": email,
        "full_name": TEST_FULL_NAME,
        "password": TEST_PASSWORD,
    }
    response = requests.post(
        f"{base_url}/api/v1/auth/register",
        json=payload,
        headers={"accept": "application/json"},
        timeout=TIMEOUT,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    return {
        "email": email,
        "password": TEST_PASSWORD,
        "full_name": TEST_FULL_NAME,
        "register": data,
    }

@pytest.fixture()
def access_token(base_url: str, registered_user: dict) -> str:
    response = requests.post(
        f"{base_url}/api/v1/auth/login",
        data={"username": registered_user["email"], "password": registered_user["password"]},
        headers={"accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"},
        timeout=TIMEOUT,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    return data["access_token"]

@pytest.fixture()
def auth_headers(access_token: str) -> dict:
    return {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
