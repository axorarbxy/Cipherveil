import { useEffect, useState } from "react";
import { getServerLogDetectorStatus } from "../services/api";

function ServerLogDetectionPanel() {
  const [status, setStatus] = useState(null);
  const [available, setAvailable] = useState(true);

  useEffect(() => {
    let active = true;

    async function refresh() {
      try {
        const next = await getServerLogDetectorStatus();
        if (active) {
          setStatus(next);
          setAvailable(true);
        }
      } catch (error) {
        if (active) setAvailable(false);
      }
    }

    refresh();
    const interval = setInterval(refresh, 3000);
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  const ready = available && status?.state === "ready";
  const latest = status?.last_result;
  const cards = [
    {
      icon: "🧠",
      title: "Server Log Model",
      value: !available ? "OFFLINE" : ready ? "READY" : "WARMING UP",
      subtitle: ready ? "Isolation Forest baseline loaded" : "Collecting baseline windows",
      tone: ready ? "normal" : "",
    },
    {
      icon: "🗂️",
      title: "Baseline Windows",
      value: (status?.baseline_windows ?? 0).toLocaleString(),
      subtitle: "Historical one-second file-log windows",
      tone: "normal",
    },
    {
      icon: "📈",
      title: "Latest Anomaly Score",
      value: latest?.state === "ready" ? `${latest.risk_score}/100` : "—",
      subtitle: latest?.risk_level ?? "Waiting for a scored window",
      tone: latest?.is_anomaly ? "warning" : "normal",
    },
    {
      icon: "⚡",
      title: "Mean Inference",
      value: `${status?.average_inference_ms ?? 0} ms`,
      subtitle: `${(status?.inference_windows ?? 0).toLocaleString()} windows scored`,
      tone: "normal",
    },
  ];

  return (
    <section className="monitoring-section server-log-detection">
      <div className="section-heading">
        <div>
          <h3>Server-Side File-Log Detection</h3>
          <p>One-second activity windows scored against the server’s historical baseline</p>
        </div>
        <span className="live-badge">{available ? "● LIVE" : "● OFFLINE"}</span>
      </div>
      <div className="monitoring-grid">
        {cards.map((card) => (
          <div className="monitoring-card" key={card.title}>
            <div className="monitoring-icon">{card.icon}</div>
            <div className="monitoring-info">
              <span className="monitoring-title">{card.title}</span>
              <strong className={card.tone}>{card.value}</strong>
              <small>{card.subtitle}</small>
            </div>
          </div>
        ))}
      </div>
      <p className="server-log-note">
        Anomaly scores at or above 99.9 are rate-limited to one backend alert per minute;
        this signal raises a review alert and does not trigger automatic isolation.
      </p>
    </section>
  );
}

export default ServerLogDetectionPanel;
