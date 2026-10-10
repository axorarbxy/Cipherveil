function RiskScore({ score = 18 }) {
  const getRiskLevel = () => {
    if (score >= 76) return "CRITICAL";
    if (score >= 51) return "HIGH";
    if (score >= 31) return "SUSPICIOUS";
    return "NORMAL";
  };

  const riskLevel = getRiskLevel();

  return (
    <div className="risk-score-panel">

      <div className="risk-score-header">
        <div>
          <h3>Ransomware Risk Score</h3>
          <p>Real-time threat assessment</p>
        </div>

        <span className={`risk-level ${riskLevel.toLowerCase()}`}>
          {riskLevel}
        </span>
      </div>

      <div className="risk-score-content">

        <div className="risk-number">
          <strong>{score}</strong>
          <span>/ 100</span>
        </div>

        <div className="risk-meter">

          <div className="risk-meter-track">
            <div
              className={`risk-meter-fill ${riskLevel.toLowerCase()}`}
              style={{
                width: `${Math.min(Math.max(score, 0), 100)}%`,
              }}
            />
          </div>

          <div className="risk-scale">
            <span>0</span>
            <span>25</span>
            <span>50</span>
            <span>75</span>
            <span>100</span>
          </div>

        </div>

      </div>

      <div className="risk-description">
        {riskLevel === "CRITICAL" &&
          "Critical ransomware-like behavior detected. Immediate containment is active."}

        {riskLevel === "HIGH" &&
          "High-risk activity detected. System requires close monitoring."}

        {riskLevel === "SUSPICIOUS" &&
          "Suspicious activity detected. Continue monitoring system behavior."}

        {riskLevel === "NORMAL" &&
          "No significant ransomware-like behavior detected."}
      </div>

    </div>
  );
}

export default RiskScore;