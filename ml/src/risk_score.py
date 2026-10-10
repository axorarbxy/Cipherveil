"""
Risk Scoring Engine for Ransomware Early-Warning System.
Maps calibrated prediction probabilities into structured 0-100 institutional risk scores
with configurable threat level tiers and operational descriptions.
"""

import logging
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)


class RansomwareRiskScorer:
    """
    Computes calibrated institutional risk scores and security posture threat levels.
    
    Default Risk Tiers:
    - 0  to 30 : NORMAL     (Baseline benign system activity, no intervention needed)
    - 31 to 60 : WATCH      (Elevated anomalous activity, log telemetry, increase sampling)
    - 61 to 80 : SUSPICIOUS (High likelihood of malicious encryption, alert security team)
    - 81 to 100: CRITICAL   (Active ransomware behavior, initiate containment protocols)
    """
    
    def __init__(
        self,
        thresholds: Optional[Dict[str, Tuple[int, int]]] = None
    ):
        self.thresholds = thresholds or {
            "NORMAL": (0, 30),
            "WATCH": (31, 60),
            "SUSPICIOUS": (61, 80),
            "CRITICAL": (81, 100)
        }

    def compute_risk(self, probability: float) -> Dict[str, Any]:
        """
        Convert a continuous ransomware probability [0.0, 1.0] into a structured risk evaluation.
        """
        clamped_prob = max(0.0, min(1.0, float(probability)))
        raw_score = clamped_prob * 100.0
        risk_score = int(round(raw_score))

        # Determine tier
        assigned_level = "NORMAL"
        for level, (low, high) in self.thresholds.items():
            if low <= risk_score <= high:
                assigned_level = level
                break

        return {
            "probability": round(clamped_prob, 4),
            "risk_score": risk_score,
            "risk_level": assigned_level,
            "is_threat": risk_score >= 40
        }
