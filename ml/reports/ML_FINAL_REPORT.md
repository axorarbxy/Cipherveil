# Member 2 — ML Engineer Final Comprehensive Report

## Project: Ransomware Early-Warning System for Small Institutions (SIH CYB04)

---

### 1. Existing MLRan Baseline Results (Preserved & Verified)

* **Dataset**: MLRan (`data/raw/MLRan/`, 4,880 samples, 483 behavioral features)
* **Model**: XGBoost Classifier (`models/ransomware_model.joblib`)
* **Decision Threshold**: `0.40`
* **Test Performance ($N=975$, 510 Benign, 465 Ransomware)**:
  * Accuracy: **97.03%**
  * Precision: **95.23%**
  * Recall: **98.71%** (459 / 465 ransomware variants detected)
  * F1-Score: **0.9694**
  * ROC-AUC: **0.9954**
  * False Positive Rate (FPR): **4.51%**
  * False Negative Rate (FNR): **1.29%**
  * Inference Latency: **0.0038 ms / sample**

---

### 2. Multi-Dataset Research & Evaluation (RanSAP, RanSMAP, AD Early-Stage)

To validate the model across the cybersecurity telemetry hierarchy, three additional research datasets were analyzed and benchmarked:

#### Summary Metrics Across All Evaluated Datasets:

| Telemetry Layer | Dataset | Selected Model | Samples | Accuracy | Recall | Precision | F1-Score | ROC-AUC | FPR | FNR |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Endpoint Runtime** | **MLRan (Baseline)** | **XGBoost (Tuned @ 0.40)** | **975** | **97.03%** | **98.71%** | **95.23%** | **0.9694** | **0.9954** | **4.51%** | **1.29%** |
| Endpoint Runtime | MLRan | SVM (RBF) | 975 | 97.95% | 98.49% | 97.24% | 0.9786 | 0.9971 | 2.55% | 1.51% |
| Endpoint Runtime | MLRan | Logistic Regression | 975 | 97.85% | 98.49% | 97.03% | 0.9776 | 0.9962 | 2.75% | 1.51% |
| Endpoint Runtime | MLRan | Random Forest | 975 | 96.72% | 97.63% | 95.58% | 0.9660 | 0.9938 | 4.12% | 2.37% |
| **Enterprise AD** | **AD Early-Stage** | **XGBoost** | **6,961** | **99.64%** | **99.87%** | **99.75%** | **0.9981** | **0.9995** | **0.25%** | **0.13%** |
| Enterprise AD | AD Early-Stage | Random Forest | 6,961 | 99.48% | 99.79% | 99.67% | 0.9973 | 0.9992 | 0.33% | 0.21% |
| **Storage Block I/O**| **RanSAP** | **XGBoost** | **400** | **99.50%** | **99.00%** | **100.0%** | **0.9950** | **0.9998** | **0.00%** | **1.00%** |
| Storage Block I/O | RanSAP | Random Forest | 400 | 99.00% | 98.00% | 100.0% | 0.9899 | 0.9996 | 0.00% | 2.00% |

---

### 3. Key Findings on Multi-Dataset Compatibility
1. **Layered Early-Warning Hierarchy**:
   * **Stage 0 (Lateral Movement)**: Active Directory Event Log models detect reconnaissance (EventID 4688, 4624) before encryption code is dropped.
   * **Stage 1 (Payload Execution)**: MLRan XGBoost model detects API, registry, and privilege escalation in memory ($98.71\%$ recall, $0.0038$ ms latency).
   * **Stage 2 (Bulk Overwrites)**: RanSAP storage layer detects high block write burstiness and Shannon entropy ($>7.5$) as an independent safety net.
2. **Zero Data Leakage**: All models were trained strictly on independent training folds with zero metadata or hash contamination.

---

### 4. Deliverables & Packaging
* All ML artifacts are packaged in `ML_Engineer_Final.zip` containing `src/`, `models/`, `reports/`, `notebooks/`, `data/processed/`, `requirements.txt`, `README.md`, and `ML_Documentation.md`.
