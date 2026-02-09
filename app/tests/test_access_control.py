def test_user_cannot_access_foreign_application(client):
    r = client.post(
        "/api/v1/auth/register",
        json={"email": "u1@example.com", "password": "pass12345"},
    )
    t1 = r.json()["access_token"]
    h1 = {"Authorization": f"Bearer {t1}"}

    r = client.post(
        "/api/v1/auth/register",
        json={"email": "u2@example.com", "password": "pass12345"},
    )
    t2 = r.json()["access_token"]
    h2 = {"Authorization": f"Bearer {t2}"}

    r = client.post(
        "/api/v1/applications",
        json={
            "company_name": "ACME",
            "position": "Backend Engineer",
            "status": "applied",
        },
        headers=h1,
    )
    app_id = r.json()["id"]

    r = client.get(f"/api/v1/applications/{app_id}", headers=h2)
    assert r.status_code == 404

    r = client.patch(
        f"/api/v1/applications/{app_id}",
        json={"status": "interview"},
        headers=h2,
    )
    assert r.status_code == 404

    r = client.delete(f"/api/v1/applications/{app_id}", headers=h2)
    assert r.status_code == 404
