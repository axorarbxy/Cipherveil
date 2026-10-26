"""Unsupervised anomaly scoring for one-second server-side file activity windows."""

import json
import os
import threading
import time
from pathlib import Path

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


FEATURES = (
    "file_created",
    "file_modified",
    "file_deleted",
    "file_renamed",
    "operations_per_sec",
    "unique_files",
    "unique_extensions",
    "process_count",
    "cpu_percent",
    "memory_percent",
)
MIN_BASELINE_WINDOWS = 32
MAX_BASELINE_WINDOWS = 2000
ALERT_RISK_THRESHOLD = 99.9


def _feature_vector(values):
    vector = []
    for name in FEATURES:
        try:
            value = float(values.get(name, 0) or 0)
        except (TypeError, ValueError):
            value = 0.0
        vector.append(value if np.isfinite(value) else 0.0)
    return np.asarray(vector, dtype=np.float64)


class ServerLogDetector:
    """Fit an Isolation Forest to historical benign windows and score live windows."""

    def __init__(self, history_file=None):
        default_history = Path(__file__).resolve().parents[2] / "monitoring" / "telemetry.jsonl"
        self.history_file = Path(history_file or os.getenv("SERVER_LOG_HISTORY_FILE", default_history))
        self.model = None
        self.baseline_scores = np.asarray([], dtype=np.float64)
        self.baseline_mean = np.zeros(len(FEATURES), dtype=np.float64)
        self.baseline_std = np.ones(len(FEATURES), dtype=np.float64)
        self.processed_windows = 0
        self.anomaly_windows = 0
        self.total_inference_ms = 0.0
        self.inference_windows = 0
        self.last_result = None
        self._last_alert_at = 0.0
        self._warmup_rows = []
        self._lock = threading.Lock()
        self._fit_from_history()

    def _fit_from_history(self):
        if not self.history_file.exists():
            return

        rows = []
        try:
            with self.history_file.open("r", encoding="utf-8") as stream:
                for line in stream:
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if isinstance(row, dict):
                        rows.append(_feature_vector(row))
        except OSError:
            return

        if len(rows) < MIN_BASELINE_WINDOWS:
            return

        self._fit(np.asarray(rows[-MAX_BASELINE_WINDOWS:], dtype=np.float64))

    def _fit(self, baseline):
        self.baseline_mean = baseline.mean(axis=0)
        self.baseline_std = np.maximum(baseline.std(axis=0), 1e-6)
        self.model = make_pipeline(
            StandardScaler(),
            IsolationForest(
                n_estimators=120,
                contamination="auto",
                random_state=42,
                n_jobs=1,
            ),
        )
        self.model.fit(baseline)
        self.baseline_scores = np.sort(self.model.decision_function(baseline))

    def score(self, features):
        started = time.perf_counter()
        vector = _feature_vector(features)

        with self._lock:
            self.processed_windows += 1
            if self.model is None:
                # Only use low-churn windows for first-run calibration. This gives a
                # fresh deployment a path to readiness without learning a burst.
                low_churn = (
                    vector[4] <= 5
                    and vector[3] <= 2
                    and vector[2] <= 2
                    and vector[0] <= 10
                )
                if low_churn:
                    self._warmup_rows.append(vector)
                    self._warmup_rows = self._warmup_rows[-MAX_BASELINE_WINDOWS:]
                    if len(self._warmup_rows) >= MIN_BASELINE_WINDOWS:
                        self._fit(np.asarray(self._warmup_rows, dtype=np.float64))

                result = {
                    "detector": "IsolationForest",
                    "state": "ready" if self.model else "warming_up",
                    "is_anomaly": False,
                    "risk_score": 0,
                    "risk_level": "CALIBRATING" if not self.model else "NORMAL",
                    "baseline_windows": len(self._warmup_rows),
                    "inference_ms": round((time.perf_counter() - started) * 1000, 3),
                    "top_deviations": [],
                }
            else:
                model_score = float(self.model.decision_function(vector.reshape(1, -1))[0])
                percentile = np.searchsorted(self.baseline_scores, model_score, side="right")
                risk_score = float(round(float(100 * (1 - percentile / max(1, len(self.baseline_scores)))), 2))
                is_anomaly = bool(risk_score >= ALERT_RISK_THRESHOLD)
                elapsed_ms = (time.perf_counter() - started) * 1000
                self.total_inference_ms += elapsed_ms
                self.inference_windows += 1
                if is_anomaly:
                    self.anomaly_windows += 1

                z_scores = np.abs((vector - self.baseline_mean) / self.baseline_std)
                top_indices = np.argsort(z_scores)[::-1][:3]
                top_deviations = [
                    {
                        "feature": FEATURES[index],
                        "z_score": round(float(z_scores[index]), 2),
                        "observed": round(float(vector[index]), 2),
                    }
                    for index in top_indices
                    if z_scores[index] > 0
                ]
                risk_level = "ANOMALY" if is_anomaly else "NORMAL"
                result = {
                    "detector": "IsolationForest",
                    "state": "ready",
                    "is_anomaly": is_anomaly,
                    "risk_score": risk_score,
                    "risk_level": risk_level,
                    "baseline_windows": int(len(self.baseline_scores)),
                    "inference_ms": round(elapsed_ms, 3),
                    "top_deviations": top_deviations,
                }

            self.last_result = result
            return dict(result)

    def reserve_alert(self, cooldown_seconds=60):
        """Limit repeated alerts from consecutive anomalous windows."""
        with self._lock:
            now = time.monotonic()
            if now - self._last_alert_at < cooldown_seconds:
                return False
            self._last_alert_at = now
            return True

    def status(self):
        with self._lock:
            average_ms = self.total_inference_ms / max(1, self.inference_windows)
            return {
                "detector": "IsolationForest",
                "state": "ready" if self.model else "warming_up",
                "baseline_source": str(self.history_file.name),
                "baseline_windows": int(len(self.baseline_scores)),
                "processed_windows": self.processed_windows,
                "inference_windows": self.inference_windows,
                "anomaly_windows": self.anomaly_windows,
                "average_inference_ms": round(average_ms, 3),
                "last_result": dict(self.last_result) if self.last_result else None,
            }
