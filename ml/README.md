# Ransomware Early-Warning System for Small Institutions
## Machine Learning Detection Module

---

### Overview
This repository contains the standalone **Machine Learning Detection Module** built for the Smart India Hackathon project *"Ransomware Early-Warning System for Small Institutions"*.

The module analyzes dynamic system behavioral data and delivers:
1. **Normal / Ransomware Classification**
2. **Calibrated Ransomware Probability**
3. **Institutional Risk Score ($0 - 100$) & Threat Alert Tiers**
4. **SHAP (TreeSHAP) Explainability & Top Contributing Behavioral Factors**

---

### Project Structure
```text
ransomware_ml/
├── data/
│   ├── raw/MLRan/                     # Verified raw MLRan dataset CSVs and JSON
│   └── processed/                     # Preprocessed train/test matrices
├── models/
│   ├── ransomware_model.joblib        # Primary detector (XGBoost)
│   ├── preprocessor_tree.joblib       # Serialized tree-based preprocessor
│   ├── preprocessor_scaled.joblib     # StandardScaler preprocessor
│   ├── model_config.json              # Operational thresholds & metadata
│   └── feature_metadata.json          # 483 feature IDs & readable mappings
├── notebooks/
│   ├── 01_eda.ipynb                   # Exploratory Data Analysis
│   ├── 02_preprocessing.ipynb         # Data Preprocessing & Validation
│   ├── 04_model_training.ipynb        # Baseline Model Training & Comparison
│   └── 05_shap_analysis.ipynb         # TreeSHAP Global & Local Explainability
├── reports/
│   ├── model_comparison.csv           # Baseline evaluation table
│   ├── threshold_analysis.csv         # Cross-validation threshold metrics
│   ├── shap_feature_importance.csv    # Ranked SHAP feature importance
│   ├── final_model_selection.md       # Comprehensive selection report
│   └── figures/                       # ROC curves, confusion matrices, SHAP plots
├── src/
│   ├── preprocessing/                 # Reusable preprocessing pipeline
│   ├── risk_score.py                  # Risk scoring engine (0-100 & tiers)
│   ├── explain.py                     # TreeSHAP explainer engine
│   ├── predict.py                     # Standalone predict_ransomware API
│   ├── train.py                       # CLI model trainer
│   └── evaluate.py                    # CLI model evaluator
├── requirements.txt
└── README.md
```

---

### Key Benchmark Results (Test Set, $N=975$)

| Model | Accuracy | Precision | Recall (Ransomware) | F1-Score | ROC-AUC | FPR | FNR | Latency |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **XGBoost (Tuned @ 0.40)** | **97.03%** | **95.23%** | **98.71%** | **0.9694** | **0.9954** | **4.51%** | **1.29%** | **0.0038 ms** |
| **SVM (RBF Kernel)** | 97.95% | 97.24% | 98.49% | 0.9786 | 0.9971 | 2.55% | 1.51% | 0.1740 ms |
| **Logistic Regression** | 97.85% | 97.03% | 98.49% | 0.9776 | 0.9962 | 2.75% | 1.51% | 0.0017 ms |
| **Random Forest** | 96.72% | 95.58% | 97.63% | 0.9660 | 0.9938 | 4.12% | 2.37% | 0.0307 ms |

---

### How to Use

#### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Run Inference via Python API
```python
from src.predict import predict_ransomware

# Pass a dictionary of behavioral features
sample_telemetry = {"6412331": 1.0, "237274": 0.0, "6468211": 1.0}
result = predict_ransomware(sample_telemetry)

print(result)
```

**Output**:
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
      "feature_name": "SIGNATURE:persistence_autorun",
      "shap_impact": 0.8007,
      "direction": "+RANSOMWARE"
    }
  ]
}
```
