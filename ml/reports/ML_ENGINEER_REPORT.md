# Member 2 — ML Engineer Comprehensive Technical Report
## Project: Ransomware Early-Warning System for Small Institutions (SIH CYB04)

---

### 1. Dataset Used
* **Dataset**: **MLRan** (Dynamic Behavioural Dataset for Ransomware Analysis and Detection)
* **Domain**: Windows API calls, Registry activity, File operations, Dropped extensions, Memory signatures, and Dynamic strings captured during runtime sandbox execution.

---

### 2. Training and Test Sample Counts
* **Training Partition (`X_train`)**: **3,905 samples**
  * Goodware (Class 0): **2,040 samples (52.2%)**
  * Ransomware (Class 1): **1,865 samples (47.8%)**
* **Untouched Test Partition (`X_test`)**: **975 samples**
  * Goodware (Class 0): **510 samples (52.3%)**
  * Ransomware (Class 1): **465 samples (47.7%)**
* **Total Samples**: **4,880 verified samples** across 64 ransomware families and diverse benign utilities.

---

### 3. Number of Features
* **483 numeric behavioral features** selected via Recursive Feature Elimination (RFE) in the benchmark dataset.
* Categorization:
  * Strings & Mutexes: 223 features
  * Registry Operations: 90 features
  * API Invocations: 63 features
  * System & Thread Operations: 38 features
  * Dropped Files & Extensions: 23 features
  * Memory Signatures: 20 features
  * File Operations: 16 features
  * Directory Traversals: 10 features

---

### 4. Preprocessing Method & Zero-Leakage Guarantee
* **Class**: `MLRanPreprocessor` (`src/preprocessing/preprocess_mlran.py`)
* **Strict Split Isolation**: Scalers and transformations fitted **strictly on `X_train`**. Test set remained completely untouched until final benchmark evaluation.
* **Dual Pipelines**:
  * `models/preprocessor_tree.joblib`: Unscaled feature pipeline for Random Forest and XGBoost.
  * `models/preprocessor_scaled.joblib`: `StandardScaler` pipeline for Logistic Regression and SVM.
* **Missing & Infinite Value Handling**: 0 missing values in MLRan; any runtime NaNs/Infs sanitized via `np.nan_to_num()`.

---

### 5. Models Trained & Compared
1. **Random Forest Classifier**: 100 estimators, max_depth=15, balanced class weights, unscaled features.
2. **XGBoost Classifier**: 100 estimators, max_depth=6, lr=0.1, logloss objective, unscaled features.
3. **Logistic Regression**: L2 regularization, max_iter=1000, balanced class weights, `StandardScaler`.
4. **SVM (RBF Kernel)**: Support Vector Classifier with RBF kernel, Platt probability calibration, `StandardScaler`.

---

### 6. Benchmark Evaluation Metrics (Untouched Test Set, $N=975$)

| Model | Preprocessing | Accuracy | Precision | Ransomware Recall | F1-Score | ROC-AUC | False Positive Rate (FPR) | False Negative Rate (FNR) | Latency (ms/sample) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **XGBoost (Tuned @ 0.40)** | **Unscaled** | **97.03%** | **0.9523** | **98.71%** (459/465) | **0.9694** | **0.9954** | **4.51%** (23/510) | **1.29%** (6/465) | **0.0038 ms** |
| **SVM (RBF Kernel)** | StandardScaler | **97.95%** | 0.9724 | 98.49% (458/465) | 0.9786 | 0.9971 | 2.55% (13/510) | 1.51% (7/465) | 0.1740 ms |
| **Logistic Regression** | StandardScaler | **97.85%** | 0.9703 | 98.49% (458/465) | 0.9776 | 0.9962 | 2.75% (14/510) | 1.51% (7/465) | 0.0017 ms |
| **Random Forest** | Unscaled | **96.72%** | 0.9558 | 97.63% (454/465) | 0.9660 | 0.9938 | 4.12% (21/510) | 2.37% (11/465) | 0.0307 ms |

---

### 7. Best Model Choice & Technical Justification

* **Final Selected Model**: **XGBoost Classifier** (`models/ransomware_model.joblib`)
* **Decision Threshold**: **`0.40`** (calibrated via 5-Fold Stratified Cross-Validation on `X_train` without test-set leakage).
* **Justification**:
  1. **Maximum Ransomware Recall**: **98.71%** (catches 459 out of 465 test attacks, missing only 6 stealth variants). In ransomware early warning, a False Negative leads to total system lockout, making recall the primary priority.
  2. **Inference Latency**: **0.0038 ms / sample** (~260,000 predictions/second) — **45× faster than SVM**, ensuring the background detection loop has zero noticeable CPU impact on resource-constrained institutional endpoints.
  3. **Exact TreeSHAP Compatibility**: Native polynomial-time TreeSHAP ($O(TLD^2)$) provides instant explainability for security alerts, whereas SVM requires expensive perturbation sampling.
  4. **Model Compactness**: 183 KB on disk.

---

### 8. SHAP Top Contributing Behavioral Features

Ranked by Mean Absolute SHAP Value across the test set:

1. `SYSTEM:DLL_LOADED:c:\windows\system32\ole32.dll` (Impact: 1.583) — COM automation / payload staging.
2. `REG:READ:HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList\...\ProfileImagePath` (Impact: 0.537) — Locating user document paths for encryption.
3. `SYSTEM:DLL_LOADED:uxtheme.dll` (Impact: 0.509) — UI window and theme suppression during malicious execution.
4. `STRING:!this program cannot be run in dos mode.` (Impact: 0.458) — Dynamic PE unpacking artifact.
5. `DROP:EXTENSION:ini` (Impact: 0.387) — Dropping configuration files in target directories.
6. `REG:READ:HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\MountPoints2\...` (Impact: 0.376) — Drive and volume mount enumeration.
7. `API:LdrGetProcedureAddress` (Impact: 0.214) — Dynamic runtime API resolution.
8. `API:NtAllocateVirtualMemory` (Impact: 0.212) — Allocating memory buffers for encryption staging.
9. `SIGNATURE:allocates_rwx` (Impact: 0.200) — Allocating Read-Write-Execute memory pages (shellcode indicator).
10. `STRING:kernel32.dll` (Impact: 0.199) — Core kernel API string references.

All SHAP figures generated:
* `reports/figures/shap/shap_summary.png` (Global Summary Beeswarm)
* `reports/figures/shap/shap_bar.png` (Global Feature Importance Bar Chart)
* `reports/figures/shap/local_tp_ransomware.png` (True Positive Waterfall)
* `reports/figures/shap/local_tn_goodware.png` (True Negative Waterfall)
* `reports/figures/shap/local_fp_sample.png` (False Positive Waterfall)
* `reports/figures/shap/local_fn_sample.png` (False Negative Waterfall)

---

### 9. Model Limitations
1. **Dynamic Sandbox Aggregation**: MLRan features represent aggregated run-time behavioral statistics. Coupling with real-time sector I/O monitoring further boosts early detection.
2. **Extreme Sleep Evasion**: Malware that delays malicious actions for days before triggering requires watchdog timers.

---

### 10. Reproduction Commands
```bash
# 1. Install Dependencies
pip install -r requirements.txt

# 2. Train Models
python src/train.py

# 3. Evaluate Models
python src/evaluate.py

# 4. Verify Full ML Module
python src/test_ml_module.py
```
