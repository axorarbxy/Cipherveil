import sys
import os
import json
from pathlib import Path
import pandas as pd
import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
BASE = Path(__file__).resolve().parent
load_dotenv(BASE / ".env")
from src.predict import predict_ransomware
from src.server_log_detector import ServerLogDetector

BACKEND_URL = os.getenv("CIPHERVEIL_BACKEND_URL", "http://127.0.0.1:8000")
ML_API_KEY = os.getenv("CIPHERVEIL_ML_DEVICE_API_KEY", "").strip()
HEADERS = {"X-Device-Key": ML_API_KEY} if ML_API_KEY else {}

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "processed")
server_log_detector = ServerLogDetector()

app = FastAPI(title="ML Behavioral Analysis Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def shap_dict_from_result(result):
    """Convert predict.py's top_contributing_features list into the flat
    {feature_name: shap_impact} dict shape the backend's Alert model expects."""
    return {f["feature_name"]: round(f["shap_impact"], 4) for f in result["top_contributing_features"]}


def forward_to_backend(reason, base_risk, result):
    ml_score = result["risk_score"]  # 0-100 scale from RansomwareRiskScorer
    shap_explanation = shap_dict_from_result(result)

    event_res = requests.post(
        f"{BACKEND_URL}/events",
        json={"event_type": "ml_analysis", "file_path": None, "features": None},
        headers=HEADERS, timeout=5,
    )
    event_id = event_res.json().get("id") if event_res.status_code == 201 else None

    alert_res = requests.post(
        f"{BACKEND_URL}/alerts",
        json={
            "event_id": event_id,
            "reason": reason,
            "base_risk": base_risk,
            "ml_score": ml_score,
            "shap_explanation": shap_explanation,
        },
        headers=HEADERS, timeout=5,
    )
    return alert_res.json()


@app.get("/health")
def health():
    return {"status": "ok", "server_log_detector": server_log_detector.status()["state"]}


@app.get("/status")
def status():
    """Operational counters for the server-side file-log detector dashboard."""
    return server_log_detector.status()


@app.post("/simulate/ransomware")
def simulate_ransomware():
    """Scores a REAL held-out ransomware-labeled sample from the test set."""
    X_test = pd.read_csv(os.path.join(DATA_DIR, "X_test.csv"))
    y_test = pd.read_csv(os.path.join(DATA_DIR, "y_test.csv"))
    label_col = y_test.columns[0]
    ransomware_rows = y_test[y_test[label_col] == 1].index
    sample = X_test.iloc[ransomware_rows[0]].to_dict()

    result = predict_ransomware(sample)
    alert = forward_to_backend(
        reason="ML Behavioral Analysis - Ransomware-like process/registry pattern",
        base_risk=60,  # represents a moderate behavioral signal that ML then confirms/escalates
        result=result,
    )
    return {"ml_result": result, "backend_alert": alert}


@app.post("/simulate/benign")
def simulate_benign():
    """Scores a REAL held-out benign-labeled sample from the test set."""
    X_test = pd.read_csv(os.path.join(DATA_DIR, "X_test.csv"))
    y_test = pd.read_csv(os.path.join(DATA_DIR, "y_test.csv"))
    label_col = y_test.columns[0]
    benign_rows = y_test[y_test[label_col] == 0].index
    sample = X_test.iloc[benign_rows[0]].to_dict()

    result = predict_ransomware(sample)
    alert = forward_to_backend(
        reason="ML Behavioral Analysis - routine activity pattern",
        base_risk=0,
        result=result,
    )
    return {"ml_result": result, "backend_alert": alert}


@app.post("/score")
def score_features(payload: dict):
    """Score one-second server file-log features with a benign-window baseline.

    The general ransomware classifier is trained on a separate behavioral feature
    set, so live file-operation windows use their own unsupervised Isolation Forest.
    """
    features = payload.get("features") if isinstance(payload.get("features"), dict) else payload
    event_id = payload.get("event_id") if isinstance(payload, dict) else None
    result = server_log_detector.score(features)

    alert = None
    if result["state"] == "ready" and result["is_anomaly"] and server_log_detector.reserve_alert():
        deviations = ", ".join(
            f"{item['feature']} (+/-{item['z_score']}σ)"
            for item in result["top_deviations"]
        ) or "unusual file-operation window"
        reason = (
            "Server-side file-log anomaly detected by Isolation Forest "
            f"(score {result['risk_score']}/100; source event {event_id or 'unlinked'}; "
            f"drivers: {deviations})"
        )
        try:
            analysis_event = requests.post(
                f"{BACKEND_URL}/events",
                json={
                    "event_type": "server_log_anomaly_analysis",
                    "features": {
                        **features,
                        "source_event_id": event_id,
                        "detector": result["detector"],
                        "anomaly_score": result["risk_score"],
                        "inference_ms": result["inference_ms"],
                    },
                },
                headers=HEADERS,
                timeout=5,
            )
            if analysis_event.status_code != 201:
                alert = {"error": f"Backend rejected analysis event ({analysis_event.status_code})"}
            else:
                alert_res = requests.post(
                    f"{BACKEND_URL}/alerts",
                    json={
                        "event_id": analysis_event.json().get("id"),
                        "reason": reason,
                        "base_risk": 45,
                        "ml_score": result["risk_score"],
                        "shap_explanation": None,
                    },
                    headers=HEADERS,
                    timeout=5,
                )
                if alert_res.status_code == 201:
                    alert = alert_res.json()
                else:
                    alert = {"error": f"Backend rejected alert ({alert_res.status_code})"}
        except requests.RequestException as exc:
            alert = {"error": f"Backend unavailable: {exc}"}

    return {
        "ml_result": result,
        "server_log_result": result,
        "backend_alert": alert,
        "forwarded": alert is not None and "error" not in alert,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8020)
