(() => {
  const cfg = window.PulseWatchRefresh;
  if (!cfg || !cfg.endpoint) return;

  const hint = document.getElementById("refresh-hint");
  const button = document.getElementById("manual-refresh");

  function formatBytes(n) {
    if (n === undefined || n === null) return "—";
    return String(n);
  }

  function renderDashboard(data) {
    const enabled = document.getElementById("enabled-count");
    const reporting = document.getElementById("reporting-count");
    const cards = document.getElementById("dashboard-cards");
    if (enabled) enabled.textContent = data.enabled_count;
    if (reporting) {
      reporting.textContent = data.items.filter((i) => i.metrics).length;
    }
    if (!cards) return;

    if (!data.items.length) {
      cards.innerHTML =
        '<p class="empty-row">No enabled servers yet. <a href="/servers">Add a server</a>.</p>';
      return;
    }

    cards.innerHTML = data.items
      .map((item) => {
        const m = item.metrics;
        const labels = item.server.labels
          ? `<span class="label-chip">${escapeHtml(item.server.labels)}</span>`
          : "";
        const body = m
          ? `<dl class="host-metrics">
              <div><dt>CPU</dt><dd class="mono">${escapeHtml(String(m.cpu_percent))}%</dd></div>
              <div><dt>Memory</dt><dd class="mono">${escapeHtml(String(m.memory?.percent ?? "—"))}%</dd></div>
              <div><dt>Net ↓/↑</dt><dd class="mono">${formatBytes(m.network?.bytes_recv)} / ${formatBytes(m.network?.bytes_sent)}</dd></div>
              <div><dt>Ports</dt><dd class="mono">${(m.listening_ports || []).length}</dd></div>
            </dl>`
          : '<p class="metric-hint">Waiting for agent metrics…</p>';
        return `<article class="host-card">
          <div class="host-card-head">
            <h2 class="mono"><a href="/servers/${encodeURIComponent(item.server.id)}">${escapeHtml(item.server.hostname)}</a></h2>
            ${labels}
          </div>
          ${body}
        </article>`;
      })
      .join("");
  }

  function renderDetail(data) {
    const m = data.metrics;
    const cpu = document.getElementById("cpu-value");
    const mem = document.getElementById("mem-value");
    const net = document.getElementById("net-value");
    const portsCount = document.getElementById("ports-count");
    const portList = document.getElementById("port-list");
    const received = document.getElementById("received-at");

    if (!m) return;
    if (cpu) cpu.textContent = `${m.cpu_percent}%`;
    if (mem && m.memory) {
      mem.textContent = `${m.memory.used_mb} / ${m.memory.total_mb} MB (${m.memory.percent}%)`;
    }
    if (net && m.network) {
      net.textContent = `↓ ${m.network.bytes_recv} · ↑ ${m.network.bytes_sent}`;
    }
    const ports = m.listening_ports || [];
    if (portsCount) portsCount.textContent = String(ports.length);
    if (portList) {
      portList.innerHTML = ports.length
        ? ports.map((p) => `<li>${escapeHtml(String(p))}</li>`).join("")
        : '<li class="empty-row">No listening ports reported.</li>';
    }
    if (received && m.received_at) received.textContent = m.received_at;
  }

  function escapeHtml(value) {
    return value
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  async function refresh() {
    try {
      const res = await fetch(cfg.endpoint, {
        credentials: "same-origin",
        headers: { Accept: "application/json" },
      });
      if (!res.ok) return;
      const data = await res.json();
      if (cfg.mode === "dashboard") renderDashboard(data);
      if (cfg.mode === "detail") renderDetail(data);
      if (hint) hint.textContent = `updated ${new Date().toLocaleTimeString()}`;
    } catch (_) {
      if (hint) hint.textContent = "refresh failed";
    }
  }

  if (button) button.addEventListener("click", refresh);
  setInterval(refresh, cfg.intervalMs || 5000);
})();
