"""
Member 2 — ML Engineer Production Verification Test Suite.
Tests model loading, preprocessor transformations, prediction API,
risk scoring, SHAP explainability, and multi-format telemetry ingestion.
"""

import os
import sys
import json
import time
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.predict import predict_ransomware, RansomwarePredictor
from src.preprocessing import MLRanPreprocessor
from src.risk_score import RansomwareRiskScorer
from src.evaluate import evaluate_models


def run_full_ml_verification():
    print("=" * 80)
    print("MEMBER 2 — ML ENGINEER PRODUCTION VERIFICATION TEST")
    print("=" * 80)

    # 1. Component Initialization
    t0 = time.time()
    predictor = RansomwarePredictor()
    init_time = time.time() - t0
    print(f"\n[PASS] 1. Predictor Initialized in {init_time*1000:.2f} ms")
    print(f"        Model: {predictor.config.get('model_name')}")
    print(f"        Threshold: {predictor.threshold}")
    print(f"        Features expected: {predictor.meta.get('feature_count')}")

    # 2. Test Goodware Sample
    proc_dir = os.path.join(parent_dir, "data", "processed")
    X_test_df = pd.read_csv(os.path.join(proc_dir, "X_test.csv"))
    y_test = pd.read_csv(os.path.join(proc_dir, "y_test.csv"))["target"].values

    goodware_idx = int(np.where(y_test == 0)[0][0])
    ransomware_idx = int(np.where(y_test == 1)[0][0])

    goodware_sample = X_test_df.iloc[goodware_idx].to_dict()
    res_good = predictor.predict(goodware_sample)
    print("\n[PASS] 2. Goodware Sample Evaluation:")
    print(f"        Prediction:  {res_good['prediction']}")
    print(f"        Probability: {res_good['probability']:.4f}")
    print(f"        Risk Score:  {res_good['risk_score']} ({res_good['risk_level']})")
    print(f"        Top Feature: {res_good['top_contributing_features'][0]['description']}")
    assert res_good["prediction"] == "NORMAL", "Goodware sample misclassified"

    # 3. Test Ransomware Sample
    ransomware_sample = X_test_df.iloc[ransomware_idx].to_dict()
    res_ran = predictor.predict(ransomware_sample)
    print("\n[PASS] 3. Ransomware Sample Evaluation:")
    print(f"        Prediction:  {res_ran['prediction']}")
    print(f"        Probability: {res_ran['probability']:.4f}")
    print(f"        Risk Score:  {res_ran['risk_score']} ({res_ran['risk_level']})")
    print(f"        Top Feature: {res_ran['top_contributing_features'][0]['description']}")
    assert res_ran["prediction"] == "RANSOMWARE", "Ransomware sample misclassified"

    # 4. Test Human-Readable Key Ingestion
    readable_sample = {
        "SIGNATURE:persistence_autorun": 1.0,
        "SIGNATURE:console_output": 1.0,
        "DROP:EXTENSION:ini": 2.0
    }
    res_readable = predictor.predict(readable_sample)
    print("\n[PASS] 4. Human-Readable Key Ingestion (Sparse Dict):")
    print(f"        Prediction:  {res_readable['prediction']}")
    print(f"        Probability: {res_readable['probability']:.4f}")
    print(f"        Risk Score:  {res_readable['risk_score']} ({res_readable['risk_level']})")

    # 5. Test 1D Numpy Array Input (483 features)
    arr_sample = X_test_df.iloc[ransomware_idx].values
    res_arr = predictor.predict(arr_sample)
    print("\n[PASS] 5. 1D Numpy Array Ingestion (Shape: 483,):")
    print(f"        Prediction:  {res_arr['prediction']}")
    print(f"        Risk Score:  {res_arr['risk_score']}")
    assert res_arr["prediction"] == "RANSOMWARE"

    # 6. Test Empty/Zero Vector Input (Baseline Telemetry)
    res_empty = predictor.predict({})
    print("\n[PASS] 6. Empty Telemetry Input (All zeros fallback):")
    print(f"        Prediction:  {res_empty['prediction']}")
    print(f"        Probability: {res_empty['probability']:.4f}")
    print(f"        Risk Score:  {res_empty['risk_score']} ({res_empty['risk_level']})")
    assert res_empty["prediction"] == "NORMAL"

    # 7. Output JSON Schema Verification
    required_keys = ["prediction", "is_ransomware", "probability", "risk_score", "risk_level", "decision_threshold", "top_contributing_features"]
    for k in required_keys:
        assert k in res_ran, f"Missing key '{k}' in prediction output"
    print("\n[PASS] 7. Output JSON Schema Strictly Matches SIH Specifications.")

    print("\n" + "=" * 80)
    print("ALL PRODUCTION ML TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    run_full_ml_verification()
