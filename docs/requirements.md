# PRD: Demo Monitoring Infrastructure (Linux Servers)

## 1. Overview

Local demo web app that shows live Linux server metrics so L1/L2/L3 and app teams do not need to SSH in for basic checks.

**Stack:** Python, Flask, attractive read-only UI  
**Deploy:** Single local machine (where Cursor runs)  
**Audience:** Internal infrastructure and application teams (demo only)

## 2. Problem

Today, checking real-time CPU, memory, network, and port usage requires logging into each Linux server. That is slow for routine monitoring and demos.

## 3. Goals

- Sign in as admin and use a clean, read-only UI
- Register Linux servers to monitor
- View live CPU, memory, network traffic, and listening ports
- Run everything locally with minimal setup

## 4. Non-Goals (Out of Scope)

- Alerts / notifications
- Historical graphs or time-series storage
- Multi-user accounts or RBAC
- HTTPS / production hardening
- Docker packaging
- Advanced reporting

## 5. Users

| Role | Access |
|------|--------|
| Admin (demo) | Single hardcoded user; full app access within read-only monitoring UI |

Username: `admin`  
Password: fixed demo password, stored hashed (e.g. Werkzeug/bcrypt). No password-reset flow.

## 6. Architecture (Minimal)

```
[Linux host]  -->  lightweight Python agent  -->  metrics
[Linux host]  -->  lightweight Python agent  -->  metrics
                         |
                         v
              Flask app (UI + API + inventory)
                         |
                         v
              Local browser (read-only dashboard)
```

- One machine runs Flask and acts as the central collector/UI.
- Each monitored host (including localhost) runs a small Python agent that reports live metrics.
- Monitored targets may be localhost or remote Linux hosts reachable from the Flask machine.

## 7. Features

### 7.1 Read-only UI

- Friendly, attractive layout
- No user actions that mutate metrics or host state
- Allowed writes: sign-in, add/list/disable servers in inventory, refresh views

### 7.2 Sign-in

- Login page
- Default username: `admin`
- Password verified against a stored hash
- Session required for dashboard and server pages

### 7.3 Server inventory

When adding a server, capture:

| Field | Required |
|-------|----------|
| Hostname / IP | Yes |
| SSH username | Yes |
| SSH port | Yes (default 22) |
| Labels | Optional |

Supported actions:

- Add server
- List servers
- Disable server (keep in inventory, stop monitoring)

### 7.4 Metrics (v1 only)

Per enabled server, show:

1. **CPU** — usage %
2. **Memory** — used / total (and %)
3. **Network** — traffic statistics (e.g. bytes in/out or rates)
4. **Ports** — listening ports only (not full connection tables)

Collected by a lightweight Python agent on each Linux host; displayed as near real-time data.

### 7.5 Refresh

- Auto-refresh every **5 seconds**
- Manual refresh control on dashboard / detail views

### 7.6 UI pages

1. **Login**
2. **Dashboard overview** — high-level status of monitored servers
3. **Server list** — inventory with enable/disable state
4. **Server detail** — live CPU, memory, network, listening ports

## 8. Local Demo Setup (Minimal)

1. Install Python dependencies for Flask app and agent.
2. Start Flask app on the local machine.
3. Start the Python agent on each Linux host to monitor (including localhost if used).
4. Open the UI in a browser, sign in as `admin`.
5. Add 1–2 servers and confirm metrics appear.

Exact install/run commands can live in a short README later; this PRD does not require production deployment steps.

## 9. Success Criteria

Demo is complete when a user can:

1. Log in with the admin account
2. Add 1–2 Linux servers (hostname/IP, SSH user, SSH port, optional labels)
3. See live CPU, memory, network traffic, and listening-port metrics
4. Use auto-refresh (5s) and manual refresh on a clean, read-only dashboard

## 10. Acceptance Checklist

- [x] Login works with hashed password for `admin`
- [x] Unauthenticated users cannot see monitoring pages
- [x] Can add, list, and disable servers
- [x] Dashboard overview shows registered servers
- [x] Server detail shows CPU, memory, network stats, listening ports
- [x] Metrics update every 5 seconds and via manual refresh
- [x] UI is read-only for host/metric data
- [x] Runs locally without Docker/HTTPS/alerts/history/RBAC
