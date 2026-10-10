import { useState, useEffect } from "react";
import { getEvents, getDevices } from "../services/api";

function MonitoringOverview() {
  const [data, setData] = useState({
    agentActive: false,
    filesMonitored: 0,
    processCount: 0,
  });

  useEffect(() => {
    async function fetchData() {
      try {
        const [events, devices] = await Promise.all([getEvents(), getDevices()]);

        const latestWithFeatures = events
          .filter((e) => e.features && Object.keys(e.features).length > 0)
          .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))[0];

        const anyRecentDevice = devices.some((d) => {
          if (!d.last_seen) return false;
          const secondsAgo = (Date.now() - new Date(d.last_seen)) / 1000;
          return secondsAgo < 60;
        });

        setData({
          agentActive: anyRecentDevice || devices.length > 0,
          filesMonitored: latestWithFeatures?.features?.unique_files ?? 0,
          processCount: latestWithFeatures?.features?.process_count ?? 0,
        });
      } catch (err) {
        console.error("Failed to fetch monitoring overview:", err);
      }
    }

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const stats = [
    {
      icon: "🖥️",
      title: "Monitoring Agent",
      value: data.agentActive ? "ACTIVE" : "INACTIVE",
      subtitle: "Continuously monitoring",
      status: data.agentActive ? "normal" : "critical",
    },
    {
      icon: "📁",
      title: "Files Monitored",
      value: data.filesMonitored.toLocaleString(),
      subtitle: "Shared drive files",
      status: "normal",
    },
    {
      icon: "⚙️",
      title: "Processes Monitored",
      value: data.processCount.toLocaleString(),
      subtitle: "Active processes",
      status: "normal",
    },
    {
      icon: "🌐",
      title: "Network Activity",
      value: "NORMAL",
      subtitle: "No unusual connections",
      status: "normal",
    },
  ];

  return (
    <div className="monitoring-section">

      <div className="section-heading">
        <div>
          <h3>🖥️ System Monitoring Overview</h3>
          <p>Real-time status of the ransomware monitoring environment</p>
        </div>
        <span className="live-badge">● LIVE</span>
      </div>

      <div className="monitoring-grid">
        {stats.map((item) => (
          <div className="monitoring-card" key={item.title}>
            <div className="monitoring-icon">{item.icon}</div>
            <div className="monitoring-info">
              <span className="monitoring-title">{item.title}</span>
              <strong className={item.status}>{item.value}</strong>
              <small>{item.subtitle}</small>
            </div>
          </div>
        ))}
      </div>

    </div>
  );
}

export default MonitoringOverview;