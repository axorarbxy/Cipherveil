import { useState, useEffect } from "react";
import { getIncidents, getAlerts, exportCertInReport, updateIncidentStatus } from "../services/api";

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
  return new Date(iso).toLocaleDateString(undefined, {
    day: "2-digit", month: "short", year: "numeric",
  });
}

function IncidentReport() {
  const [selectedReport, setSelectedReport] = useState(null);
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [incidentList, alertList] = await Promise.all([getIncidents(), getAlerts()]);
        const alertsById = Object.fromEntries(alertList.map((a) => [a.id, a]));

        const mapped = incidentList.map((inc) => {
          const alert = alertsById[inc.alert_id];
          const risk = alert ? alert.risk_score : 0;
          return {
            id: `RPT-${inc.id.slice(0, 6).toUpperCase()}`,
            incident: inc.id.slice(0, 8).toUpperCase(),
            incidentId: inc.id,
            date: formatDate(inc.time_of_detection),
            type: inc.symptoms_observed,
            severity: severityFromRisk(risk),
            risk,
            status: statusLabel(inc.status),
            system_network_affected: inc.system_network_affected,
            threat_classification: inc.threat_classification,
            suspected_source: inc.suspected_source,
            business_impact: inc.business_impact,
            action_taken: inc.action_taken,
            technical_iocs: inc.technical_iocs,
            point_of_contact: inc.point_of_contact,
          };
        });

        setReports(mapped);
      } catch (err) {
        console.error("Failed to fetch reports:", err);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleExport = async () => {
    try {
      const report = await exportCertInReport(selectedReport.incidentId);
      const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `CERT-IN-${selectedReport.incident}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Export failed:", err);
    }
  };

  const handleMarkContained = async () => {
    try {
      await updateIncidentStatus(selectedReport.incidentId, "contained");
      setSelectedReport({ ...selectedReport, status: "CONTAINED" });
      setReports((prev) =>
        prev.map((r) =>
          r.incidentId === selectedReport.incidentId ? { ...r, status: "CONTAINED" } : r
        )
      );
    } catch (err) {
      console.error("Status update failed:", err);
    }
  };

  return (
    <div className="reports-page">

      <div className="page-heading">
        <div>
          <h2>Incident Reports</h2>
          <p>Security incident reports and investigation summaries</p>
        </div>
        <div className="report-count">{reports.length} REPORTS</div>
      </div>

      <div className="report-summary-grid">
        <div className="report-summary-card">
          <span>TOTAL REPORTS</span>
          <strong>{reports.length}</strong>
          <small>Generated security reports</small>
        </div>
        <div className="report-summary-card">
          <span>CRITICAL INCIDENTS</span>
          <strong>{reports.filter((r) => r.severity === "CRITICAL").length}</strong>
          <small>Require immediate investigation</small>
        </div>
        <div className="report-summary-card">
          <span>HIGH RISK</span>
          <strong>{reports.filter((r) => r.severity === "HIGH").length}</strong>
          <small>High priority incidents</small>
        </div>
        <div className="report-summary-card">
          <span>RESOLVED</span>
          <strong>{reports.filter((r) => r.status === "RESOLVED" || r.status === "CONTAINED").length}</strong>
          <small>Successfully handled incidents</small>
        </div>
      </div>

      <div className="report-info-box">
        <div className="report-info-icon">🛡️</div>
        <div>
          <h3>Security Reporting System</h3>
          <p>
            Incident information, risk assessment, detection signals and
            response status are recorded for investigation and security analysis.
          </p>
        </div>
      </div>

      <div className="reports-table-section">
        <div className="section-header">
          <h3>📄 Generated Reports</h3>
          <p>Review detected security incidents and their outcomes</p>
        </div>

        <div className="reports-table-wrapper">
          <table className="reports-table">
            <thead>
              <tr>
                <th>REPORT ID</th>
                <th>INCIDENT</th>
                <th>DATE</th>
                <th>EVENT TYPE</th>
                <th>SEVERITY</th>
                <th>RISK</th>
                <th>STATUS</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr><td colSpan={8}>Loading reports...</td></tr>
              )}
              {!loading && reports.map((report) => (
                <tr key={report.id}>
                  <td className="report-id">{report.id}</td>
                  <td>{report.incident}</td>
                  <td>{report.date}</td>
                  <td>{report.type}</td>
                  <td>
                    <span className={`severity-badge ${report.severity.toLowerCase()}`}>
                      {report.severity}
                    </span>
                  </td>
                  <td className="risk-value">{report.risk}/100</td>
                  <td>
                    <span className={`status-badge ${report.status.toLowerCase()}`}>
                      {report.status}
                    </span>
                  </td>
                  <td>
                    <button className="view-report-btn" onClick={() => setSelectedReport(report)}>
                      View Report
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {selectedReport && (
        <div className="report-details-panel">
          <div className="report-details-header">
            <div>
              <h3>📄 Incident Report Details</h3>
              <p>CERT-In compliant investigation summary</p>
            </div>
            <div style={{ display: "flex", gap: "0.5rem" }}>
              {selectedReport.status !== "CONTAINED" && selectedReport.status !== "RESOLVED" && (
                <button className="view-report-btn" onClick={handleMarkContained}>
                  ✓ Mark Contained
                </button>
              )}
              <button className="view-report-btn" onClick={handleExport}>
                ⬇ Export CERT-In JSON
              </button>
              <button className="close-report-btn" onClick={() => setSelectedReport(null)}>
                ✕ Close
              </button>
            </div>
          </div>

          <div className="report-detail-grid">
            <div><span>REPORT ID</span><strong>{selectedReport.id}</strong></div>
            <div><span>INCIDENT ID</span><strong>{selectedReport.incident}</strong></div>
            <div><span>DATE</span><strong>{selectedReport.date}</strong></div>
            <div><span>EVENT TYPE</span><strong>{selectedReport.type}</strong></div>
            <div><span>SEVERITY</span><strong>{selectedReport.severity}</strong></div>
            <div><span>RISK SCORE</span><strong>{selectedReport.risk}/100</strong></div>
            <div><span>SYSTEM STATUS</span><strong>{selectedReport.status}</strong></div>
          </div>

          <div className="report-section">
            <h4>🔍 System/Network Affected</h4>
            <p>{selectedReport.system_network_affected}</p>
          </div>

          <div className="report-section">
            <h4>🧬 Threat Classification</h4>
            <p>{selectedReport.threat_classification}</p>
          </div>

          <div className="report-section">
            <h4>📉 Business Impact</h4>
            <p>{selectedReport.business_impact}</p>
          </div>

          <div className="report-section">
            <h4>🛡️ Action Taken</h4>
            <p>{selectedReport.action_taken}</p>
          </div>

          {selectedReport.technical_iocs && (
            <div className="report-section">
              <h4>🧾 Technical Indicators of Compromise</h4>
              <p>{selectedReport.technical_iocs}</p>
            </div>
          )}

          <div className="report-section">
            <h4>📇 Point of Contact</h4>
            <p>{selectedReport.point_of_contact}</p>
          </div>
        </div>
      )}

      <div className="compliance-box">
        <span>ℹ️</span>
        <div>
          <strong>Audit & Compliance</strong>
          <p>
            Incident reports follow the CERT-In mandatory 9-field format and
            maintain an audit trail of detected ransomware-like activity.
          </p>
        </div>
      </div>

    </div>
  );
}

export default IncidentReport;