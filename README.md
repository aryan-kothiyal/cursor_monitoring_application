# PulseWatch — Demo Monitoring Infrastructure

Local Flask demo that shows live Linux server metrics (CPU, memory, network, listening ports) in a read-only UI so teams do not need SSH for basic checks.

Specs: [docs/requirements.md](docs/requirements.md) · [docs/TODO.md](docs/TODO.md)

**CI:** GitHub Actions runs lint (`ruff`) and `pytest` on every push/PR to `main`/`master`.

## Out of scope

Alerts, historical graphs, multi-user RBAC, HTTPS, Docker, advanced reporting.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run locally (minimal)

1. **Start Flask** (binds to localhost only). Use port **5070** if 5000 is already taken by another app on this machine:

```bash
cd ~/Desktop/New_Monitoring_application
source venv/bin/activate
export FLASK_APP=app
export FLASK_DEBUG=0
export INGEST_TOKEN=demo-ingest-token
flask run --host=127.0.0.1 --port=5070
```

2. Open http://127.0.0.1:5070/login (look for the **PulseWatch** brand) and sign in:
   - Username: `admin`
   - Password: `admin123` (**local demo only — do not reuse elsewhere**)

   If the page title/brand is not PulseWatch, you are on a different app — change the port.

3. **Add a server** on `/servers` (example: hostname `localhost`, SSH user `monitor`, port `22`).

4. **Start the agent** (hostname must match the inventory entry):

```bash
export INGEST_TOKEN=demo-ingest-token
export AGENT_HOSTNAME=localhost
python agent/agent.py --server-url http://127.0.0.1:5070/api/ingest
```

5. Open **Dashboard** / **Server detail** — metrics auto-refresh every 5 seconds; use **Refresh** for a manual update.

More agent detail: [agent/README.md](agent/README.md).

## Auth notes

- Single hardcoded admin user; password verified with a **Werkzeug hash** (`ADMIN_PASSWORD_HASH`).
- Sessions use `HttpOnly` + `SameSite=Lax` cookies. Logout clears the session.
- Change the hash:

```bash
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('YOUR_PASSWORD'))"
```

Set `ADMIN_PASSWORD_HASH` in the environment (see `.env.example`). Never commit plaintext passwords.

## Security (demo)

- Monitoring pages require login.
- Agent ingest requires `X-Agent-Token`; unknown/disabled hosts are dropped.
- Inventory stores hostname, SSH username/port, labels only — **no SSH passwords**.
- Default bind: `127.0.0.1`. Jinja auto-escaping stays on.

## Tests & lint

```bash
pytest -q
ruff check app agent tests
```

## Pages

| URL | Page | Auth |
|-----|------|------|
| `/` | Home | No |
| `/login` | Sign in | No |
| `/dashboard` | Overview of enabled servers | Yes |
| `/servers` | Add / list / disable | Yes |
| `/servers/<id>` | Live metrics detail | Yes |
| `/api/ingest` | Agent metrics POST | Token |
| `/api/metrics/<id>` | JSON metrics (refresh) | Yes |
| `/api/dashboard` | JSON dashboard (refresh) | Yes |

## Storage

SQLite at `instance/monitoring.db` (gitignored): server inventory + **latest metrics snapshot only** (no history).
