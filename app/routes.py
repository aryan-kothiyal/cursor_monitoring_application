"""HTTP routes for the read-only monitoring UI (placeholders in Phase 0)."""

from flask import Blueprint, render_template

bp = Blueprint("main", __name__)


@bp.route("/")
def home():
    return render_template("home.html")


@bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@bp.route("/servers")
def server_list():
    return render_template("servers.html")


@bp.route("/servers/<server_id>")
def server_detail(server_id: str):
    return render_template("server_detail.html", server_id=server_id)
