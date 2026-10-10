function AlertDetail({
  riskScore = 18,
  systemStatus = "PROTECTED",
  canaryStatus = "SAFE",
  heartbeat = "ONLINE",
}) {

  const features = [
    {
      name: "File Modification Rate",
      value: 35,
      description: "Unusually high number of files modified"
    },
    {
      name: "File Entropy Increase",
      value: 25,
      description: "File content shows encryption-like changes"
    },
    {
      name: "Process Activity",
      value: 18,
      description: "Abnormal process/file activity detected"
    },
    {
      name: "Canary Trigger",
      value: 14,
      description: "Protected canary file was modified"
    }
  ];

  const affectedFiles = [
    "/shared/docs/file1.docx",
    "/shared/docs/file2.pdf",
    "/shared/data/report.xlsx"
  ];

  const detectionSignals = [
    {
      icon: "🔴",
      title: "Canary Triggered",
      description: "Protected canary file was modified"
    },
    {
      icon: "🔴",
      title: "High File Activity",
      description: "Abnormal file modification rate detected"
    },
    {
      icon: "🟠",
      title: "Suspicious Process",
      description: "Process behavior differs from normal activity"
    },
    {
      icon: "🟢",
      title: "Heartbeat Online",
      description: "Monitoring agent is responding normally"
    }
  ];

  return (
    <div className="alert-detail-panel">

      {/* =================================
          ALERT HEADER
      ================================= */}

      <div className="alert-detail-header">

        <div>
          <h3>🚨 Ransomware Alert</h3>

          <p>
            Ransomware-like activity detected
          </p>
        </div>

        <div
  className={
    riskScore >= 76
      ? "critical-badge"
      : riskScore >= 31
      ? "warning-badge"
      : "normal-badge"
  }
>
  {riskScore >= 76
    ? "CRITICAL"
    : riskScore >= 31
    ? "HIGH"
    : "NORMAL"}
</div>

      </div>


      {/* =================================
          BASIC INFORMATION
      ================================= */}

      <div className="alert-info-grid">

        <div className="alert-info-card">

          <span>RISK SCORE</span>

          <strong className="risk-critical">
            {riskScore} / 100
          </strong>

          <small>
            CRITICAL RISK
          </small>

        </div>


        <div className="alert-info-card">

          <span>DETECTION TIME</span>

          <strong>
            {new Date().toLocaleTimeString()}
          </strong>

          <small>
            Real-time detection
          </small>

        </div>


        <div className="alert-info-card">

          <span>SYSTEM STATUS</span>

          <strong
  className={
    systemStatus === "ISOLATED"
      ? "isolated-text"
      : "protected-text"
  }
>
  {systemStatus}
</strong>

          <small>
            Threat containment active
          </small>

        </div>

      </div>


      {/* =================================
          WHY WAS THIS FLAGGED?
      ================================= */}

      <div className="explanation-section">

        <div className="section-title">

          <div>
            <h4>
              Why Was This Flagged?
            </h4>

            <p>
              ML feature contribution analysis
            </p>
          </div>

          <span className="explainability-badge">
            SHAP
          </span>

        </div>


        <div className="feature-list">

          {features.map((feature) => (

            <div
              className="feature-item"
              key={feature.name}
            >

              <div className="feature-info">

                <span className="feature-name">
                  {feature.name}
                </span>

                <span className="feature-description">
                  {feature.description}
                </span>

              </div>


              <div className="feature-value-area">

                <div className="feature-bar">

                  <div
                    className="feature-progress"
                    style={{
                      width: `${(feature.value / 35) * 100}%`
                    }}
                  />

                </div>

                <span className="feature-score">
                  +{feature.value}
                </span>

              </div>

            </div>

          ))}

        </div>

      </div>


      {/* =================================
          DETECTION SIGNALS
      ================================= */}

      <div className="signals-section">

        <div className="section-title">

          <div>

            <h4>
              🔍 Detection Signals
            </h4>

            <p>
              Evidence collected by the monitoring system
            </p>

          </div>

        </div>


        <div className="signals-grid">

          {detectionSignals.map((signal) => (

            <div
              className="signal-card"
              key={signal.title}
            >

              <span className="signal-icon">
                {signal.icon}
              </span>

              <div>

                <strong>
                  {signal.title}
                </strong>

                <p>
                  {signal.description}
                </p>

              </div>

            </div>

          ))}

        </div>

      </div>


      {/* =================================
          AFFECTED FILES
      ================================= */}

      <div className="affected-section">

        <h4>
          📁 Affected Files
        </h4>

        <p>
          Files involved in suspicious activity
        </p>


        <div className="file-list">

          {affectedFiles.map((file) => (

            <div
              className="affected-file"
              key={file}
            >

              <span>
                📄
              </span>

              <code>
                {file}
              </code>

            </div>

          ))}

        </div>

      </div>


      {/* =================================
          SYSTEM RESPONSE
      ================================= */}

      <div className="response-box">

        <span className="response-icon">
          🛡️
        </span>

        <div>

          <strong>
            Automated Response
          </strong>

          <p>
  {systemStatus === "ISOLATED"
    ? "System isolation has been initiated to prevent further file damage."
    : "No containment action is currently required. System is operating normally."}
</p>

        </div>

        <span className="response-status">
          ISOLATED
        </span>

      </div>

    </div>
  );
}

export default AlertDetail;