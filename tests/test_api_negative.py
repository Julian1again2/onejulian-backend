import requests

from conftest import TEST_FULL_NAME, TEST_PASSWORD, unique_email

TIMEOUT = 20

def test_bad_login_returns_401(base_url, registered_user):
    response = requests.post(
        f"{base_url}/api/v1/auth/login",
        data={"username": registered_user["email"], "password": "wrongpassword"},
        headers={"accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"},
        timeout=TIMEOUT,
    )
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Incorrect email or password"

def test_protected_route_without_token_returns_401(base_url):
    response = requests.get(
        f"{base_url}/api/v1/clients/me",
        headers={"accept": "application/json"},
        timeout=TIMEOUT,
    )
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Not authenticated"

def test_protected_route_with_bad_token_returns_401(base_url):
    response = requests.get(
        f"{base_url}/api/v1/clients/me",
        headers={"accept": "application/json", "Authorization": "Bearer not-a-real-token"},
        timeout=TIMEOUT,
    )
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Could not validate credentials"

def test_invalid_delivery_payload_returns_422(base_url, auth_headers):
    response = requests.post(
        f"{base_url}/api/v1/deliveries/",
        json={"description": "missing required title"},
        headers={**auth_headers, "Content-Type": "application/json"},
        timeout=TIMEOUT,
    )
    assert response.status_code == 422, response.text
    detail = response.json()["detail"]
    assert any(item["loc"][-1] == "title" for item in detail)

def test_nonexistent_delivery_returns_404(base_url, auth_headers):
    response = requests.get(
        f"{base_url}/api/v1/deliveries/999999",
        headers=auth_headers,
        timeout=TIMEOUT,
    )
    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "Delivery not found"

def test_duplicate_registration_returns_conflict_or_validation(base_url):
    email = unique_email("duplicate")
    payload = {"email": email, "full_name": TEST_FULL_NAME, "password": TEST_PASSWORD}

    first = requests.post(
        f"{base_url}/api/v1/auth/register",
        json=payload,
        headers={"accept": "application/json"},
        timeout=TIMEOUT,
    )
    assert first.status_code == 201, first.text

    second = requests.post(
        f"{base_url}/api/v1/auth/register",
        json=payload,
        headers={"accept": "application/json"},
        timeout=TIMEOUT,
    )
    assert second.status_code in (400, 409, 422), second.text

def test_policy_evaluate_sparse_payload_returns_decision(base_url, auth_headers):
    response = requests.post(
        f"{base_url}/api/v1/policy/evaluate",
        json={"type": "payment"},
        headers={**auth_headers, "Content-Type": "application/json"},
        timeout=TIMEOUT,
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert "decision" in body
    assert "rule_version_id" in body

def test_policy_learn_sparse_payload_returns_rejected_candidate(base_url, auth_headers):
    response = requests.post(
        f"{base_url}/api/v1/policy/learn",
        json={"name": "missing fields"},
        headers={**auth_headers, "Content-Type": "application/json"},
        timeout=TIMEOUT,
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "rejected"
    assert body["approved"] is False
    assert "candidate" in body
