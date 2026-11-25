"""Agent collector and ingest API tests."""

from agent.collect import collect_all


def test_collect_all_keys():
    payload = collect_all("localhost")
    assert payload["hostname"] == "localhost"
    assert "cpu_percent" in payload
    assert {"total_mb", "used_mb", "percent"} <= set(payload["memory"])
    assert {"bytes_sent", "bytes_recv"} <= set(payload["network"])
    assert isinstance(payload["listening_ports"], list)


def test_ingest_rejects_missing_token(client):
    response = client.post("/api/ingest", json={"hostname": "localhost"})
    assert response.status_code == 401


def test_ingest_rejects_bad_token(client):
    response = client.post(
        "/api/ingest",
        json={"hostname": "localhost"},
        headers={"X-Agent-Token": "wrong"},
    )
    assert response.status_code == 401


def test_ingest_accepts_known_enabled_host(auth_client, client):
    auth_client.post(
        "/servers",
        data={
            "hostname": "localhost",
            "ssh_username": "monitor",
            "ssh_port": "22",
        },
    )
    payload = {
        "hostname": "localhost",
        "cpu_percent": 10.0,
        "memory": {"total_mb": 1000, "used_mb": 400, "percent": 40.0},
        "network": {"bytes_sent": 1, "bytes_recv": 2},
        "listening_ports": ["tcp/22"],
    }
    response = client.post(
        "/api/ingest",
        json=payload,
        headers={"X-Agent-Token": "test-ingest-token"},
    )
    assert response.status_code == 200
    assert response.get_json()["ok"] is True


def test_ingest_drops_unknown_host(client):
    response = client.post(
        "/api/ingest",
        json={"hostname": "unknown.example", "cpu_percent": 1},
        headers={"X-Agent-Token": "test-ingest-token"},
    )
    assert response.status_code == 404
