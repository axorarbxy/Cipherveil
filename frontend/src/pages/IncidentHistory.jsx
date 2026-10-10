import { useState, useEffect } from "react";
import { getIncidents, getAlerts } from "../services/api";

function severityFromRisk(risk) {
  if (risk >= 90) return "CRITICAL";
  if (risk >= 76) return "HIGH";
  if (risk >= 31) return "MEDIUM";
  return "LOW";
}

function statusLabel(status) {
  if (status === "open") return "ISOLATED";
  if (status === "contained") return "CONTAINED";
  return "RESOLVED";
}

function formatDate(iso) {
  const d = new Date(iso);
  return {
    date: d.toLocaleDateString(undefined, { day: "2-digit", month: "short", year: "numeric" }),
    time: d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false }),
  };
}

function IncidentHistory() {
  const [search, setSearch] = useState("");
  const [severity, setSeverity] = useState("ALL");
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [incidentList, alertList] = await Promise.all([getIncidents(), getAlerts()]);
        const alertsById = Object.fromEntries(alertList.map((a) => [a.id, a]));

        const mapped = incidentList.map((inc) => {
          const alert = alertsById[inc.alert_id];
          const risk = alert ? alert.risk_score : 0;
          const { date, time } = formatDate(inc.time_of_detection);
          return {
            id: inc.id.slice(0, 8).toUpperCase(),
            date,
            time,
            type: inc.symptoms_observed,
            severity: severityFromRisk(risk),
            risk,
            status: statusLabel(inc.status),
          };
        });

        setIncidents(mapped);
      } catch (err) {
        console.error("Failed to fetch incidents:", err);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const filteredIncidents = incidents.filter((incident) => {
    const matchesSearch =
      incident.id.toLowerCase().includes(search.toLowerCase()) ||
      incident.type.toLowerCase().includes(search.toLowerCase());
    const matchesSeverity = severity === "ALL" || incident.severity === severity;
    return matchesSearch && matchesSeverity;
  });

  return (
    <div className="history-page">

      <div className="history-header">
        <div>
          <h2>Historical Incidents</h2>
          <p>Security incident history and audit trail</p>
        </div>
        <div className="incident-count">{filteredIncidents.length} INCIDENTS</div>
      </div>

      <div className="history-filters">
        <input
          type="text"
          placeholder="🔍 Search incident..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select value={severity} onChange={(e) => setSeverity(e.target.value)}>
          <option value="ALL">All Severity</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
        </select>
      </div>

      <div className="history-statistics">
        <div className="history-stat-card">
          <span>Total Incidents</span>
          <strong>{incidents.length}</strong>
        </div>
        <div className="history-stat-card critical">
          <span>Critical</span>
          <strong>{incidents.filter((i) => i.severity === "CRITICAL").length}</strong>
        </div>
        <div className="history-stat-card high">
          <span>High Risk</span>
          <strong>{incidents.filter((i) => i.severity === "HIGH").length}</strong>
        </div>
        <div className="history-stat-card resolved">
          <span>Resolved</span>
          <strong>{incidents.filter((i) => i.status === "RESOLVED").length}</strong>
        </div>
      </div>

      <div className="history-panel">
        <div className="history-table-header">
          <span>INCIDENT</span>
          <span>DATE & TIME</span>
          <span>EVENT TYPE</span>
          <span>SEVERITY</span>
          <span>RISK</span>
          <span>STATUS</span>
        </div>

        {loading ? (
          <div className="no-incidents">Loading incidents...</div>
        ) : filteredIncidents.length === 0 ? (
          <div className="no-incidents">No incidents found.</div>
        ) : (
          filteredIncidents.map((incident) => (
            <div className="history-row" key={incident.id}>
              <span className="incident-id">{incident.id}</span>
              <span className="incident-date">
                {incident.date}
                <small>{incident.time}</small>
              </span>
              <span className="incident-type">{incident.type}</span>
              <span>
                <span className={`history-severity ${incident.severity.toLowerCase()}`}>
                  {incident.severity}
                </span>
              </span>
              <span className="history-risk">{incident.risk}/100</span>
              <span>
                <span className={`history-status ${incident.status.toLowerCase()}`}>
                  {incident.status}
                </span>
              </span>
            </div>
          ))
        )}
      </div>

      <div className="audit-info">
        <span className="audit-icon">🛡️</span>
        <div>
          <strong>Audit Trail Active</strong>
          <p>Security events and incidents are recorded for investigation and reporting.</p>
        </div>
      </div>

    </div>
  );
}

export default IncidentHistory;