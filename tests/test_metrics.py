"""Dashboard / detail metrics and refresh API tests."""

import re


def _add_server_with_metrics(auth_client, client):
    auth_client.post(
        "/servers",
        data={
            "hostname": "localhost",
            "ssh_username": "monitor",
            "ssh_port": "22",
            "labels": "demo",
        },
    )
    listed = auth_client.get("/servers")
    match = re.search(rb'/servers/([a-f0-9]+)"', listed.data)
    assert match
    server_id = match.group(1).decode()

    client.post(
        "/api/ingest",
        json={
            "hostname": "localhost",
            "cpu_percent": 22.5,
            "memory": {"total_mb": 2048, "used_mb": 512, "percent": 25.0},
            "network": {"bytes_sent": 100, "bytes_recv": 200},
            "listening_ports": ["tcp/22", "tcp/5000"],
        },
        headers={"X-Agent-Token": "test-ingest-token"},
    )
    return server_id


def test_detail_page_shows_fixture_metrics(auth_client, client):
    server_id = _add_server_with_metrics(auth_client, client)
    page = auth_client.get(f"/servers/{server_id}")
    assert page.status_code == 200
    assert b"22.5%" in page.data
    assert b"tcp/22" in page.data


def test_metrics_api_requires_session(client, auth_client):
    server_id = _add_server_with_metrics(auth_client, client)
    # fresh client without session
    bare = client.application.test_client()
    response = bare.get(f"/api/metrics/{server_id}")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_metrics_api_returns_latest_for_auth_user(auth_client, client):
    server_id = _add_server_with_metrics(auth_client, client)
    response = auth_client.get(f"/api/metrics/{server_id}")
    assert response.status_code == 200
    body = response.get_json()
    assert body["metrics"]["cpu_percent"] == 22.5


def test_disabled_server_ingest_rejected(auth_client, client):
    server_id = _add_server_with_metrics(auth_client, client)
    auth_client.post(f"/servers/{server_id}/disable")
    response = client.post(
        "/api/ingest",
        json={"hostname": "localhost", "cpu_percent": 1},
        headers={"X-Agent-Token": "test-ingest-token"},
    )
    assert response.status_code == 404
