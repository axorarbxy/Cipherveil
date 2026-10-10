import { useState, useEffect } from "react";
import { getAlerts, updateAlertStatus } from "../services/api";

function severityFromRisk(risk) {
  if (risk >= 90) return "CRITICAL";
  if (risk >= 76) return "HIGH";
  if (risk >= 31) return "MEDIUM";
  return "LOW";
}

function statusFromAlert(alert) {
  return alert.auto_isolated ? "DETECTED" : "MONITORED";
}

function formatTime(isoString) {
  return new Date(isoString).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

function LiveEvents() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchAlerts() {
      try {
        const alerts = await getAlerts();
        const mapped = alerts.map((a) => ({
          id: a.id,
          time: formatTime(a.created_at),
          type: a.reason,
          description: `Risk score ${a.risk_score}/100 — ${a.status} status`,
          severity: severityFromRisk(a.risk_score),
          status: statusFromAlert(a),
          rawStatus: a.status,
        }));
        setEvents(mapped);
      } catch (err) {
        console.error("Failed to fetch alerts:", err);
      } finally {
        setLoading(false);
      }
    }

    fetchAlerts();
    const interval = setInterval(fetchAlerts, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleMarkFalsePositive = async (alertId) => {
    try {
      await updateAlertStatus(alertId, "NORMAL");
      setEvents((prev) =>
        prev.map((e) => (e.id === alertId ? { ...e, rawStatus: "NORMAL", status: "REVIEWED" } : e))
      );
    } catch (err) {
      console.error("Failed to update alert status:", err);
    }
  };

  return (
    <div className="live-events-page">

      <div className="page-heading">
        <div>
          <h2>Live Events</h2>
          <p>Real-time security events detected by the monitoring system</p>
        </div>

        <div className="live-indicator">
          <span className="live-dot"></span>
          LIVE MONITORING
        </div>
      </div>

      <div className="monitoring-banner">
        <div className="monitoring-icon">🛡️</div>
        <div>
          <strong>Monitoring Agent Active</strong>
          <p>
            System activity is being continuously monitored for
            ransomware-like behavior.
          </p>
        </div>
      </div>

      <div className="events-panel">

        <div className="events-header">
          <div>
            <h3>Event Timeline</h3>
            <p>Latest security activity</p>
          </div>

          <span className="event-count">
            {events.length} EVENTS
          </span>
        </div>

        <div className="event-list">

          {loading && <p style={{ padding: "1rem" }}>Loading events...</p>}

          {!loading && events.length === 0 && (
            <p style={{ padding: "1rem" }}>No events yet. Trigger a detection to see it here.</p>
          )}

          {events.map((event, index) => (
            <div className="event-row" key={event.id || index}>
              <div className="event-time">{event.time}</div>
              <div className={`event-dot ${event.severity.toLowerCase()}`}></div>
              <div className="event-content">
                <div className="event-main">
                  <strong>{event.type}</strong>
                  <span className={`severity-badge ${event.severity.toLowerCase()}`}>
                    {event.severity}
                  </span>
                </div>
                <p>{event.description}</p>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <div className={`event-status ${event.status.toLowerCase()}`}>
                  {event.status}
                </div>
                {event.rawStatus === "CRITICAL" && (
                  <button
                    className="view-report-btn"
                    onClick={() => handleMarkFalsePositive(event.id)}
                    style={{ fontSize: "0.75rem", padding: "0.25rem 0.5rem" }}
                  >
                    Mark False Positive
                  </button>
                )}
              </div>
            </div>
          ))}

        </div>

      </div>

      <div className="event-info-box">
        <span>ℹ️</span>
        <div>
          <strong>Real-Time Detection</strong>
          <p>Events are live from the backend and refresh every 3 seconds.</p>
        </div>
      </div>

    </div>
  );
}

export default LiveEvents;