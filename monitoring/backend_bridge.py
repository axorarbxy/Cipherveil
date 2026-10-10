import json
import time
import requests
from pathlib import Path

BASE = Path(__file__).resolve().parent
TELEMETRY_FILE = BASE / "telemetry.jsonl"
BACKEND_URL = "http://127.0.0.1:8000"
API_KEY = "c67a92cdc5ed435b81fad7e635b481c4"
HEADERS = {"X-Device-Key": API_KEY}
ML_SERVICE_URL = "http://127.0.0.1:8020"


def tail_and_forward():
    print(f"Bridging {TELEMETRY_FILE} -> {BACKEND_URL}/events")
    print(f"Also scoring each window via {ML_SERVICE_URL}/score")
    last_size = 0
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
                            ml_res = requests.post(f"{ML_SERVICE_URL}/score", json=features, timeout=5)
                            if ml_res.status_code == 200:
                                score = ml_res.json().get("ml_result", {}).get("risk_score")
                                print(f"[BRIDGE] ML score: {score}/100")
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