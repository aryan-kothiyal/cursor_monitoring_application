"""Flask application factory for the demo monitoring UI."""

import os

from flask import Flask


def create_app() -> Flask:
    app = Flask(__name__)

    # Debug only via environment (never hard-coded on in committed config).
    app.config["DEBUG"] = os.environ.get("FLASK_DEBUG", "0") == "1"

    from app.routes import bp

    app.register_blueprint(bp)
    return app
