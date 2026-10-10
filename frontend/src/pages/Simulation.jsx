import SimulationPanel from "../components/SimulationPanel";

function Simulation({ onSimulation }) {
  return (
    <div className="simulation-page">

      {/* PAGE HEADER */}
      <div className="simulation-header">

        <div>
          <h2>Attack Simulation</h2>

          <p>
            Safely test ransomware detection and response scenarios
          </p>
        </div>

        <div className="simulation-badge">
          🧪 DEMO MODE
        </div>

      </div>


      {/* INFORMATION CARD */}
      <div className="simulation-info">

        <div className="simulation-info-icon">
          🛡️
        </div>

        <div>
          <h3>Controlled Security Simulation</h3>

          <p>
            Use the scenarios below to simulate suspicious system
            behavior and observe how the early-warning system responds.
          </p>
        </div>

      </div>


      {/* SIMULATION PANEL */}
      <SimulationPanel
        onSimulation={onSimulation}
      />


      {/* SIMULATION FLOW */}
      <div className="simulation-flow">

        <h3>🔄 Detection & Response Flow</h3>

        <div className="flow-steps">

          <div className="flow-step">
            <span>1</span>
            <strong>Simulate</strong>
            <small>Generate activity</small>
          </div>

          <div className="flow-arrow">→</div>

          <div className="flow-step">
            <span>2</span>
            <strong>Detect</strong>
            <small>Analyze behavior</small>
          </div>

          <div className="flow-arrow">→</div>

          <div className="flow-step">
            <span>3</span>
            <strong>Assess</strong>
            <small>Calculate risk</small>
          </div>

          <div className="flow-arrow">→</div>

          <div className="flow-step">
            <span>4</span>
            <strong>Respond</strong>
            <small>Contain threat</small>
          </div>

        </div>

      </div>


      {/* SAFETY NOTE */}
      <div className="simulation-note">

        <span>ℹ️</span>

        <p>
          <strong>Simulation only:</strong> These controls generate
          controlled demo events. They do not execute ransomware or
          modify real user files.
        </p>

      </div>

    </div>
  );
}

export default Simulation;