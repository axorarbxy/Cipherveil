import { useState, useEffect } from "react";
import { getAlerts } from "../services/api";

const ICONS = {
  "CANARY FILE MODIFIED": "🧪",
  "DEAD-MAN'S-SWITCH: heartbeat timeout": "💓",
  "Mass file-change pattern detected": "📁",
};

function typeFromRisk(risk) {
  if (risk >= 76) return "critical";
  if (risk >= 31) return "warning";
  return "normal";
}

function formatTime(iso) {
  return new Date(iso).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

function EventTimeline() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    async function fetchAlerts() {
      try {
        const alerts = await getAlerts();
        const mapped = alerts.slice(0, 5).map((a) => ({
          time: formatTime(a.created_at),
          title: a.reason,
          description: `Risk score ${a.risk_score}/100 — ${a.status}`,
          type: typeFromRisk(a.risk_score),
          icon: ICONS[a.reason] || "📄",
        }));
        setEvents(mapped);
      } catch (err) {
        console.error("Failed to fetch alerts for timeline:", err);
      }
    }

    fetchAlerts();
    const interval = setInterval(fetchAlerts, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="timeline-card">

      <div className="timeline-header">
        <div>
          <h3>🔍 Security Event Timeline</h3>
          <p>Recent events detected by the monitoring system</p>
        </div>
        <span className="live-badge">● LIVE</span>
      </div>

      <div className="timeline">
        {events.length === 0 && (
          <p style={{ padding: "1rem" }}>No events yet.</p>
        )}
        {events.map((event, index) => (
          <div className={`timeline-event ${event.type}`} key={index}>
            <div className="timeline-indicator">{event.icon}</div>
            <div className="timeline-content">
              <div className="timeline-top">
                <strong>{event.title}</strong>
                <span className="event-time">{event.time}</span>
              </div>
              <p>{event.description}</p>
            </div>
          </div>
        ))}
      </div>

    </div>
  );
}

export default EventTimeline;