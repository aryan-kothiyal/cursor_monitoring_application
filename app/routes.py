"""HTTP routes for the read-only monitoring UI."""

from __future__ import annotations

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from app.auth import current_user, login_required, login_user, logout_user, verify_admin
from app.db import (
    add_server,
    find_enabled_server_by_hostname,
    get_metrics,
    get_server,
    list_servers,
    set_server_enabled,
    store_metrics,
)
from app.validators import is_valid_host, parse_ssh_port, sanitize_labels

bp = Blueprint("main", __name__)


@bp.app_context_processor
def inject_auth_state():
    return {"current_user": current_user()}


@bp.route("/")
def home():
    return render_template("home.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user():
        return redirect(url_for("main.dashboard"))

    error = None
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        if verify_admin(username, password):
            login_user(username)
            next_url = request.args.get("next") or url_for("main.dashboard")
            if not next_url.startswith("/"):
                next_url = url_for("main.dashboard")
            return redirect(next_url)
        error = "Invalid username or password."

    return render_template("login.html", error=error), (400 if error else 200)


@bp.route("/logout", methods=["POST"])
def logout():
    logout_user()
    return redirect(url_for("main.login"))


@bp.route("/dashboard")
@login_required
def dashboard():
    servers = list_servers()
    enabled = [s for s in servers if s["enabled"]]
    cards = []
    reporting = 0
    for server in enabled:
        metrics = get_metrics(server["id"])
        if metrics:
            reporting += 1
        cards.append({"server": server, "metrics": metrics})
    return render_template(
        "dashboard.html",
        servers=servers,
        enabled_count=len(enabled),
        reporting_count=reporting,
        cards=cards,
    )


@bp.route("/servers", methods=["GET", "POST"])
@login_required
def server_list():
    error = None
    if request.method == "POST":
        hostname = (request.form.get("hostname") or "").strip()
        ssh_username = (request.form.get("ssh_username") or "").strip()
        ssh_port = parse_ssh_port(request.form.get("ssh_port"))
        labels = sanitize_labels(request.form.get("labels"))

        if not is_valid_host(hostname):
            error = "Enter a valid hostname or IP address."
        elif not ssh_username:
            error = "SSH username is required."
        elif ssh_port is None:
            error = "SSH port must be an integer between 1 and 65535."
        else:
            add_server(hostname, ssh_username, ssh_port, labels)
            flash("Server added.", "ok")
            return redirect(url_for("main.server_list"))

    servers = list_servers()
    return render_template("servers.html", servers=servers, error=error), (
        400 if error else 200
    )


@bp.route("/servers/<server_id>/disable", methods=["POST"])
@login_required
def disable_server(server_id: str):
    server = set_server_enabled(server_id, False)
    if server is None:
        flash("Server not found.", "error")
    else:
        flash(f"Disabled {server['hostname']}.", "ok")
    return redirect(url_for("main.server_list"))


@bp.route("/servers/<server_id>/enable", methods=["POST"])
@login_required
def enable_server(server_id: str):
    server = set_server_enabled(server_id, True)
    if server is None:
        flash("Server not found.", "error")
    else:
        flash(f"Enabled {server['hostname']}.", "ok")
    return redirect(url_for("main.server_list"))


@bp.route("/servers/<server_id>")
@login_required
def server_detail(server_id: str):
    server = get_server(server_id)
    if server is None:
        flash("Server not found.", "error")
        return redirect(url_for("main.server_list"))
    metrics = get_metrics(server_id)
    return render_template("server_detail.html", server=server, metrics=metrics)


@bp.route("/api/metrics/<server_id>")
@login_required
def metrics_api(server_id: str):
    server = get_server(server_id)
    if server is None:
        return jsonify({"error": "not found"}), 404
    metrics = get_metrics(server_id)
    return jsonify({"server": {"id": server["id"], "hostname": server["hostname"], "enabled": bool(server["enabled"])}, "metrics": metrics})


@bp.route("/api/dashboard")
@login_required
def dashboard_api():
    enabled = list_servers(enabled_only=True)
    items = []
    for server in enabled:
        items.append(
            {
                "server": {
                    "id": server["id"],
                    "hostname": server["hostname"],
                    "labels": server["labels"],
                },
                "metrics": get_metrics(server["id"]),
            }
        )
    return jsonify({"items": items, "enabled_count": len(enabled)})


@bp.route("/api/ingest", methods=["POST"])
def ingest_metrics():
    token = request.headers.get("X-Agent-Token", "")
    expected = current_app.config["INGEST_TOKEN"]
    if not token or token != expected:
        return jsonify({"error": "unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    hostname = (payload.get("hostname") or "").strip()
    if not hostname:
        return jsonify({"error": "hostname required"}), 400

    server = find_enabled_server_by_hostname(hostname)
    if server is None:
        # Drop unknown or disabled hosts — do not store.
        return jsonify({"error": "unknown or disabled host"}), 404

    metrics = {
        "hostname": hostname,
        "cpu_percent": payload.get("cpu_percent"),
        "memory": payload.get("memory") or {},
        "network": payload.get("network") or {},
        "listening_ports": payload.get("listening_ports") or [],
    }
    store_metrics(server["id"], metrics)
    return jsonify({"ok": True, "server_id": server["id"]}), 200
