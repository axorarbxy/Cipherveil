import { useState, useEffect } from "react";
import DevicesPanel from "./components/DevicesPanel";
import { login, getAlerts, getDevices } from "./services/api";

import StatusCard from "./components/StatusCard";
import RiskScore from "./components/RiskScore";
import EventTimeline from "./components/EventTimeline";
import SimulationPanel from "./components/SimulationPanel";
import AlertDetail from "./pages/AlertDetail";
import IncidentHistory from "./pages/IncidentHistory";
import LiveEvents from "./pages/LiveEvents";
import Simulation from "./pages/Simulation";
import MonitoringOverview from "./components/MonitoringOverview";
import ServerLogDetectionPanel from "./components/ServerLogDetectionPanel";
import IncidentReport from "./pages/IncidentReport";
import ThreatStatistics from "./components/ThreatStatistics";
import { getCurrentUser } from "./services/api";

function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [currentPage, setCurrentPage] = useState("dashboard");

  // ================================
  // SECURITY STATE
  // ================================

  const [securityState, setSecurityState] = useState({
    systemStatus: "PROTECTED",
    riskScore: 18,
    canaryStatus: "SAFE",
    heartbeat: "ONLINE",
  });

  // ================================
  // BACKEND CONNECTION
  // ================================

  const [connected, setConnected] = useState(false);

  useEffect(() => {
    async function init() {
      try {
        await login("admin", "SecurePass123!");
        setConnected(true);
        const user = await getCurrentUser();
        setCurrentUser(user);
      } catch (err) {
        console.error("Backend login failed:", err);
      }
    }
    init();
  }, []);

  useEffect(() => {
    if (!connected) return;

    async function fetchStatus() {
      try {
        const [alerts, devices] = await Promise.all([getAlerts(), getDevices()]);
        const latestAlert = alerts[0]; // most recent, since backend orders desc
        const device = devices[0];

        if (latestAlert && device) {
          setSecurityState({
            systemStatus: device.is_isolated ? "ISOLATED" : "PROTECTED",
            riskScore: latestAlert.risk_score,
            canaryStatus: latestAlert.reason === "CANARY FILE MODIFIED" ? "TRIGGERED" : "SAFE",
            heartbeat: latestAlert.reason.includes("HEARTBEAT") ? "LOST" : "ONLINE",
          });
        }
      } catch (err) {
        console.error("Failed to fetch status:", err);
      }
    }

    fetchStatus();
    const interval = setInterval(fetchStatus, 3000); // poll every 3s
    return () => clearInterval(interval);
  }, [connected]);

  // ================================
  // SIMULATION HANDLER
  // ================================

  const handleSimulation = (type) => {

    if (type === "start") {

      setSecurityState({
        systemStatus: "PROTECTED",
        riskScore: 18,
        canaryStatus: "SAFE",
        heartbeat: "ONLINE",
      });

    }

    if (type === "mass-change") {

      setSecurityState({
        systemStatus: "PROTECTED",
        riskScore: 58,
        canaryStatus: "SAFE",
        heartbeat: "ONLINE",
      });

    }

    if (type === "canary") {

      setSecurityState({
        systemStatus: "ISOLATED",
        riskScore: 92,
        canaryStatus: "TRIGGERED",
        heartbeat: "ONLINE",
      });

    }

    if (type === "heartbeat") {

      setSecurityState({
        systemStatus: "ISOLATED",
        riskScore: 82,
        canaryStatus: "SAFE",
        heartbeat: "LOST",
      });

    }

    if (type === "reset") {

      setSecurityState({
        systemStatus: "PROTECTED",
        riskScore: 18,
        canaryStatus: "SAFE",
        heartbeat: "ONLINE",
      });

    }
  };

  return (
    <div className="app">

      {/* ================================
          SIDEBAR
      ================================= */}

      <aside className="sidebar">

        <div className="logo">
          🛡️ <span>Digital Sentinel</span>
        </div>

        <p className="logo-subtitle">
          Ransomware Early-Warning
        </p>

        <nav>

          <button
            className={currentPage === "dashboard" ? "active" : ""}
            onClick={() => setCurrentPage("dashboard")}
          >
            🏠 Dashboard
          </button>

          <button
            className={currentPage === "events" ? "active" : ""}
            onClick={() => setCurrentPage("events")}
          >
            📊 Live Events
          </button>

          <button
            className={currentPage === "simulation" ? "active" : ""}
            onClick={() => setCurrentPage("simulation")}
          >
            🧪 Simulation
          </button>

          <button
  className={currentPage === "alerts" ? "active" : ""}
  onClick={() => setCurrentPage("alerts")}
>
  🚨 Alerts
</button>

<button
  className={currentPage === "history" ? "active" : ""}
  onClick={() => setCurrentPage("history")}
>
  📜 Incident History
</button>

<button
  className={currentPage === "reports" ? "active" : ""}
  onClick={() => setCurrentPage("reports")}
>
  📄 Incident Reports
</button>

        </nav>

      </aside>


      {/* ================================
          MAIN CONTENT
      ================================= */}

      <main className="main-content">

        <header className="topbar">

          <div>
            <h1>
              Ransomware Early-Warning System
            </h1>

            <p>
              Lightweight Threat Detection & Response
            </p>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
            {currentUser && (
              <span style={{ fontSize: "0.85rem", color: "#a0aaa2" }}>
                👤 {currentUser.username} ({currentUser.role})
              </span>
            )}
            <div className="system-online">
              <span className="online-dot"></span>
              {connected ? "SYSTEM ONLINE" : "CONNECTING..."}
            </div>
          </div>

        </header>


        <section className="page-content">


          {/* ================================
              DASHBOARD
          ================================= */}

          {currentPage === "dashboard" && (

            <>

              <h2>Security Dashboard</h2>


              {/* STATUS CARDS */}

              <div className="status-grid">

                <StatusCard
                  title="System Status"
                  value={securityState.systemStatus}
                  icon="🛡️"
                  type={
                    securityState.systemStatus === "ISOLATED"
                      ? "critical"
                      : "normal"
                  }
                  subtitle={
                    securityState.systemStatus === "ISOLATED"
                      ? "Threat containment active"
                      : "System operating normally"
                  }
                />


                <StatusCard
                  title="Risk Score"
                  value={`${securityState.riskScore} / 100`}
                  icon="📊"
                  type={
                    securityState.riskScore >= 76
                      ? "critical"
                      : securityState.riskScore >= 31
                      ? "warning"
                      : "normal"
                  }
                  subtitle={
                    securityState.riskScore >= 76
                      ? "Risk level: CRITICAL"
                      : securityState.riskScore >= 31
                      ? "Risk level: SUSPICIOUS"
                      : "Risk level: NORMAL"
                  }
                />


                <StatusCard
                  title="Canary Status"
                  value={securityState.canaryStatus}
                  icon="🧪"
                  type={
                    securityState.canaryStatus === "TRIGGERED"
                      ? "critical"
                      : "normal"
                  }
                  subtitle={
                    securityState.canaryStatus === "TRIGGERED"
                      ? "Canary file triggered"
                      : "Canary file unchanged"
                  }
                />


                <StatusCard
                  title="Heartbeat"
                  value={securityState.heartbeat}
                  icon="💓"
                  type={
                    securityState.heartbeat === "LOST"
                      ? "critical"
                      : "normal"
                  }
                  subtitle={
                    securityState.heartbeat === "LOST"
                      ? "Monitoring connection lost"
                      : "Monitoring connection healthy"
                  }
                />

              </div>
   
<ThreatStatistics />

<MonitoringOverview />
<ServerLogDetectionPanel />
<DevicesPanel />


              {/* RISK SCORE */}

              <RiskScore
                score={securityState.riskScore}
              />
              {/* SYSTEM MONITORING OVERVIEW */}




              {/* EVENT TIMELINE */}

              <EventTimeline />


              {/* SIMULATION */}

              <SimulationPanel
                onSimulation={handleSimulation}
              />


              {/* SYSTEM MESSAGE */}

              <div className="welcome-card">

                <h3>
                  {securityState.systemStatus === "ISOLATED"
                    ? "🚨 Threat Contained"
                    : "🛡️ System Protected"}
                </h3>

                <p>

                  {securityState.systemStatus === "ISOLATED"
                    ? "Suspicious ransomware-like activity has been detected and the system is isolated."
                    : "Your institutional shared drive is currently being monitored."}

                </p>

              </div>

            </>

          )}


          {/* ================================
              LIVE EVENTS
          ================================= */}

          {currentPage === "events" && <LiveEvents />}


          {/* ================================
              SIMULATION
          ================================= */}

          {currentPage === "simulation" && (

  <Simulation
    onSimulation={handleSimulation}
  />

)}


          {/* ================================
              ALERTS
          ================================= */}

          {currentPage === "alerts" && (

  <>

    <h2>Alert Details</h2>

    <AlertDetail
  riskScore={securityState.riskScore}
  systemStatus={securityState.systemStatus}
  canaryStatus={securityState.canaryStatus}
  heartbeat={securityState.heartbeat}
/>

  </>

)}
{/* ================================
    INCIDENT HISTORY
================================= */}

{currentPage === "history" && (

  <IncidentHistory />

)}


          {/* ================================
              REPORTS
          ================================= */}

          {currentPage === "reports" && (

  <IncidentReport />

)}

        </section>

      </main>

    </div>
  );
}

export default App;
