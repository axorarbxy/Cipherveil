const metrics = [
  { name: "Accuracy", values: [0.85, 0.84, 0.90, 0.87, 0.92] },
  { name: "F1", values: [0.86, 0.875, 0.99, 0.99, 0.973] },
  { name: "Sensitivity", values: [0.85, 0.84, 0.90, 0.87, 0.92] },
  { name: "Specificity", values: [0.86, 0.875, 0.99, 0.99, 0.973] },
];

const models = [
  { name: "RF", color: "#4f89d0" },
  { name: "SVM", color: "#c84e4e" },
  { name: "DT", color: "#91b747" },
  { name: "ADA", color: "#9878bb" },
  { name: "XGB", color: "#45b9d5" },
];

const plot = { left: 70, top: 28, width: 570, height: 240, min: 0.75, max: 1 };
const ticks = [0.75, 0.8, 0.85, 0.9, 0.95, 1];

function yPosition(value) {
  return plot.top + ((plot.max - value) / (plot.max - plot.min)) * plot.height;
}

function ModelPerformanceComparison() {
  const groupWidth = plot.width / metrics.length;
  const barWidth = 16;
  const barGap = 3;
  const barsWidth = models.length * barWidth + (models.length - 1) * barGap;

  return (
    <section className="performance-chart-panel" aria-labelledby="performance-chart-title">
      <div className="performance-chart-heading">
        <div>
          <p className="model-cost-eyebrow">MODEL EVALUATION</p>
          <h3 id="performance-chart-title">Tuned model performance comparison</h3>
          <p className="model-cost-description">Compare classification scores across four evaluation metrics.</p>
        </div>
      </div>

      <div className="performance-chart-wrap">
        <svg className="performance-chart" viewBox="0 0 760 360" role="img" aria-labelledby="performance-svg-title performance-svg-desc">
          <title id="performance-svg-title">Tuned model performance comparison</title>
          <desc id="performance-svg-desc">
            Grouped bar chart comparing approximate accuracy, F1, sensitivity, and specificity scores for Random Forest, SVM, Decision Tree, AdaBoost, and XGBoost.
          </desc>

          {ticks.map((tick) => {
            const y = yPosition(tick);
            return (
              <g key={tick}>
                <line x1={plot.left} y1={y} x2={plot.left + plot.width} y2={y} className="performance-grid-line" />
                <text x={plot.left - 12} y={y + 4} textAnchor="end" className="performance-tick-label">
                  {tick === 1 ? "1" : tick.toFixed(2).replace(/0+$/, "").replace(/\.$/, "").replace(".", ",")}
                </text>
              </g>
            );
          })}

          <rect x={plot.left} y={plot.top} width={plot.width} height={plot.height} className="performance-plot-border" />

          {metrics.map((metric, metricIndex) => {
            const groupCenter = plot.left + groupWidth * (metricIndex + 0.5);
            const startX = groupCenter - barsWidth / 2;
            return (
              <g key={metric.name}>
                {metric.values.map((value, modelIndex) => {
                  const x = startX + modelIndex * (barWidth + barGap);
                  const y = yPosition(value);
                  const height = plot.top + plot.height - y;
                  const model = models[modelIndex];
                  return (
                    <g key={model.name}>
                      <title>{`${metric.name} — ${model.name}: approximately ${(value * 100).toFixed(1)}%`}</title>
                      <rect x={x} y={y} width={barWidth} height={height} fill={model.color} rx="2" />
                    </g>
                  );
                })}
                <text x={groupCenter} y={plot.top + plot.height + 23} textAnchor="middle" className="performance-category-label">{metric.name}</text>
              </g>
            );
          })}

          {models.map((model, index) => {
            const y = 108 + index * 28;
            return (
              <g key={model.name}>
                <rect x="675" y={y - 10} width="9" height="9" fill={model.color} rx="1" />
                <text x="691" y={y - 2} className="performance-legend-label">{model.name}</text>
              </g>
            );
          })}

          <text x={plot.left + plot.width / 2} y="337" textAnchor="middle" className="performance-axis-label">Metrics</text>
          <text transform={`translate(19 ${plot.top + plot.height / 2}) rotate(-90)`} textAnchor="middle" className="performance-axis-label">Score</text>
        </svg>
      </div>

      <p className="model-cost-note">
        Values are approximate estimates traced from the supplied figure; the vertical axis starts at 0.75. Replace with measured results before reporting model performance.
      </p>
    </section>
  );
}

export default ModelPerformanceComparison;
