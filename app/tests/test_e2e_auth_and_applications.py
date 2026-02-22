from datetime import UTC, datetime, timedelta


def test_e2e_register_login_and_crud(client):
    r = client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "password": "pass12345"},
    )
    assert r.status_code == 201, r.text
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    follow_up_at = (datetime.now(UTC) + timedelta(days=1)).isoformat()

    r = client.post(
        "/api/v1/applications",
        json={
            "company_name": "Google",
            "position": "Backend Engineer",
            "status": "applied",
            "recruiter_name": "Alex Recruiter",
            "recruiter_email": " Alex@Google.com ",
            "job_url": "https://example.com/job",
            "salary_range": "$150k-$180k",
            "location": "Remote",
            "follow_up_at": follow_up_at,
        },
        headers=headers,
    )
    assert r.status_code == 201, r.text
    created = r.json()
    app_id = created["id"]
    assert created["recruiter_name"] == "Alex Recruiter"
    assert created["recruiter_email"] == " Alex@Google.com "
    assert created["job_url"] == "https://example.com/job"
    assert created["salary_range"] == "$150k-$180k"
    assert created["location"] == "Remote"
    assert created["follow_up_at"] is not None

    r = client.post(
        "/api/v1/applications",
        json={
            "company_name": "Google",
            "position": "Backend Engineer",
            "status": "applied",
        },
        headers=headers,
    )
    assert r.status_code == 409, r.text
    assert r.json()["detail"]["conflicting_fields"] == [
        "company_name",
        "position",
    ]

    r = client.get("/api/v1/applications?page=1&page_size=20", headers=headers)
    assert r.status_code == 200, r.text
    data = r.json()
    assert sorted(data.keys()) == ["items", "page", "page_size", "total"]
    assert data["page"] == 1
    assert data["page_size"] == 20
    assert data["total"] == 1
    assert len(data["items"]) == 1

    r = client.get("/api/v1/applications?q=google", headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["total"] == 1

    r = client.get("/api/v1/applications?q=backend", headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["total"] == 1

    r = client.get("/api/v1/applications?q=alex@google.com", headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["total"] == 1

    r = client.patch(
        f"/api/v1/applications/{app_id}",
        json={"status": "offer"},
        headers=headers,
    )
    assert r.status_code == 422, r.text

    r = client.patch(
        f"/api/v1/applications/{app_id}",
        json={"status": "screening"},
        headers=headers,
    )
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "screening"

    next_follow_up_at = (
        datetime.now(UTC) + timedelta(days=2)
    ).isoformat()
    r = client.patch(
        f"/api/v1/applications/{app_id}",
        json={
            "follow_up_at": next_follow_up_at,
            "recruiter_email": "new.recruiter@google.com",
        },
        headers=headers,
    )
    assert r.status_code == 200, r.text
    assert r.json()["recruiter_email"] == "new.recruiter@google.com"
    assert r.json()["follow_up_at"] is not None

    r = client.get("/api/v1/applications/followups?days=7", headers=headers)
    assert r.status_code == 200, r.text
    followups = r.json()
    assert len(followups) == 1
    assert followups[0]["id"] == app_id

    r = client.patch(
        f"/api/v1/applications/{app_id}",
        json={"status": "interview"},
        headers=headers,
    )
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "interview"

    r = client.get(f"/api/v1/applications/{app_id}/timeline", headers=headers)
    assert r.status_code == 200, r.text
    timeline = r.json()
    assert len(timeline) >= 3
    event_types = [item["event_type"] for item in timeline]
    assert "status_change" in event_types
    assert "follow_up" in event_types
    assert "contact" in event_types

    r = client.get(
        "/api/v1/applications/analytics/recruiter-performance-v2",
        headers=headers,
    )
    assert r.status_code == 200, r.text
    recruiter_perf = r.json()["recruiters"]
    assert len(recruiter_perf) == 1
    assert recruiter_perf[0]["recruiter_email"] == "new.recruiter@google.com"
    assert recruiter_perf[0]["total"] == 1
    by_status = recruiter_perf[0]["by_status"]
    assert len(by_status) == 6
    by_status_map = {item["status"]: item["count"] for item in by_status}
    assert by_status_map["interview"] == 1
    assert by_status_map["applied"] == 0
    assert recruiter_perf[0]["last_contacted_at"] is None

    r = client.delete(f"/api/v1/applications/{app_id}", headers=headers)
    assert r.status_code == 204, r.text

    r = client.get("/api/v1/applications", headers=headers)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["total"] == 0
    assert data["items"] == []
