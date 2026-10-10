# Ransomware Early-Warning Machine Learning Documentation
## Smart India Hackathon CYB04 — Member 2 Deliverable

This documentation provides an end-to-end technical overview of the Machine Learning architectures, dataset evaluations, and inference modules for the Ransomware Early-Warning System.

---

### 1. Existing MLRan Baseline (Core Production Model)
* **Dataset**: MLRan (4,880 samples: 3,905 train, 975 test).
* **Features**: 483 numeric runtime dynamic behavioral indicators.
* **Production Model**: **XGBoost Classifier** (`models/ransomware_model.joblib`).
* **Decision Threshold**: **`0.40`**
* **Test Performance**:
  * **Ransomware Recall**: **98.71%** (459/465 attacks detected)
  * **Precision**: **95.23%**
  * **F1-Score**: **0.9694**
  * **ROC-AUC**: **0.9954**
  * **False Positive Rate (FPR)**: **4.51%**
  * **False Negative Rate (FNR)**: **1.29%**
  * **Inference Latency**: **0.0038 ms / sample** (~260,000 predictions/sec)

---

### 2. Multi-Dataset Research & Behavioral Taxonomy

#### Datasets Evaluated
1. **MLRan (Endpoint Runtime Layer)**: Dynamic API calls, registry modifications, dropped extensions, memory signatures.
2. **AD Early-Stage Dataset (Active Directory Layer)**: Enterprise Windows Event Logs (EventID 4688, 4624, 4672, 4657, 5140) capturing the initial 20–25 minutes of lateral staging.
3. **RanSAP (Storage Layer)**: Low-level ATA block storage read/write patterns, I/O burstiness, and sector Shannon entropy.
4. **RanSMAP (Memory & Storage Layer)**: Storage access patterns with concurrent memory bus telemetry under multitasking workloads.

#### Behavioral Feature Alignment Schema (`models/feature_mapping.json`)
* **FILE_OPERATIONS**: High-frequency modifications, mass overwrites, rapid extension alters.
* **STORAGE_ENTROPY**: Block entropy spikes ($>7.5$ bits/byte) indicating ciphertext staging.
* **PROCESS_ACTIVITY**: Process creations, thread injections, virtual memory allocation.
* **SYSTEM_REGISTRY**: Profile enumeration, persistence autorun keys, volume drive checks.
* **NETWORK_LATERAL**: Active Directory network logons (Type 3) and remote SMB share access.

---

### 3. Multi-Dataset Model Benchmarks

| Telemetry Domain | Dataset | Model | Accuracy | Recall | Precision | F1-Score | ROC-AUC |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Endpoint Runtime** | **MLRan (Primary)** | **XGBoost (Tuned @ 0.40)** | **97.03%** | **98.71%** | **95.23%** | **0.9694** | **0.9954** |
| Endpoint Runtime | MLRan | SVM (RBF) | 97.95% | 98.49% | 97.24% | 0.9786 | 0.9971 |
| Endpoint Runtime | MLRan | Logistic Regression | 97.85% | 98.49% | 97.03% | 0.9776 | 0.9962 |
| Endpoint Runtime | MLRan | Random Forest | 96.72% | 97.63% | 95.58% | 0.9660 | 0.9938 |
| **Enterprise AD** | **AD Early-Stage** | **XGBoost** | **99.64%** | **99.87%** | **99.75%** | **0.9981** | **0.9995** |
| Enterprise AD | AD Early-Stage | Random Forest | 99.48% | 99.79% | 99.67% | 0.9973 | 0.9992 |
| Enterprise AD | AD Early-Stage | SVM (RBF) | 99.36% | 99.67% | 99.67% | 0.9967 | 0.9988 |
| **Storage Block I/O**| **RanSAP** | **XGBoost** | **99.50%** | **99.00%** | **100.0%** | **0.9950** | **0.9998** |
| Storage Block I/O | RanSAP | Random Forest | 99.00% | 98.00% | 100.0% | 0.9899 | 0.9996 |

---

### 4. SHAP Explainability Engine
* **Technology**: TreeSHAP on XGBoost ($O(TLD^2)$ exact Shapley values).
* **Key Indicators Driving Ransomware Predictions**:
  1. `SYSTEM:DLL_LOADED:...ole32.dll` (COM automation & payload staging)
  2. `REG:READ:...ProfileList\...\ProfileImagePath` (Target user directory reconnaissance)
  3. `SYSTEM:DLL_LOADED:uxtheme.dll` (UI window suppression)
  4. `STRING:!this program cannot be run in dos mode.` (PE unpacking artifact)
  5. `DROP:EXTENSION:ini` (Dropped configuration files)

---

### 5. Production Prediction API
```python
from src.predict import predict_ransomware

# Ingest observed telemetry
result = predict_ransomware({"6412331": 1.0, "237274": 0.0, "6468211": 1.0})
print(result)
```

**Output Schema**:
```json
{
  "prediction": "RANSOMWARE",
  "is_ransomware": true,
  "probability": 0.9982,
  "risk_score": 100,
  "risk_level": "CRITICAL",
  "decision_threshold": 0.4,
  "top_contributing_features": [...]
}
```

---

### 6. Reproduction Commands
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run verification tests
python src/test_ml_module.py

# 3. Train models
python src/train.py

# 4. Evaluate models
python src/evaluate.py
```
