"""
Prediction and Real-Time Inference Module.
Loads the primary trained model, preprocessor, and explainer to deliver
actionable ransomware predictions with calibrated risk scoring and SHAP explainability.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Union, Optional
import numpy as np
import pandas as pd
import joblib

# Ensure package importability
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.preprocessing import MLRanPreprocessor
from src.risk_score import RansomwareRiskScorer
from src.explain import RansomwareExplainer

logger = logging.getLogger(__name__)


class RansomwarePredictor:
    """
    Production-grade ransomware detector.
    Integrates preprocessor, XGBoost classifier, risk scorer, and SHAP explainer.
    """

    def __init__(
        self,
        models_dir: Optional[str] = None
    ):
        if models_dir is None:
            models_dir = os.path.join(parent_dir, "models")

        self.models_dir = models_dir
        self.model_path = os.path.join(models_dir, "ransomware_model.joblib")
        self.prep_path = os.path.join(models_dir, "preprocessor_tree.joblib")
        self.config_path = os.path.join(models_dir, "model_config.json")
        self.meta_path = os.path.join(models_dir, "feature_metadata.json")

        self._load_components()

    def _load_components(self) -> None:
        logger.info("Loading ransomware model and preprocessor...")
        self.model = joblib.load(self.model_path)
        self.preprocessor = MLRanPreprocessor.load(self.prep_path)

        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        with open(self.meta_path, "r", encoding="utf-8") as f:
            self.meta = json.load(f)

        self.threshold = self.config.get("decision_threshold", 0.40)
        self.risk_scorer = RansomwareRiskScorer()
        
        # Build mapping dictionary
        readable_map = dict(zip(self.meta["feature_column_ids"], self.meta["feature_readable_names"]))
        self.explainer = RansomwareExplainer(
            model=self.model,
            feature_names=self.meta["feature_column_ids"],
            readable_mapping=readable_map
        )
        logger.info("Predictor initialized successfully.")

    def predict(
        self,
        features: Union[Dict[str, Any], pd.DataFrame, np.ndarray],
        top_k_features: int = 5
    ) -> Dict[str, Any]:
        """
        Predict ransomware status for incoming telemetry vector.
        
        Args:
            features: Dictionary of feature_id -> value, single-row DataFrame, or 1D array.
            top_k_features: Number of top contributing SHAP features to return.
            
        Returns:
            Dictionary with prediction, probability, risk_score, risk_level, and SHAP top features.
        """
        X_trans = self.preprocessor.transform(features)
        prob = float(self.model.predict_proba(X_trans)[0, 1])
        
        is_ransomware = prob >= self.threshold
        prediction_label = "RANSOMWARE" if is_ransomware else "NORMAL"
        
        risk_info = self.risk_scorer.compute_risk(prob)
        top_explanations = self.explainer.explain_instance(X_trans, top_k=top_k_features)

        return {
            "prediction": prediction_label,
            "is_ransomware": is_ransomware,
            "probability": risk_info["probability"],
            "risk_score": risk_info["risk_score"],
            "risk_level": risk_info["risk_level"],
            "decision_threshold": self.threshold,
            "top_contributing_features": top_explanations
        }


# Convenience standalone function
_DEFAULT_PREDICTOR: Optional[RansomwarePredictor] = None


def predict_ransomware(
    features: Union[Dict[str, Any], pd.DataFrame, np.ndarray],
    models_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Predict ransomware behavior for an input feature vector.
    """
    global _DEFAULT_PREDICTOR
    if _DEFAULT_PREDICTOR is None or models_dir is not None:
        _DEFAULT_PREDICTOR = RansomwarePredictor(models_dir=models_dir)
    return _DEFAULT_PREDICTOR.predict(features)


if __name__ == "__main__":
    predictor = RansomwarePredictor()
    proc_dir = os.path.join(parent_dir, "data", "processed")
    X_test_df = pd.read_csv(os.path.join(proc_dir, "X_test.csv"))
    
    # Test on a single sample
    sample = X_test_df.iloc[0].to_dict()
    res = predictor.predict(sample)
    print("Test Sample Prediction Output:")
    print(json.dumps(res, indent=2))
