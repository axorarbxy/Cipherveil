# Step 4 — Final Model Selection, Risk Scoring & SHAP Explainability Report

## Ransomware Early-Warning System for Small Institutions (ML Module)

---

### 1. Executive Decision & Transparent Model Comparison

An early-warning ransomware detection system operating on resource-constrained endpoints in small institutions (e.g. schools, municipal offices, primary clinics) requires balancing:
1. **Ransomware Recall**: Missing an active ransomware payload causes catastrophic data loss.
2. **False Alarm Rate (FPR)**: Excessive false positives cause alert fatigue and disruption to normal work.
3. **Inference Latency & CPU Overhead**: Must execute in real time without bogging down host processors.
4. **Explainability**: Security responders must immediately understand *why* an alert was generated.

#### Multi-Criteria Decision Matrix

| Dimension | XGBoost (Selected Primary) | SVM (RBF Kernel) | Logistic Regression | Random Forest |
| :--- | :--- | :--- | :--- | :--- |
| **Test Accuracy** | 97.03% (Tuned) | **97.95%** | 97.85% | 96.72% |
| **Ransomware Recall** | **98.71%** (459/465) | 98.49% (458/465) | 98.49% (458/465) | 97.63% (454/465) |
| **False Negative Rate (FNR)** | **1.29%** (Only 6 missed) | 1.51% (7 missed) | 1.51% (7 missed) | 2.37% (11 missed) |
| **False Positive Rate (FPR)** | 4.51% | **2.55%** | 2.75% | 4.12% |
| **ROC-AUC** | **0.9954** | **0.9971** | 0.9962 | 0.9938 |
| **Inference Latency** | **0.0038 ms / sample** | 0.1740 ms / sample | **0.0017 ms / sample** | 0.0307 ms / sample |
| **Throughput** | **~260,000 samples/sec** | ~5,700 samples/sec | ~580,000 samples/sec | ~32,000 samples/sec |
| **Model File Size** | **183 KB** | 2,238 KB | **4.7 KB** | 1,879 KB |
| **SHAP Explainability** | **Exact TreeSHAP ($O(TLD^2)$)** | KernelSHAP (Exponential/Sampled) | Linear Weights only | Exact TreeSHAP |
| **Endpoint Readiness** | **Superior** | Poor (High CPU) | Good (Linear only) | Moderate |

#### Why XGBoost was Selected over SVM:
* **Inference Speed**: XGBoost is **45× faster** than SVM (0.0038 ms vs 0.1740 ms per sample), critical for low-overhead background monitoring.
* **SHAP Performance**: XGBoost supports **TreeSHAP**, computing exact local explanations in sub-milliseconds, whereas SVM requires expensive perturbation-based KernelSHAP sampling.
* **Model Size**: XGBoost (183 KB) is **12× smaller** than SVM (2.2 MB).

---

### 2. Probability Calibration & Reliability Analysis

* **Methodology**: 5-Fold Stratified Cross-Validation on `X_train` was used to evaluate calibration without test-set contamination.
* **Brier Scores (Lower = Better Calibrated)**:
  * Logistic Regression: `0.0057`
  * SVM (RBF): `0.0074`
  * XGBoost: `0.0111`
  * Random Forest: `0.0116`
* **Plot**: `reports/figures/calibration_curves.png`

---

### 3. Operational Decision Threshold Tuning

Because missing ransomware is significantly more damaging than generating occasional warnings, the decision threshold was tuned using **5-Fold Cross-Validation strictly on `X_train`**:

| Threshold | CV Accuracy | CV Precision | CV Recall | CV F1-Score | CV FPR | CV FNR | Operational Assessment |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 0.20 | 98.39% | 0.9722 | 99.46% | 0.9833 | 2.60% | 0.54% | Highest sensitivity, slightly more alarms |
| 0.30 | 98.59% | 0.9773 | 99.36% | 0.9854 | 2.11% | 0.64% | Balanced high-sensitivity tier |
| **0.40 (Selected)** | **98.57%** | **0.9798** | **99.03%** | **0.9851** | **1.86%** | **0.97%** | **Optimal institutional operating point** |
| 0.50 (Default) | 98.57% | 0.9824 | 98.77% | 0.9850 | 1.62% | 1.23% | Standard default |
| 0.70 | 98.54% | 0.9865 | 98.28% | 0.9847 | 1.23% | 1.72% | Too conservative (misses stealthy variants) |

