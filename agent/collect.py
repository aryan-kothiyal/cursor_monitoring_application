"""Read-only host metric collectors for the demo agent."""

from __future__ import annotations

from typing import Any

import psutil


def collect_cpu() -> float:
    return float(psutil.cpu_percent(interval=0.1))


def collect_memory() -> dict[str, Any]:
    mem = psutil.virtual_memory()
    return {
        "total_mb": round(mem.total / (1024 * 1024), 1),
        "used_mb": round(mem.used / (1024 * 1024), 1),
        "percent": float(mem.percent),
    }


def collect_network() -> dict[str, Any]:
    io = psutil.net_io_counters()
    return {
        "bytes_sent": int(io.bytes_sent),
        "bytes_recv": int(io.bytes_recv),
    }


def collect_listening_ports() -> list[str]:
    ports: set[str] = set()
    try:
        connections = psutil.net_connections(kind="inet")
    except (psutil.AccessDenied, PermissionError):
        return []
    for conn in connections:
        if conn.status != "LISTEN" or not conn.laddr:
            continue
        port = getattr(conn.laddr, "port", None)
        if port is None:
            continue
        family = "tcp" if conn.type.name == "SOCK_STREAM" else "udp"
        ports.add(f"{family}/{port}")
    return sorted(ports, key=lambda item: (item.split("/")[0], int(item.split("/")[1])))


def collect_all(hostname: str) -> dict[str, Any]:
    return {
        "hostname": hostname,
        "cpu_percent": collect_cpu(),
        "memory": collect_memory(),
        "network": collect_network(),
        "listening_ports": collect_listening_ports(),
    }
