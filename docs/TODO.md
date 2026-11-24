# TODO: Demo Monitoring Infrastructure

Small increments for AI-assisted development. Complete in order. Each step includes **security** and **docs**.

Reference: [requirements.md](./requirements.md)

---

## Phase 0 — Project initialization and Basic UI

- [x] **0.1** Create project layout (`app/`, `tests/`, `docs/`, `agent/`, `.gitignore`)
  - Security: ignore `.env`, secrets, `__pycache__/`, `venv/`
  - Docs: note folder purpose in README stub

- [x] **0.2** Add `requirements.txt` (Flask + minimal deps) and create a virtualenv
  - Security: pin versions; do not commit `venv/`
  - Docs: one-line install note in README

- [x] **0.3** Create minimal Flask app entrypoint that serves a home page
  - Security: do not enable debug in committed config; use env for `FLASK_DEBUG`
  - Docs: document `flask run` / start command in README

- [x] **0.4** Add base HTML template + CSS (attractive, simple, read-only look)
  - Security: use Jinja auto-escaping (default); no `safe` on user input
  - Docs: short note on UI structure in README

- [x] **0.5** Add placeholder pages: Dashboard, Server List, Server Detail (static content)
  - Security: no forms that mutate host state yet
  - Docs: update README with page list

---

## Phase 1 — Sign-in and unit tests

- [ ] **1.1** Add config for admin username + hashed password (env or local config file)
  - Security: store only a hash; never commit plaintext password; document demo password only in README (local demo)
  - Docs: document how to set/change the hashed password

- [ ] **1.2** Implement login page (username/password form)
  - Security: POST only; CSRF-safe patterns for demo (at least same-site cookies / Flask session)
  - Docs: document login URL and default username `admin`

- [ ] **1.3** Verify password against hash; create session on success
  - Security: constant-time compare via Werkzeug; regenerate session on login; set `SESSION_COOKIE_HTTPONLY`
  - Docs: note session behavior in README

- [ ] **1.4** Protect Dashboard / Server List / Server Detail behind login
  - Security: redirect unauthenticated users to login; no metrics leakage
  - Docs: document auth requirement for pages

- [ ] **1.5** Add logout
  - Security: clear session fully on logout
  - Docs: document logout

- [ ] **1.6** Unit tests: login success, login failure, protected route redirect, logout
  - Security: assert failed login does not create a session
  - Docs: document `pytest` command in README

---

## Phase 2 — CI/CD (GitHub Actions)

- [ ] **2.1** Add `.github/workflows/ci.yml` — install deps, run tests on push/PR
  - Security: no secrets in workflow logs; use `permissions: contents: read`
  - Docs: note CI status badge / workflow purpose in README

- [ ] **2.2** Add lint step (e.g. `ruff` or `flake8`) to CI
  - Security: fail CI on obvious unsafe patterns if lint rules allow
  - Docs: document local lint command

- [ ] **2.3** Cache pip dependencies in Actions for faster runs
  - Security: pin Action versions (`@v4` style tags)
  - Docs: one-line note that CI runs on every PR

---

## Phase 3 — Server inventory (add / list / disable)

- [ ] **3.1** Define server model/storage (SQLite or JSON file for demo)
  - Security: validate hostname/IP format; constrain SSH port to 1–65535
  - Docs: document storage location and fields

- [ ] **3.2** Server List page: show registered servers and enabled/disabled state
  - Security: require login; escape all displayed fields
  - Docs: screenshot or short description of list page

- [ ] **3.3** Add-server form: hostname/IP, SSH username, SSH port (default 22), optional labels
  - Security: sanitize inputs; never store SSH passwords in this demo; treat inventory as metadata only
  - Docs: document required fields

- [ ] **3.4** Disable server (soft-disable; keep in inventory)
  - Security: POST/action with auth required; no arbitrary delete of host data via GET
  - Docs: explain disable vs remove

- [ ] **3.5** Unit tests: add, list, disable, validation errors
  - Security: test that unauthenticated inventory actions fail
  - Docs: update test section in README

---

## Phase 4 — Lightweight Python agent

- [ ] **4.1** Scaffold `agent/` script that collects CPU and memory (e.g. via `psutil`)
  - Security: agent runs read-only OS metrics; no remote shell execution
  - Docs: minimal agent run steps in README or `agent/README.md`

- [ ] **4.2** Add network traffic stats and listening ports to agent output
  - Security: expose listening ports only (no connection tables / process dumps beyond need)
  - Docs: document JSON/payload shape

- [ ] **4.3** Agent posts metrics to Flask ingest endpoint (localhost or configured URL)
  - Security: shared demo token/header for ingest; reject requests without token; bind Flask to local/demo host only
  - Docs: document agent config (`SERVER_URL`, token)

- [ ] **4.4** Unit tests: agent collectors return expected keys; ingest rejects bad auth
  - Security: test missing/invalid token returns 401/403
  - Docs: document how to run agent tests

---

## Phase 5 — Dashboard and server detail metrics

- [ ] **5.1** Store latest metrics per server in memory or SQLite (latest only — no history)
  - Security: associate metrics only with known server IDs; drop unknown hosts
  - Docs: note “latest snapshot only” (no history)

- [ ] **5.2** Dashboard overview: show high-level status for enabled servers
  - Security: login required; hide disabled servers from active overview (or mark clearly)
  - Docs: describe dashboard widgets

- [ ] **5.3** Server Detail: CPU, memory, network stats, listening ports
  - Security: read-only display; escape port/process labels
  - Docs: document metrics shown

- [ ] **5.4** Unit/integration tests: detail page shows fixture metrics; disabled server not polled
  - Security: ensure metrics API requires session
  - Docs: update acceptance notes

---

## Phase 6 — Refresh (auto 5s + manual)

- [ ] **6.1** Add manual refresh control on Dashboard and Server Detail
  - Security: refresh is GET/read-only; no state-changing side effects
  - Docs: document refresh button

- [ ] **6.2** Add auto-refresh every 5 seconds (meta refresh or small JS fetch)
  - Security: if using JS fetch, send credentials same-origin only; no eval of metric payloads
  - Docs: document 5s interval

- [ ] **6.3** Tests: metrics endpoint returns latest payload for authenticated user
  - Security: unauthenticated refresh/API calls fail
  - Docs: confirm success criteria mapping in README

---

## Phase 7 — Polish, local run docs, acceptance

- [ ] **7.1** Wire end-to-end local demo path: Flask + agent on localhost
  - Security: default bind `127.0.0.1`; demo token required
  - Docs: minimal “run locally” section (install → start app → start agent → login → add 1–2 servers)

- [ ] **7.2** Final README pass: features, out-of-scope, default admin, CI
  - Security: remind not to reuse demo password outside local demo
  - Docs: link PRD + TODO

- [ ] **7.3** Walk acceptance checklist from PRD §10 and check off items
  - Security: confirm no plaintext secrets in repo
  - Docs: mark demo complete in TODO when done

---

## Progress tracking

| Phase | Focus                         | Status |
|-------|-------------------------------|--------|
| 0     | Init + Basic UI               | Done |
| 1     | Sign-in + unit tests          | Not started |
| 2     | GitHub Actions CI             | Not started |
| 3     | Server inventory              | Not started |
| 4     | Python agent                  | Not started |
| 5     | Dashboard + detail metrics    | Not started |
| 6     | Auto/manual refresh           | Not started |
| 7     | Local polish + acceptance     | Not started |

**Suggested AI session size:** complete **one checkbox** per session (or at most one numbered step like `1.3`).
