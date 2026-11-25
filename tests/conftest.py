"""Pytest fixtures for the PulseWatch demo app."""

from __future__ import annotations

import pytest

from app import create_app


@pytest.fixture()
def app(tmp_path):
    db_path = tmp_path / "test.db"
    application = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "DATABASE_PATH": str(db_path),
            "INGEST_TOKEN": "test-ingest-token",
            # hash for password "admin123"
            "ADMIN_USERNAME": "admin",
            "ADMIN_PASSWORD_HASH": (
                "scrypt:32768:8:1$ddLc8R3zDrUHe4W9$"
                "a5f588fec21f6e1ad6fd8d8be4dfef11b1d0116fe5c7a7673186d44283eb365d2e928f6ab97a9242b4669003a3254d37c042c05864523cb8459def446944ca41"
            ),
        }
    )
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_client(client):
    client.post("/login", data={"username": "admin", "password": "admin123"})
    return client
