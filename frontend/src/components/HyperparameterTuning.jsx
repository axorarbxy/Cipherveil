const models = [
  {
    name: "RF",
    fullName: "Random Forest",
    search: ["n_estimators: [10, 25, 50, 100, 150]", "criterion: [gini, entropy]", "max_depth: 2–6", "min_samples_split: 2–6", "min_samples_leaf: 1–6"],
    best: ["criterion: entropy", "max_depth: 5", "min_samples_leaf: 1", "min_samples_split: 2", "n_estimators: 25"],
  },
  {
    name: "SVM",
    fullName: "Support Vector Machine",
    search: ["criterion: [gini, entropy]", "max_depth: 2–10", "min_samples_split: 2–10", "min_samples_leaf: 1–10"],
    best: ["estimator_criterion: gini", "estimator_max_depth: 4", "estimator_min_samples_leaf: 2", "estimator_min_samples_split: 4", "learning_rate: 1", "n_estimators: 100"],
  },
  {
    name: "DT",
    fullName: "Decision Tree",
    search: ["criterion: [gini, entropy]", "max_depth: 2–10", "min_samples_split: 2–10", "min_samples_leaf: 1–10"],
    best: ["criterion: entropy", "max_depth: 9", "min_samples_leaf: 2", "min_samples_split: 9"],
  },
  {
    name: "ADA",
    fullName: "AdaBoost",
    search: ["estimator_criterion: [gini, entropy]", "n_estimators: [50, 100, 150, 200]", "learning_rate: [0.1, 1, 10]", "estimator_max_depth: 2–5", "estimator_min_samples_split: 2–5", "estimator_min_samples_leaf: 1–5"],
    best: ["estimator_criterion: gini", "estimator_max_depth: 4", "estimator_min_samples_leaf: 2", "estimator_min_samples_split: 4", "learning_rate: 1", "n_estimators: 100"],
  },
  {
    name: "XGB",
    fullName: "XGBoost",
    search: ["n_estimators: [50, 100, 150, 200]", "learning_rate: [0.2, 0.3, 0.5, 1]", "subsample: [0.3, 0.4, 0.5, 0.7, 1]", "gamma: [0, 1, 3, 5]", "max_depth: [4, 5, 6, 10]", "tree_method: [hist]", "grow_policy: [lossguide]", "min_child_weight: [0, 3, 5]", "max_delta_step: [0, 1, 2, 5, 10]", "lambda: [0, 1, 2]", "alpha: [0, 1, 2]"],
    best: ["alpha: 0", "gamma: 5", "grow_policy: lossguide", "lambda: 0", "learning_rate: 1", "max_delta_step: 0", "max_depth: 5", "min_child_weight: 0", "n_estimators: 50", "subsample: 1"],
  },
];

function HyperparameterTuning() {
  return (
    <section className="tuning-panel" aria-labelledby="tuning-title">
      <div className="tuning-heading">
        <div>
          <p className="model-cost-eyebrow">MODEL DEVELOPMENT</p>
          <h3 id="tuning-title">Hyperparameter tuning</h3>
          <p className="model-cost-description">Explore the search space and compare the selected settings for each classifier.</p>
        </div>
        <span className="tuning-count">{models.length} classifiers</span>
      </div>

      <div className="tuning-table-wrap">
        <table className="tuning-table">
          <caption className="visually-hidden">Hyperparameter search spaces and best settings for five classifiers</caption>
          <thead>
            <tr>
              <th scope="col">Model</th>
              <th scope="col">Hyperparameter tuning space</th>
              <th scope="col">Best hyperparameter set</th>
            </tr>
          </thead>
          <tbody>
            {models.map((model) => (
              <tr key={model.name}>
                <th scope="row">
                  <span className={`tuning-model-mark tuning-model-${model.name.toLowerCase()}`}>{model.name}</span>
                  <span className="tuning-model-name">{model.fullName}</span>
                </th>
                <td><ul className="tuning-values">{model.search.map((value) => <li key={value}>{value}</li>)}</ul></td>
                <td><ul className="tuning-values selected">{model.best.map((value) => <li key={value}>{value}</li>)}</ul></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="model-cost-note">Parameter ranges and selected settings are transcribed from the supplied reference image. Confirm against the original experiment before treating these as measured results.</p>
    </section>
  );
}

export default HyperparameterTuning;
