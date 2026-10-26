const cohorts = [
  { name: "MLRan", context: "Endpoint behavior", samples: "975", features: 483, recall: 98.49, fpr: 4.51, model: "XGBoost" },
  { name: "AD Early-Stage", context: "Directory activity", samples: "6,961", features: 13, recall: 99.99, fpr: 0, model: "XGBoost" },
  { name: "RanSAP Storage I/O", context: "Storage behavior", samples: "400", features: 5, recall: 81, fpr: 7.67, model: "XGBoost" },
];

const lifecycle = [
  { number: "01", title: "Monitor drift", detail: "Track feature and score distributions by environment." },
  { number: "02", title: "Verify labels", detail: "Add analyst-confirmed outcomes from new campaigns and benign workloads." },
  { number: "03", title: "Train candidate", detail: "Keep each dataset's feature adapter and provenance with the candidate." },
  { number: "04", title: "Validate & review", detail: "Compare per-cohort recall and false alarms before an approved release." },
];

function EnterpriseModelReadiness() {
  return (
    <section className="enterprise-readiness" aria-labelledby="enterprise-readiness-title">
      <div className="enterprise-readiness-heading">
        <div>
          <p className="model-cost-eyebrow">GENERALIZATION & MODEL LIFECYCLE</p>
          <h3 id="enterprise-readiness-title">Enterprise validation & resilience</h3>
          <p className="model-cost-description">Review performance across distinct behavior cohorts and the proposed guardrails for model refreshes.</p>
        </div>
        <span className="enterprise-evidence-tag">3 reported cohorts</span>
      </div>

      <div className="enterprise-cohort-grid">
        {cohorts.map((cohort) => (
          <article className="enterprise-cohort" key={cohort.name}>
            <div className="enterprise-cohort-topline">
              <div>
                <h4>{cohort.name}</h4>
                <p>{cohort.context}</p>
              </div>
              <span>{cohort.features} features</span>
            </div>
            <p className="enterprise-samples">{cohort.samples} evaluation samples <span>·</span> {cohort.model}</p>
            <div className="enterprise-metric">
              <div><span>Ransomware recall</span><strong>{cohort.recall.toFixed(2)}%</strong></div>
              <div className="enterprise-meter" role="img" aria-label={`${cohort.recall.toFixed(2)} percent ransomware recall`}>
                <span style={{ width: `${cohort.recall}%` }} />
              </div>
            </div>
            <div className="enterprise-cohort-footer">
              <span>False positive rate</span><strong>{cohort.fpr.toFixed(2)}%</strong>
            </div>
          </article>
        ))}
      </div>

      <div className="enterprise-lifecycle">
        <div className="enterprise-lifecycle-title">
          <div>
            <h4>Adaptive retraining release gates</h4>
            <p>Recommended workflow; candidate training and promotion are not automated yet.</p>
          </div>
          <span className="enterprise-manual-tag">Human approval required</span>
        </div>
        <ol className="enterprise-lifecycle-steps">
          {lifecycle.map((step) => (
            <li key={step.number}>
              <span className="enterprise-step-number">{step.number}</span>
              <div><strong>{step.title}</strong><p>{step.detail}</p></div>
            </li>
          ))}
        </ol>
      </div>

      <p className="model-cost-note">Reported comparison values are from <code>ml/reports/multi_dataset_model_comparison.csv</code>. Feature counts differ, so these cohorts are evaluated independently; the results do not establish cross-environment generalization on their own.</p>
    </section>
  );
}

export default EnterpriseModelReadiness;
