"""Input validation for server inventory."""

from __future__ import annotations

import ipaddress
import re

_HOSTNAME_RE = re.compile(
    r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*$"
)


def is_valid_host(value: str) -> bool:
    host = value.strip()
    if not host or len(host) > 253:
        return False
    if host.lower() == "localhost":
        return True
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        pass
    return bool(_HOSTNAME_RE.match(host))


def parse_ssh_port(value: str | int | None, default: int = 22) -> int | None:
    if value is None or value == "":
        return default
    try:
        port = int(value)
    except (TypeError, ValueError):
        return None
    if 1 <= port <= 65535:
        return port
    return None


def sanitize_labels(value: str | None) -> str:
    if not value:
        return ""
    # Keep labels as plain text; strip control characters.
    cleaned = "".join(ch for ch in value.strip() if ch.isprintable())
    return cleaned[:120]
