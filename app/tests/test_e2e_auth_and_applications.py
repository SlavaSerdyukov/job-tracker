def test_e2e_register_login_and_crud(client):
    r = client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "password": "pass12345"},
    )
    assert r.status_code == 201, r.text
    token = r.json()["access_token"]
    assert token

    headers = {"Authorization": f"Bearer {token}"}

    r = client.post(
        "/api/v1/applications",
        json={
            "company_name": "Google",
            "position": "Backend Engineer",
            "status": "applied",
        },
        headers=headers,
    )
    assert r.status_code == 201, r.text
    app_id = r.json()["id"]

    r = client.get("/api/v1/applications", headers=headers)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1

    r = client.patch(
        f"/api/v1/applications/{app_id}",
        json={"status": "interview"},
        headers=headers,
    )
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "interview"

    r = client.get("/api/v1/applications?status=interview", headers=headers)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["status"] == "interview"

    r = client.delete(f"/api/v1/applications/{app_id}", headers=headers)
    assert r.status_code == 204, r.text

    r = client.get("/api/v1/applications", headers=headers)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["total"] == 0
    assert data["items"] == []
