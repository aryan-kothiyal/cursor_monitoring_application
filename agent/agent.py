#!/usr/bin/env python3
"""Lightweight metrics agent — posts read-only host stats to Flask ingest."""

from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import time
import urllib.error
import urllib.request

# Allow running as `python agent/agent.py` from repo root.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.collect import collect_all  # noqa: E402


def post_metrics(url: str, token: str, payload: dict) -> tuple[int, str]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "X-Agent-Token": token,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, body
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, body


def main() -> int:
    parser = argparse.ArgumentParser(description="PulseWatch demo metrics agent")
    parser.add_argument(
        "--server-url",
        default=os.environ.get("SERVER_URL", "http://127.0.0.1:5000/api/ingest"),
        help="Flask ingest URL",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("INGEST_TOKEN", "demo-ingest-token"),
        help="Shared ingest token (X-Agent-Token)",
    )
    parser.add_argument(
        "--hostname",
        default=os.environ.get("AGENT_HOSTNAME", socket.gethostname()),
        help="Must match an enabled inventory hostname/IP",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=float(os.environ.get("AGENT_INTERVAL", "5")),
        help="Seconds between posts",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Collect and post once, then exit",
    )
    args = parser.parse_args()

    print(f"Agent hostname={args.hostname} -> {args.server_url}", flush=True)
    while True:
        payload = collect_all(args.hostname)
        status, body = post_metrics(args.server_url, args.token, payload)
        print(f"post status={status} body={body}", flush=True)
        if args.once:
            return 0 if status == 200 else 1
        time.sleep(max(args.interval, 1.0))


if __name__ == "__main__":
    raise SystemExit(main())
