"""Flask application factory for the demo monitoring UI."""

from flask import Flask

from app.config import load_config
from app.db import close_db, init_db


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.update(load_config())
    if test_config:
        app.config.update(test_config)

    app.teardown_appcontext(close_db)
    init_db(app)

    from app.routes import bp

    app.register_blueprint(bp)
    return app
