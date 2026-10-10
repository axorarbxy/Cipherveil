import { useState } from "react";
import { simulateCanaryHit, simulateHeartbeatLoss, simulateMassChange } from "../services/api";
import { simulateMLRansomware, simulateMLBenign } from "../services/api";

function SimulationPanel({ onSimulation }) {

  const [monitoring, setMonitoring] = useState(false);

  const [message, setMessage] = useState(
    "Ready for security simulation."
  );


  const startMonitoring = () => {

    setMonitoring(true);

    setMessage(
      "Monitoring started successfully."
    );

    onSimulation("start");
  };


  const simulateMassChanges = async () => {
    setMessage("⚠️ Simulated mass file modification activity detected.");
    try {
      await simulateMassChange();
    } catch (err) {
      console.error("Simulation failed:", err);
    }
    onSimulation("mass-change");
  };

  const simulateCanaryHit_ = async () => {
    setMessage("🚨 Canary file triggered — ransomware activity detected.");
    try {
      await simulateCanaryHit();
    } catch (err) {
      console.error("Simulation failed:", err);
    }
    onSimulation("canary");
  };

  const simulateHeartbeatLoss_ = async () => {
    setMessage("💔 Heartbeat lost — monitoring agent may be offline.");
    try {
      await simulateHeartbeatLoss();
    } catch (err) {
      console.error("Simulation failed:", err);
    }
    onSimulation("heartbeat");
  };

  const simulateMLThreat = async () => {
    setMessage("🧠 ML engine analyzing behavioral pattern...");
    try {
      const res = await simulateMLRansomware();
      setMessage(`🚨 ML detected ransomware-like behavior — ${(res.ml_result.probability * 100).toFixed(1)}% confidence.`);
    } catch (err) {
      console.error("ML simulation failed:", err);
    }
    onSimulation("canary");
  };

  const simulateMLNormal = async () => {
    setMessage("🧠 ML engine analyzing behavioral pattern...");
    try {
      const res = await simulateMLBenign();
      setMessage(`✅ ML classified activity as normal — ${(res.ml_result.probability * 100).toFixed(2)}% ransomware probability.`);
    } catch (err) {
      console.error("ML simulation failed:", err);
    }
  };


  const resetDemo = () => {

    setMonitoring(false);

    setMessage(
      "Demo has been reset. Ready for simulation."
    );

    onSimulation("reset");
  };


  return (

    <div className="simulation-panel">


      <div className="simulation-header">

        <div>

          <h3>
            🧪 Attack Simulation
          </h3>

          <p>
            Test ransomware detection and response scenarios
          </p>

        </div>


        <div
          className={`monitoring-status ${
            monitoring ? "active" : "inactive"
          }`}
        >

          {monitoring
            ? "MONITORING ACTIVE"
            : "MONITORING STOPPED"}

        </div>

      </div>


      <div className="simulation-buttons">


        <button className="simulation-btn danger" onClick={simulateCanaryHit_}>
          🧪 Simulate Canary Hit
        </button>

        <button className="simulation-btn danger" onClick={simulateHeartbeatLoss_}>
          💔 Heartbeat Loss
        </button>

        <button className="simulation-btn danger" onClick={simulateMLThreat}>
          🧠 Simulate ML-Detected Threat
        </button>

        <button className="simulation-btn" onClick={simulateMLNormal}>
          🧠 Simulate ML Normal Activity
        </button>


      </div>


      <button
        className="reset-btn"
        onClick={resetDemo}
      >
        ↻ Reset Demo
      </button>


      <div className="simulation-message">

        {message}

      </div>


    </div>

  );
}

export default SimulationPanel;