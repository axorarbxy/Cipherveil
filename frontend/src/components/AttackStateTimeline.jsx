import { useEffect, useState } from "react";
import { getDashboardTimeline } from "../services/api";

const WINDOW_MS = 24 * 60 * 60 * 1000;
const chart = { left: 64, top: 26, width: 584, height: 190 };

function formatClock(timestamp) {
  return new Date(timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false });
}

function AttackStateTimeline() {
  const [alerts, setAlerts] = useState([]);
  const [now, setNow] = useState(Date.now());
  const [available, setAvailable] = useState(true);

  useEffect(() => {
    let active = true;
    async function refresh() {
      try {
        const timeline = await getDashboardTimeline(24);
        if (!active) return;
        setAlerts(Array.isArray(timeline) ? timeline : []);
        setAvailable(true);
      } catch (error) {
        if (active) setAvailable(false);
      }
      if (active) setNow(Date.now());
    }

    refresh();
    const interval = setInterval(refresh, 15000);
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  const start = now - WINDOW_MS;
  const points = alerts
    .map((alert) => {
      const timestamp = new Date(alert.created_at).getTime();
      const status = String(alert.status || "").toUpperCase();
      return {
        id: alert.id || `${timestamp}-${alert.reason}`,
        timestamp,
        state: status === "CRITICAL" || Number(alert.risk_score) >= 76 ? 1 : 0,
        status: status || "UNKNOWN",
        reason: alert.reason || "Alert",
      };
    })
    .filter((point) => Number.isFinite(point.timestamp) && point.timestamp >= start && point.timestamp <= now)
    .sort((a, b) => a.timestamp - b.timestamp);

  const xFor = (timestamp) => chart.left + ((timestamp - start) / WINDOW_MS) * chart.width;
  const yFor = (state) => chart.top + (1 - state) * chart.height;

  let currentState = 0;
  let path = `M ${chart.left} ${yFor(currentState)}`;
  points.forEach((point) => {
    const x = xFor(point.timestamp);
    path += ` L ${x} ${yFor(currentState)} L ${x} ${yFor(point.state)}`;
    currentState = point.state;
  });
  path += ` L ${chart.left + chart.width} ${yFor(currentState)}`;

  const ticks = [0, 6, 12, 18, 24].map((hours) => {
    const timestamp = start + (hours / 24) * WINDOW_MS;
    return { x: xFor(timestamp), label: formatClock(timestamp), key: hours };
  });

  return (
    <section className="attack-state-panel" aria-labelledby="attack-state-title">
      <div className="attack-state-heading">
        <div>
          <p className="model-cost-eyebrow">LIVE DETECTION HISTORY</p>
          <h3 id="attack-state-title">Attack state over time</h3>
          <p className="model-cost-description">Critical alert state reconstructed from the last 24 hours of backend alerts.</p>
        </div>
        <span className={`attack-state-live ${available ? "online" : "offline"}`}>
          {available ? "● CONNECTED" : "● OFFLINE"}
        </span>
      </div>

      <div className="attack-state-chart-wrap">
        <svg className="attack-state-chart" viewBox="0 0 760 300" role="img" aria-labelledby="attack-state-svg-title attack-state-svg-desc">
          <title id="attack-state-svg-title">Attack state timeline for the last 24 hours</title>
          <desc id="attack-state-svg-desc">
            A binary step chart showing state 1 at critical alerts with risk score 76 or greater, and state 0 at other alert records.
          </desc>

          {[0, 1].map((state) => {
            const y = yFor(state);
            return (
              <g key={state}>
                <line x1={chart.left} y1={y} x2={chart.left + chart.width} y2={y} className="attack-state-grid-line" />
                <text x={chart.left - 14} y={y + 4} textAnchor="end" className="attack-state-tick">{state}</text>
              </g>
            );
          })}

          {ticks.map((tick) => (
            <g key={tick.key}>
              <line x1={tick.x} y1={chart.top} x2={tick.x} y2={chart.top + chart.height} className="attack-state-grid-line vertical" />
              <text x={tick.x} y={chart.top + chart.height + 21} textAnchor="middle" className="attack-state-tick">{tick.label}</text>
            </g>
          ))}

          <rect x={chart.left} y={chart.top} width={chart.width} height={chart.height} className="attack-state-plot-border" />
          <path d={path} className="attack-state-line" />

          {points.map((point) => (
            <circle
              key={point.id}
              cx={xFor(point.timestamp)}
              cy={yFor(point.state)}
              r="3.5"
              className={point.state ? "attack-state-point critical" : "attack-state-point normal"}
            >
              <title>{`${formatClock(point.timestamp)} — ${point.status}: ${point.reason} (state ${point.state})`}</title>
            </circle>
          ))}

          <text x={chart.left + chart.width / 2} y="284" textAnchor="middle" className="attack-state-axis-label">Time (last 24 hours)</text>
          <text transform={`translate(17 ${chart.top + chart.height / 2}) rotate(-90)`} textAnchor="middle" className="attack-state-axis-label">Attack state (0/1)</text>

          <line x1="290" y1="12" x2="316" y2="12" className="attack-state-legend-line" />
          <circle cx="303" cy="12" r="3" className="attack-state-point critical" />
          <text x="323" y="16" className="attack-state-legend-label">Critical alert state</text>
        </svg>
      </div>

      <p className="model-cost-note">
        State 1 indicates a critical alert (risk score ≥ 76); state 0 indicates another alert. The step line holds each alert’s state until the next record and is not continuous endpoint telemetry.
        {!available && " Backend timeline is currently unavailable."}
      </p>
    </section>
  );
}

export default AttackStateTimeline;
