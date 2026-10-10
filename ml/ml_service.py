import sys
import os
import json
import pandas as pd
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.predict import predict_ransomware

BACKEND_URL = "http://127.0.0.1:8000"
ML_API_KEY = "920889dfd7a5444185de5e9f1cd223f3"
HEADERS = {"X-Device-Key": ML_API_KEY}

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "processed")

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
    return {"status": "ok"}


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
def score_features(features: dict):
    """Scores an arbitrary feature dict (used for live Monitoring telemetry).
    Only forwards to the backend when the result is non-trivial, to avoid
    flooding the alerts table with routine near-zero scores."""
    result = predict_ransomware(features)

    if result["risk_score"] < 10:
        return {"ml_result": result, "backend_alert": None, "forwarded": False}

    alert = forward_to_backend(
        reason="ML Behavioral Analysis - live telemetry scan",
        base_risk=0,
        result=result,
    )
    return {"ml_result": result, "backend_alert": alert, "forwarded": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8020)