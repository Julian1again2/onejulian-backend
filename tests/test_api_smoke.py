import requests

TIMEOUT = 20

def test_register_login_and_me(base_url, registered_user, access_token, auth_headers):
    me = requests.get(f"{base_url}/api/v1/clients/me", headers=auth_headers, timeout=TIMEOUT)
    assert me.status_code == 200, me.text
    body = me.json()
    assert body["email"] == registered_user["email"]
    assert body["full_name"] == registered_user["full_name"]
    assert "id" in body

def test_delivery_crud_flow(base_url, auth_headers):
    create_payload = {
        "title": "Pytest Smoke Delivery",
        "description": "Created by pytest",
        "status": "pending",
    }
    create = requests.post(
        f"{base_url}/api/v1/deliveries/",
        json=create_payload,
        headers={**auth_headers, "Content-Type": "application/json"},
        timeout=TIMEOUT,
    )
    assert create.status_code == 201, create.text
    created = create.json()
    delivery_id = created["id"]
    assert created["title"] == create_payload["title"]
    assert created["status"] == "pending"

    listing = requests.get(f"{base_url}/api/v1/deliveries/", headers=auth_headers, timeout=TIMEOUT)
    assert listing.status_code == 200, listing.text
    listed = listing.json()
    assert any(item["id"] == delivery_id for item in listed)

    one = requests.get(f"{base_url}/api/v1/deliveries/{delivery_id}", headers=auth_headers, timeout=TIMEOUT)
    assert one.status_code == 200, one.text
    assert one.json()["id"] == delivery_id

    patch = requests.patch(
        f"{base_url}/api/v1/deliveries/{delivery_id}",
        json={"status": "completed", "description": "Updated by pytest"},
        headers={**auth_headers, "Content-Type": "application/json"},
        timeout=TIMEOUT,
    )
    assert patch.status_code == 200, patch.text
    patched = patch.json()
    assert patched["status"] == "completed"
    assert patched["description"] == "Updated by pytest"

    delete = requests.delete(f"{base_url}/api/v1/deliveries/{delivery_id}", headers=auth_headers, timeout=TIMEOUT)
    assert delete.status_code == 204, delete.text

    confirm = requests.get(f"{base_url}/api/v1/deliveries/{delivery_id}", headers=auth_headers, timeout=TIMEOUT)
    assert confirm.status_code == 404, confirm.text
    assert confirm.json()["detail"] == "Delivery not found"
