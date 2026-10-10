import { useState, useEffect } from "react";
import { getDevices, getDevice, isolateDevice, restoreDevice, deleteDevice } from "../services/api";

function DevicesPanel() {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);

  async function fetchDevices() {
    try {
      const data = await getDevices();
      setDevices(data);
    } catch (err) {
      console.error("Failed to fetch devices:", err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchDevices();
    const interval = setInterval(fetchDevices, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleIsolate = async (id) => {
    try {
      await isolateDevice(id);
      fetchDevices();
    } catch (err) {
      console.error("Isolate failed:", err);
    }
  };

  const handleRestore = async (id) => {
    try {
      await restoreDevice(id);
      fetchDevices();
    } catch (err) {
      console.error("Restore failed:", err);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Remove this device permanently?")) return;
    try {
      await deleteDevice(id);
      fetchDevices();
    } catch (err) {
      console.error("Delete failed:", err);
    }
  };

  const handleViewDetails = async (id) => {
    try {
      const device = await getDevice(id);
      alert(
        `Device: ${device.device_name}\nIP: ${device.ip_address}\nMAC: ${device.mac_address}\nRegistered: ${new Date(device.registered_at).toLocaleString()}\nLast seen: ${device.last_seen ? new Date(device.last_seen).toLocaleString() : "Never"}`
      );
    } catch (err) {
      console.error("Failed to fetch device details:", err);
    }
  };

  return (
    <div className="monitoring-section">
      <div className="section-heading">
        <div>
          <h3>🖧 Connected Devices</h3>
          <p>Registered sidecar and monitoring endpoints</p>
        </div>
        <span className="live-badge">● LIVE</span>
      </div>

      <div className="monitoring-grid">
        {loading && <p style={{ padding: "1rem" }}>Loading devices...</p>}
        {!loading && devices.map((d) => (
          <div className="monitoring-card" key={d.id}>
            <div className="monitoring-icon">{d.is_isolated ? "🔒" : "🖥️"}</div>
            <div className="monitoring-info">
              <span className="monitoring-title">{d.device_name}</span>
              <strong className={d.is_isolated ? "critical" : "normal"}>
                {d.is_isolated ? "ISOLATED" : "ACTIVE"}
              </strong>
              <small>{d.location || d.ip_address}</small>
              <div style={{ marginTop: "0.5rem", display: "flex", gap: "0.4rem", flexWrap: "wrap" }}>
                {d.is_isolated ? (
                  <button className="view-report-btn" onClick={() => handleRestore(d.id)} style={{ fontSize: "0.75rem", padding: "0.25rem 0.5rem" }}>
                    ↺ Restore
                  </button>
                ) : (
                  <button className="view-report-btn" onClick={() => handleIsolate(d.id)} style={{ fontSize: "0.75rem", padding: "0.25rem 0.5rem" }}>
                    🔒 Isolate
                  </button>
                )}
                <button className="view-report-btn" onClick={() => handleViewDetails(d.id)} style={{ fontSize: "0.75rem", padding: "0.25rem 0.5rem" }}>
                  ℹ️ Details
                </button>
                <button className="close-report-btn" onClick={() => handleDelete(d.id)} style={{ fontSize: "0.75rem", padding: "0.25rem 0.5rem" }}>
                  🗑️ Remove
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default DevicesPanel;