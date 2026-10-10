"""
SHAP Explainability Module for Tree-based Ransomware Detectors.
Computes TreeSHAP feature attributions and produces local prediction breakdowns
with mapped system indicators and behavioral directions.
"""

import os
import json
import logging
from typing import Dict, List, Any, Union, Optional
import numpy as np
import pandas as pd
import shap

logger = logging.getLogger(__name__)


class RansomwareExplainer:
    """
    SHAP explainability engine for ransomware detection.
    Translates mathematical model decisions into actionable cybersecurity intelligence.
    """

    def __init__(
        self,
        model: Any,
        feature_names: List[str],
        readable_mapping: Optional[Dict[str, str]] = None
    ):
        self.model = model
        self.feature_names = feature_names
        self.readable_mapping = readable_mapping or {}
        self.readable_feature_names = [self.readable_mapping.get(c, c) for c in self.feature_names]
        self.explainer = shap.TreeExplainer(self.model)

    def explain_instance(
        self,
        X_sample: np.ndarray,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Compute top contributing SHAP behavioral features for a single sample.
        """
        if X_sample.ndim == 1:
            X_sample = X_sample.reshape(1, -1)

        shap_vals = self.explainer(X_sample)
        sample_shap = shap_vals.values[0]

        # Rank features by absolute SHAP impact
        ranked_indices = np.argsort(np.abs(sample_shap))[::-1][:top_k]

        top_features = []
        for idx in ranked_indices:
            feat_id = self.feature_names[idx]
            readable = self.readable_feature_names[idx]
            impact = float(sample_shap[idx])
            feature_val = float(X_sample[0, idx])
            direction = "+RANSOMWARE" if impact > 0 else "-BENIGN"

            top_features.append({
                "feature_id": feat_id,
                "feature_name": readable,
                "value": feature_val,
                "shap_impact": round(impact, 4),
                "direction": direction,
                "description": f"{readable} (Impact: {impact:+.3f})"
            })

        return top_features
