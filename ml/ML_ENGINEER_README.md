# Member 2 — ML Engineer Deliverables
## Ransomware Early-Warning System for Small Institutions (SIH CYB04)

This package contains the complete, production-ready **Machine Learning Detection and Explainability Engine** developed for the SIH project.

---

### Quick Start Guide

#### 1. Install Required Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Run Automated Verification Tests
Run the end-to-end ML test suite to verify model loading, preprocessor transformations, prediction API, risk scoring, and TreeSHAP explainability:
```bash
python src/test_ml_module.py
```

#### 3. Train All Models from Scratch (Optional)
```bash
python src/train.py
```

#### 4. Evaluate Models on Test Data
```bash
python src/evaluate.py
```

---

### How to Use the Prediction API in Other Modules

Import the primary `predict_ransomware` function directly:

```python
from src.predict import predict_ransomware

# Input can be a dictionary of active behavioral indicators
sample_telemetry = {
    "SIGNATURE:persistence_autorun": 1.0,
    "DROP:EXTENSION:ini": 1.0,
    "SYSTEM:DLL_LOADED:uxtheme.dll": 1.0
}

# Ingest and predict
result = predict_ransomware(sample_telemetry)

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
  "top_contributing_features": [
    {
      "feature_id": "153306",
      "feature_name": "REG:READ:HKEY_CURRENT_USER\...\MountPoints2\...\Data",
      "value": 1.0,
      "shap_impact": 1.6353,
      "direction": "+RANSOMWARE",
      "description": "REG:READ:... (Impact: +1.635)"
    }
  ]
}
```

---

### Package Directory Structure
```text
Member_2_ML_Engineer/
├── data/
│   └── README.md
├── models/
│   ├── ransomware_model.joblib        # Primary XGBoost detector
│   ├── random_forest.joblib           # Random Forest model
│   ├── xgboost.joblib                 # XGBoost model
│   ├── logistic_regression.joblib     # Logistic Regression model
│   ├── svm.joblib                     # SVM RBF model
│   ├── preprocessor_tree.joblib       # Production Tree Preprocessor
│   ├── preprocessor_scaled.joblib     # Production Scaled Preprocessor
│   ├── feature_metadata.json          # 483 feature mapping schema
│   └── model_config.json              # Model configuration & threshold
├── src/
│   ├── predict.py                     # predict_ransomware() inference engine
│   ├── risk_score.py                  # 0-100 institutional risk scorer
│   ├── explain.py                     # TreeSHAP explainability engine
│   ├── train.py                       # CLI model training script
│   ├── evaluate.py                    # CLI model evaluation script
│   ├── preprocessing.py               # Preprocessing interface
│   ├── preprocessing/                 # MLRanPreprocessor implementation
│   └── test_ml_module.py              # Production verification test suite
├── reports/
│   ├── model_comparison.csv           # Benchmark comparison metrics
│   ├── shap_feature_importance.csv    # 483-feature SHAP importance rankings
│   ├── ML_ENGINEER_REPORT.md          # Comprehensive technical report
│   └── figures/
│       └── shap/                      # Global & local SHAP waterfall plots
├── notebooks/
│   ├── 01_eda.ipynb                   # Exploratory Data Analysis
│   ├── 02_preprocessing.ipynb         # Preprocessing pipeline validation
│   ├── 04_model_training.ipynb        # Model benchmark & training
│   └── 05_shap_analysis.ipynb         # SHAP explainability analysis
├── requirements.txt
└── ML_ENGINEER_README.md
```
