# PulseWatch — Demo Monitoring Infrastructure

Local Flask demo that shows live Linux server metrics (CPU, memory, network, listening ports) in a read-only UI so teams do not need SSH for basic checks.

See [docs/requirements.md](docs/requirements.md) and [docs/TODO.md](docs/TODO.md).

## Folder purpose

| Path | Purpose |
|------|---------|
| `app/` | Flask application (routes, templates, static assets) |
| `agent/` | Lightweight host metrics agent (later phases) |
| `tests/` | Automated tests |
| `docs/` | PRD, TODO, and project notes |

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

Debug stays off unless you set it explicitly:

```bash
export FLASK_APP=app
export FLASK_DEBUG=0
flask run --host=127.0.0.1 --port=5000
```

Then open http://127.0.0.1:5000/

## UI structure

- **Base template** (`app/templates/base.html`) — shared header/nav/footer
- **Styles** (`app/static/css/style.css`) — light, read-only monitoring look
- Jinja auto-escaping is left on (default). Do not mark user-controlled values `|safe`.

## Pages (Phase 0 placeholders)

| URL | Page |
|-----|------|
| `/` | Home |
| `/dashboard` | Dashboard overview (static) |
| `/servers` | Server list (static sample rows) |
| `/servers/<server_id>` | Server detail (static metrics) |

No forms mutate host state yet. Sign-in and inventory arrive in later phases.
