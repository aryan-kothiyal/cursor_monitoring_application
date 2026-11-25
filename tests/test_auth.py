"""Auth unit tests."""


def test_login_success_creates_session(client):
    response = client.post(
        "/login",
        data={"username": "admin", "password": "admin123"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    with client.session_transaction() as sess:
        assert sess.get("user") == "admin"


def test_login_failure_does_not_create_session(client):
    response = client.post(
        "/login",
        data={"username": "admin", "password": "wrong"},
        follow_redirects=False,
    )
    assert response.status_code == 400
    with client.session_transaction() as sess:
        assert sess.get("user") is None


def test_protected_route_redirects(client):
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_logout_clears_session(auth_client):
    with auth_client.session_transaction() as sess:
        assert sess.get("user") == "admin"
    response = auth_client.post("/logout", follow_redirects=False)
    assert response.status_code == 302
    with auth_client.session_transaction() as sess:
        assert sess.get("user") is None
