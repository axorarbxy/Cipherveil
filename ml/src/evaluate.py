"""
Model Evaluation Module.
Evaluates saved models on unseen test data, computes metrics, and generates comparison reports.
"""

import os
import sys

# Ensure project root is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import json
import logging
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)

from src.preprocessing import MLRanPreprocessor

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def evaluate_models(
    processed_dir: str,
    models_dir: str,
    reports_dir: str
) -> pd.DataFrame:
    os.makedirs(reports_dir, exist_ok=True)
    
    # Load test data
    X_test_df = pd.read_csv(os.path.join(processed_dir, "X_test.csv"))
    y_test = pd.read_csv(os.path.join(processed_dir, "y_test.csv"))["target"].values

    prep_tree = MLRanPreprocessor.load(os.path.join(models_dir, "preprocessor_tree.joblib"))
    prep_scaled = MLRanPreprocessor.load(os.path.join(models_dir, "preprocessor_scaled.joblib"))

    X_test_tree = prep_tree.transform(X_test_df)
    X_test_scaled = prep_scaled.transform(X_test_df)

    models = [
        ("Random Forest", "random_forest.joblib", X_test_tree, "unscaled"),
        ("XGBoost", "xgboost.joblib", X_test_tree, "unscaled"),
        ("Logistic Regression", "logistic_regression.joblib", X_test_scaled, "StandardScaler"),
        ("SVM (RBF Kernel)", "svm.joblib", X_test_scaled, "StandardScaler")
    ]

    records = []
    for name, filename, X_data, prep_type in models:
        model_path = os.path.join(models_dir, filename)
        if not os.path.exists(model_path):
            logger.warning(f"Model file {filename} not found, skipping.")
            continue
        
        clf = joblib.load(model_path)
        y_pred = clf.predict(X_data)
        y_prob = clf.predict_proba(X_data)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)

        cm = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = cm.ravel()
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

        records.append({
            "Model": name,
            "Preprocessing": prep_type,
            "Accuracy": acc,
            "Precision": prec,
            "Recall (Ransomware)": rec,
            "F1-Score": f1,
            "ROC-AUC": auc,
            "False Positive Rate (FPR)": fpr,
            "False Negative Rate (FNR)": fnr,
            "True Positives (TP)": int(tp),
            "False Positives (FP)": int(fp),
            "True Negatives (TN)": int(tn),
            "False Negatives (FN)": int(fn)
        })

    df = pd.DataFrame(records)
    csv_path = os.path.join(reports_dir, "model_comparison.csv")
    df.to_csv(csv_path, index=False)
    logger.info(f"Saved evaluation comparison to {csv_path}")
    return df


if __name__ == "__main__":
    proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    proc_path = os.path.join(proj_root, "data", "processed")
    mod_path = os.path.join(proj_root, "models")
    rep_path = os.path.join(proj_root, "reports")
    df_res = evaluate_models(proc_path, mod_path, rep_path)
    print(df_res.to_string(index=False))
