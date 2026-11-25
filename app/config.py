"""Application configuration for the local demo."""

import os

# Demo password plaintext is documented in README only — never committed as config.
# Default hash corresponds to password: admin123
_DEFAULT_ADMIN_HASH = (
    "scrypt:32768:8:1$ddLc8R3zDrUHe4W9$"
    "a5f588fec21f6e1ad6fd8d8be4dfef11b1d0116fe5c7a7673186d44283eb365d2e928f6ab97a9242b4669003a3254d37c042c05864523cb8459def446944ca41"
)


def load_config() -> dict:
    return {
        "DEBUG": os.environ.get("FLASK_DEBUG", "0") == "1",
        "SECRET_KEY": os.environ.get("SECRET_KEY", "dev-only-pulsewatch-secret"),
        "ADMIN_USERNAME": os.environ.get("ADMIN_USERNAME", "admin"),
        "ADMIN_PASSWORD_HASH": os.environ.get("ADMIN_PASSWORD_HASH", _DEFAULT_ADMIN_HASH),
        "INGEST_TOKEN": os.environ.get("INGEST_TOKEN", "demo-ingest-token"),
        "DATABASE_PATH": os.environ.get("DATABASE_PATH", ""),
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SESSION_COOKIE_SECURE": False,  # local HTTP demo only
    }
