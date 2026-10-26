const chartModels = [
  { name: "RF", fpr: 0.03, tpr: 0.84, color: "#4f89d0", marker: "diamond" },
  { name: "SVM", fpr: 0.02, tpr: 0.53, color: "#c84e4e", marker: "square" },
  { name: "DT", fpr: 0.07, tpr: 0.82, color: "#91b747", marker: "triangle" },
  { name: "ADA", fpr: 0.20, tpr: 0.70, color: "#9878bb", marker: "x" },
  { name: "XGB", fpr: 0.01, tpr: 0.90, color: "#45b9d5", marker: "asterisk" },
];

const chart = { left: 64, top: 24, width: 540, height: 222 };
const xTicks = [0, 0.05, 0.1, 0.15, 0.2, 0.25];
const yTicks = [0, 0.2, 0.4, 0.6, 0.8, 1];

function xPosition(value) {
  return chart.left + (value / 0.25) * chart.width;
}

function yPosition(value) {
  return chart.top + (1 - value) * chart.height;
}

function Marker({ model, x, y, size = 6 }) {
  const common = { fill: model.color, stroke: model.color, strokeWidth: 1.5 };
  if (model.marker === "diamond") {
    return <polygon points={`${x},${y - size} ${x + size},${y} ${x},${y + size} ${x - size},${y}`} {...common} />;
  }
  if (model.marker === "square") {
    return <rect x={x - size + 1} y={y - size + 1} width={size * 2 - 2} height={size * 2 - 2} {...common} />;
  }
  if (model.marker === "triangle") {
    return <polygon points={`${x},${y - size} ${x + size},${y + size} ${x - size},${y + size}`} {...common} />;
  }
  if (model.marker === "asterisk") {
    return (
      <g stroke={model.color} strokeWidth="1.7" strokeLinecap="round">
        <path d={`M ${x - size} ${y} L ${x + size} ${y} M ${x - size * 0.5} ${y - size * 0.87} L ${x + size * 0.5} ${y + size * 0.87} M ${x + size * 0.5} ${y - size * 0.87} L ${x - size * 0.5} ${y + size * 0.87}`} />
      </g>
    );
  }
  return <path d={`M ${x - size} ${y - size} L ${x + size} ${y + size} M ${x + size} ${y - size} L ${x - size} ${y + size}`} stroke={model.color} strokeWidth="1.7" />;
}

function RocPointAnalysis() {
  return (
    <section className="roc-analysis-panel" aria-labelledby="roc-analysis-title">
      <div className="roc-analysis-heading">
        <div>
          <p className="model-cost-eyebrow">MODEL EVALUATION</p>
          <h3 id="roc-analysis-title">ROC point analysis</h3>
          <p className="model-cost-description">True positive rate compared with false positive rate.</p>
        </div>
      </div>

      <div className="roc-chart-wrap">
        <svg className="roc-chart" viewBox="0 0 740 315" role="img" aria-labelledby="roc-svg-title roc-svg-desc">
          <title id="roc-svg-title">ROC point analysis of initial models</title>
          <desc id="roc-svg-desc">
            Scatter plot of approximate false positive and true positive rates for RF, SVM, DT, ADA, and XGB models.
          </desc>

          {yTicks.map((tick) => {
            const y = yPosition(tick);
            return (
              <g key={`y-${tick}`}>
                <line x1={chart.left} y1={y} x2={chart.left + chart.width} y2={y} className="roc-grid-line" />
                <text x={chart.left - 12} y={y + 4} textAnchor="end" className="roc-tick-label">{tick === 1 ? "1" : tick.toFixed(1).replace(".", ",")}</text>
              </g>
            );
          })}

          {xTicks.map((tick) => {
            const x = xPosition(tick);
            return (
              <g key={`x-${tick}`}>
                <line x1={x} y1={chart.top} x2={x} y2={chart.top + chart.height} className="roc-grid-line" />
                <text x={x} y={chart.top + chart.height + 20} textAnchor="middle" className="roc-tick-label">{tick === 0 ? "0" : tick.toFixed(2).replace(/0+$/, "").replace(/\.$/, "").replace(".", ",")}</text>
              </g>
            );
          })}

          <rect x={chart.left} y={chart.top} width={chart.width} height={chart.height} className="roc-chart-border" />

          {chartModels.map((model) => {
            const x = xPosition(model.fpr);
            const y = yPosition(model.tpr);
            return (
              <g key={model.name}>
                <title>{`${model.name}: FPR approximately ${model.fpr.toFixed(2)}, TPR approximately ${model.tpr.toFixed(2)}`}</title>
                <Marker model={model} x={x} y={y} />
              </g>
            );
          })}

          {chartModels.map((model, index) => {
            const y = 91 + index * 27;
            return (
              <g key={`legend-${model.name}`}>
                <Marker model={model} x={644} y={y - 4} size={5} />
                <text x={658} y={y} className="roc-legend-label">{model.name}</text>
              </g>
            );
          })}

          <text x={chart.left + chart.width / 2} y={chart.top + chart.height + 54} textAnchor="middle" className="roc-axis-label">False Positive Rate (FPR)</text>
          <text transform={`translate(17 ${chart.top + chart.height / 2}) rotate(-90)`} textAnchor="middle" className="roc-axis-label">True Positive Rate (TPR)</text>
        </svg>
      </div>

      <p className="model-cost-note">
        Coordinates are approximate estimates traced from the supplied figure. Replace them with measured ROC results before using this chart for evaluation.
      </p>
    </section>
  );
}

export default RocPointAnalysis;
