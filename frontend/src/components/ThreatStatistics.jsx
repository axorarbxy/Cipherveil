import { useState, useEffect } from "react";
import { getDashboardOverview } from "../services/api";

function ThreatStatistics() {
  const [overview, setOverview] = useState(null);

  useEffect(() => {
    async function fetchOverview() {
      try {
        const data = await getDashboardOverview();
        setOverview(data);
      } catch (err) {
        console.error("Failed to fetch dashboard overview:", err);
      }
    }
    fetchOverview();
    const interval = setInterval(fetchOverview, 5000);
    return () => clearInterval(interval);
  }, []);

  const counts = overview?.alert_counts || { NORMAL: 0, SUSPICIOUS: 0, CRITICAL: 0 };

  const statistics = [
    {
      icon: "🛡️",
      value: (overview?.total_events_24h ?? 0).toLocaleString(),
      label: "Events Analyzed (24h)",
      description: "Security events processed",
    },
    {
      icon: "⚠️",
      value: counts.SUSPICIOUS.toLocaleString(),
      label: "Suspicious Events",
      description: "Potential threats detected",
    },
    {
      icon: "🚨",
      value: counts.CRITICAL.toLocaleString(),
      label: "Critical Alerts",
      description: "High-risk activities detected",
    },
    {
      icon: "🔒",
      value: (overview?.isolated_devices ?? 0).toLocaleString(),
      label: "Devices Isolated",
      description: "Threats successfully contained",
    },
  ];

  return (
    <div className="threat-statistics">
      <div className="section-heading">
        <div>
          <h3>📊 Threat Statistics</h3>
          <p>Security activity and detection summary</p>
        </div>
      </div>
      <div className="statistics-grid">
        {statistics.map((stat) => (
          <div className="statistic-card" key={stat.label}>
            <div className="statistic-icon">{stat.icon}</div>
            <div className="statistic-content">
              <strong>{stat.value}</strong>
              <span>{stat.label}</span>
              <small>{stat.description}</small>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ThreatStatistics;