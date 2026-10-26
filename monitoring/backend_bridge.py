import json
import os
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

BASE = Path(__file__).resolve().parent
TELEMETRY_FILE = BASE / "telemetry.jsonl"
load_dotenv(BASE / ".env")
BACKEND_URL = os.getenv("CIPHERVEIL_BACKEND_URL", "http://127.0.0.1:8000")
API_KEY = os.getenv("CIPHERVEIL_DEVICE_API_KEY", "").strip()
HEADERS = {"X-Device-Key": API_KEY} if API_KEY else {}
ML_SERVICE_URL = os.getenv("CIPHERVEIL_ML_SERVICE_URL", "http://127.0.0.1:8020")


def tail_and_forward():
    print(f"Bridging {TELEMETRY_FILE} -> {BACKEND_URL}/events")
    print(f"Also scoring each window via {ML_SERVICE_URL}/score")
    # This bridge is a live forwarder: historical JSONL rows are already part of
    # the local archive and should not be replayed into the backend on startup.
    last_size = TELEMETRY_FILE.stat().st_size if TELEMETRY_FILE.exists() else 0
    while True:
        if TELEMETRY_FILE.exists():
            with open(TELEMETRY_FILE, "r", encoding="utf-8") as f:
                f.seek(last_size)
                new_lines = f.readlines()
                last_size = f.tell()

            for line in new_lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue

                features = {
                    "file_created": record.get("file_created", 0),
                    "file_modified": record.get("file_modified", 0),
                    "file_deleted": record.get("file_deleted", 0),
                    "file_renamed": record.get("file_renamed", 0),
                    "operations_per_sec": record.get("operations_per_sec", 0),
                    "unique_files": record.get("unique_files", 0),
                    "unique_extensions": record.get("unique_extensions", 0),
                    "process_count": record.get("process_count", 0),
                    "cpu_percent": record.get("cpu_percent", 0),
                    "memory_percent": record.get("memory_percent", 0),
                }

                payload = {
                    "event_type": "file_modified",
                    "file_path": None,
                    "process_name": record.get("top_cpu_process"),
                    "features": features,
                }

                try:
                    r = requests.post(f"{BACKEND_URL}/events", json=payload, headers=HEADERS, timeout=3)
                    if r.status_code == 201:
                        print(f"[BRIDGE] Forwarded telemetry window -> event {r.json()['id']}")
                        try:
                            ml_res = requests.post(
                                f"{ML_SERVICE_URL}/score",
                                json={"features": features, "event_id": r.json()["id"]},
                                timeout=8,
                            )
                            if ml_res.status_code == 200:
                                response = ml_res.json()
                                score = response.get("server_log_result", response.get("ml_result", {}))
                                print(
                                    f"[BRIDGE] Server-log ML: {score.get('risk_score', 0)}/100 "
                                    f"({score.get('risk_level', score.get('state', 'unknown'))}, "
                                    f"{score.get('inference_ms', 0)} ms)"
                                )
                                if response.get("forwarded"):
                                    print("[BRIDGE] Anomaly alert linked to telemetry event")
                            else:
                                print(f"[BRIDGE] ML service rejected: {ml_res.status_code}")
                        except requests.RequestException as e:
                            print(f"[BRIDGE] ML scoring unavailable: {e}")
                    else:
                        print(f"[BRIDGE] Backend rejected: {r.status_code} {r.text}")
                except requests.RequestException as e:
                    print(f"[BRIDGE] Failed to reach backend: {e}")

        time.sleep(2)


if __name__ == "__main__":
    tail_and_forward()
