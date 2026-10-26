const models = [
  { name: "RF", falsePositives: 25, falseNegatives: 310 },
  { name: "SVM", falsePositives: 23, falseNegatives: 330 },
  { name: "DT", falsePositives: 2, falseNegatives: 210 },
  { name: "ADA", falsePositives: 2, falseNegatives: 270 },
  { name: "XGB", falsePositives: 5, falseNegatives: 170 },
];

const falsePositiveCost = 1;
const falseNegativeCost = 10;

function getWeightedCost(model) {
  return model.falsePositives * falsePositiveCost + model.falseNegatives * falseNegativeCost;
}

function ModelCostMatrix() {
  const lowestCost = Math.min(...models.map(getWeightedCost));
  const highestCost = Math.max(...models.map(getWeightedCost));

  return (
    <section className="model-cost-panel" aria-labelledby="model-cost-title">
      <div className="model-cost-heading">
        <div>
          <p className="model-cost-eyebrow">MODEL EVALUATION</p>
          <h3 id="model-cost-title">Cost matrix analysis</h3>
          <p className="model-cost-description">
            Compare false alarms with missed ransomware detections across classifiers.
          </p>
        </div>
        <span className="model-cost-formula">Cost = 1 × FP + 10 × FN</span>
      </div>

      <div className="model-cost-table-wrap">
        <table className="model-cost-table">
          <caption className="visually-hidden">
            Example false positive, false negative, and weighted cost values for five classifiers
          </caption>
          <thead>
            <tr>
              <th scope="col">Metric</th>
              {models.map((model) => <th scope="col" key={model.name}>{model.name}</th>)}
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="row">False positives (FP)</th>
              {models.map((model) => <td key={model.name}>{model.falsePositives}</td>)}
            </tr>
            <tr>
              <th scope="row">False negatives (FN)</th>
              {models.map((model) => <td key={model.name}>{model.falseNegatives}</td>)}
            </tr>
            <tr className="model-cost-total-row">
              <th scope="row">Weighted total cost</th>
              {models.map((model) => (
                <td className={getWeightedCost(model) === lowestCost ? "lowest-cost" : ""} key={model.name}>
                  {getWeightedCost(model).toLocaleString("en-US")}
                  {getWeightedCost(model) === lowestCost && <span className="best-model-tag">Lowest</span>}
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>

      <div className="model-cost-bars" aria-label="Relative weighted cost comparison">
        {models.map((model) => {
          const cost = getWeightedCost(model);
          return (
            <div className="model-cost-bar-row" key={model.name}>
              <span>{model.name}</span>
              <div className="model-cost-track" aria-hidden="true">
                <div
                  className={cost === lowestCost ? "model-cost-fill best" : "model-cost-fill"}
                  style={{ width: `${(cost / highestCost) * 100}%` }}
                />
              </div>
              <strong>{cost.toLocaleString("en-US")}</strong>
            </div>
          );
        })}
      </div>

      <p className="model-cost-note">
        Example counts transcribed from the supplied reference. Weighted costs are recalculated using its stated penalties
        (FP = 1, FN = 10); replace the example counts with measured evaluation results before drawing research conclusions.
      </p>
    </section>
  );
}

export default ModelCostMatrix;
