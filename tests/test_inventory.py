"""Server inventory tests."""


def test_unauthenticated_inventory_post_redirects(client):
    response = client.post(
        "/servers",
        data={
            "hostname": "localhost",
            "ssh_username": "monitor",
            "ssh_port": "22",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_add_list_disable_server(auth_client):
    add = auth_client.post(
        "/servers",
        data={
            "hostname": "localhost",
            "ssh_username": "monitor",
            "ssh_port": "22",
            "labels": "lab",
        },
        follow_redirects=True,
    )
    assert add.status_code == 200
    assert b"localhost" in add.data

    listed = auth_client.get("/servers")
    assert b"enabled" in listed.data

    # Extract server id from detail link
    import re

    match = re.search(rb'/servers/([a-f0-9]+)"', listed.data)
    assert match
    server_id = match.group(1).decode()

    disabled = auth_client.post(
        f"/servers/{server_id}/disable",
        follow_redirects=True,
    )
    assert disabled.status_code == 200
    assert b"disabled" in disabled.data


def test_invalid_hostname_rejected(auth_client):
    response = auth_client.post(
        "/servers",
        data={
            "hostname": "bad host!!",
            "ssh_username": "monitor",
            "ssh_port": "22",
        },
    )
    assert response.status_code == 400
    assert b"valid hostname" in response.data


def test_invalid_port_rejected(auth_client):
    response = auth_client.post(
        "/servers",
        data={
            "hostname": "localhost",
            "ssh_username": "monitor",
            "ssh_port": "70000",
        },
    )
    assert response.status_code == 400
    assert b"SSH port" in response.data
