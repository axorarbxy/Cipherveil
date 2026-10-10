"""
Model Training Module.
Trains Random Forest, XGBoost, Logistic Regression, and SVM on preprocessed MLRan training data.
"""

import os
import sys

# Ensure project root is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import logging
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

from src.preprocessing import MLRanPreprocessor

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def train_all_models(
    processed_dir: str,
    models_dir: str
) -> None:
    os.makedirs(models_dir, exist_ok=True)
    
    # Load training data
    logger.info("Loading processed training datasets...")
    X_train_df = pd.read_csv(os.path.join(processed_dir, "X_train.csv"))
    y_train = pd.read_csv(os.path.join(processed_dir, "y_train.csv"))["target"].values

    # Load preprocessors
    prep_tree = MLRanPreprocessor.load(os.path.join(models_dir, "preprocessor_tree.joblib"))
    prep_scaled = MLRanPreprocessor.load(os.path.join(models_dir, "preprocessor_scaled.joblib"))

    X_train_tree = prep_tree.transform(X_train_df)
    X_train_scaled = prep_scaled.transform(X_train_df)

    # 1. Random Forest
    logger.info("Training Random Forest...")
    rf = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1, class_weight="balanced")
    rf.fit(X_train_tree, y_train)
    joblib.dump(rf, os.path.join(models_dir, "random_forest.joblib"))
    logger.info("Saved models/random_forest.joblib")

    # 2. XGBoost
    logger.info("Training XGBoost...")
    xgb = XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, eval_metric="logloss", n_jobs=-1)
    xgb.fit(X_train_tree, y_train)
    joblib.dump(xgb, os.path.join(models_dir, "xgboost.joblib"))
    joblib.dump(xgb, os.path.join(models_dir, "ransomware_model.joblib"))
    logger.info("Saved models/xgboost.joblib and models/ransomware_model.joblib")

    # 3. Logistic Regression
    logger.info("Training Logistic Regression (StandardScaler)...")
    lr = LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced")
    lr.fit(X_train_scaled, y_train)
    joblib.dump(lr, os.path.join(models_dir, "logistic_regression.joblib"))
    logger.info("Saved models/logistic_regression.joblib")

    # 4. SVM
    logger.info("Training SVM RBF Kernel (StandardScaler)...")
    svm = SVC(kernel="rbf", probability=True, random_state=42, class_weight="balanced")
    svm.fit(X_train_scaled, y_train)
    joblib.dump(svm, os.path.join(models_dir, "svm.joblib"))
    logger.info("Saved models/svm.joblib")

    logger.info("All 4 models successfully trained and serialized.")


if __name__ == "__main__":
    proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    proc_path = os.path.join(proj_root, "data", "processed")
    mod_path = os.path.join(proj_root, "models")
    train_all_models(proc_path, mod_path)