#### Untouched Test Set Verification (Threshold = 0.40):
* **Accuracy**: **97.03%**
* **Precision**: **95.23%**
* **Recall (Ransomware)**: **98.71%** (Caught **459 of 465** test ransomware samples)
* **F1-Score**: **0.9694**
* **FPR**: **4.51%** (23 / 510 false alarms)
* **FNR**: **1.29%** (Only 6 missed attacks)

---

### 4. SHAP Global & Local Explainability Findings

#### Top 10 Most Influential Behavioral Indicators (Global TreeSHAP)

1. `SYSTEM:DLL_LOADED:c:\windows\system32\ole32.dll` (Impact: 1.583) — Object linking/embedding library utilized for COM automation and payload delivery.
2. `REG:READ:...\ProfileList\...\ProfileImagePath` (Impact: 0.537) — Registry enumeration used to locate target user document directories.
3. `SYSTEM:DLL_LOADED:uxtheme.dll` (Impact: 0.509) — UI theme loading patterns during execution.
4. `STRING:!this program cannot be run in dos mode.` (Impact: 0.458) — Embedded PE header string indicative of dynamically unpacked executables.
5. `DROP:EXTENSION:ini` (Impact: 0.387) — Dropping configuration files into target directories.
6. `REG:READ:...\MountPoints2\CPC\Volume\...` (Impact: 0.376) — Drive and volume mount point enumeration prior to multi-volume encryption.
7. `API:LdrGetProcedureAddress` (Impact: 0.214) — Dynamic API resolution to evade static signature scanning.
8. `API:NtAllocateVirtualMemory` (Impact: 0.212) — Allocating memory buffers for encryption keys and file staging.
9. `SIGNATURE:allocates_rwx` (Impact: 0.200) — Allocating Read-Write-Execute memory pages (classic shellcode / unpacker indicator).
10. `STRING:kernel32.dll` (Impact: 0.199) — Core kernel API string references.

#### Local Explanation Artifacts
* `reports/figures/shap/shap_summary.png` (Global Beeswarm Summary)
* `reports/figures/shap/shap_bar.png` (Global Importance Bar Chart)
* `reports/figures/shap/local_tp_ransomware.png` (True Positive Waterfall breakdown)
* `reports/figures/shap/local_tn_goodware.png` (True Negative Waterfall breakdown)
* `reports/figures/shap/local_fp_sample.png` (False Positive Analysis)
* `reports/figures/shap/local_fn_sample.png` (False Negative Analysis)

---

### 5. Risk Scoring Engine Design (`src/risk_score.py`)

Risk scores are computed on a normalized scale ($0 - 100$) reflecting threat severity:

$$	ext{Risk Score} = 	ext{round}(	ext{Probability} 	imes 100)$$

| Risk Score Range | Threat Level | Recommended Action for Small Institutions |
| :--- | :--- | :--- |
| **0 – 30** | `NORMAL` | Standard baseline benign activity; telemetry logged quietly. |
| **31 – 60** | `WATCH` | Elevated anomaly detected; increase telemetry sampling frequency. |
| **61 – 80** | `SUSPICIOUS` | High probability of malicious intent; alert IT administrator. |
| **81 – 100** | `CRITICAL` | Confirmed ransomware behavior; trigger immediate containment workflows. |

---

### 6. Production Prediction Module (`src/predict.py`)

The inference function `predict_ransomware(features)` ingests raw behavioral telemetry and outputs:

```json
{
  "prediction": "RANSOMWARE",
  "is_ransomware": true,
  "probability": 0.9982,
  "risk_score": 100,
  "risk_level": "CRITICAL",
  "decision_threshold": 0.4,
  "top_contributing_features": [
    {
      "feature_name": "REG:READ:...\MountPoints2\CPC\Volume\...\Data",
      "value": 1.0,
      "shap_impact": 1.6353,
      "direction": "+RANSOMWARE"
    },
    {
      "feature_name": "SIGNATURE:persistence_autorun",
      "value": 1.0,
      "shap_impact": 0.8007,
      "direction": "+RANSOMWARE"
    },
    {
      "feature_name": "SIGNATURE:console_output",
      "value": 1.0,
      "shap_impact": 0.5932,
      "direction": "+RANSOMWARE"
    }
  ]
}
```

---

### 7. Known Limitations

1. **Static vs. Temporal Context**: MLRan feature matrices aggregate sandbox run-time statistics. While highly effective, pairing with sub-second sector I/O streams (RanSAP/RanSMAP) provides even earlier millisecond-level detection.
2. **Obfuscation Evasion**: Advanced malware using kernel rootkits or sleeping for hours before activating may require complementary heuristic watchdog timers.
