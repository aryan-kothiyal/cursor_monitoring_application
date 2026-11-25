# PulseWatch agent

Lightweight Python agent that collects **CPU**, **memory**, **network**, and **listening ports**, then POSTs them to the Flask ingest API.

## Run (local demo)

From the repo root (venv activated):

```bash
export INGEST_TOKEN=demo-ingest-token
export AGENT_HOSTNAME=localhost
python agent/agent.py --server-url http://127.0.0.1:5070/api/ingest
```

`AGENT_HOSTNAME` must match an **enabled** server hostname/IP in the UI inventory.

## Payload shape

```json
{
  "hostname": "localhost",
  "cpu_percent": 12.5,
  "memory": {"total_mb": 8192.0, "used_mb": 3200.0, "percent": 39.0},
  "network": {"bytes_sent": 1000, "bytes_recv": 2000},
  "listening_ports": ["tcp/22", "tcp/5000"]
}
```

Auth header: `X-Agent-Token: <INGEST_TOKEN>`
