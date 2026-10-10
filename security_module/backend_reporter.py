import requests

class BackendReporter:
    def __init__(self, base_url, api_key):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {"X-Device-Key": api_key}

    def send_event(self, event_type, file_path=None, features=None):
        """Reports a raw event (file_modified, heartbeat, canary_trip, etc.)"""
        payload = {
            "event_type": event_type,
            "file_path": file_path,
            "features": features
        }
        try:
            r = requests.post(f"{self.base_url}/events", json=payload, headers=self.headers, timeout=3)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            print(f"[BACKEND] Failed to send event: {e}")
            return None

    def send_alert(self, reason, base_risk, event_id=None, ml_score=0.0, shap_explanation=None):
        """Reports a scored alert; backend auto-fuses risk and opens an incident if CRITICAL."""
        payload = {
            "event_id": event_id,
            "reason": reason,
            "base_risk": base_risk,
            "ml_score": ml_score,
            "shap_explanation": shap_explanation
        }
        try:
            r = requests.post(f"{self.base_url}/alerts", json=payload, headers=self.headers, timeout=3)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            print(f"[BACKEND] Failed to send alert: {e}")
            return None

    def send_heartbeat(self, status_note=None):
        payload = {"status_note": status_note}
        try:
            r = requests.post(f"{self.base_url}/devices/heartbeat", json=payload, headers=self.headers, timeout=3)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            print(f"[BACKEND] Failed to send heartbeat: {e}")
            return None