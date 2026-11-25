"""Authentication helpers for the single demo admin user."""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from flask import current_app, redirect, request, session, url_for
from werkzeug.security import check_password_hash


def verify_admin(username: str, password: str) -> bool:
    expected_user = current_app.config["ADMIN_USERNAME"]
    password_hash = current_app.config["ADMIN_PASSWORD_HASH"]
    if username != expected_user:
        # Still run hash check on dummy path timing? Keep simple for demo:
        # reject unknown usernames without revealing hash details.
        check_password_hash(password_hash, password)
        return False
    return check_password_hash(password_hash, password)


def login_user(username: str) -> None:
    session.clear()
    session["user"] = username
    session.permanent = False


def logout_user() -> None:
    session.clear()


def current_user() -> str | None:
    return session.get("user")


def login_required(view: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(view)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        if current_user() is None:
            return redirect(url_for("main.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped
