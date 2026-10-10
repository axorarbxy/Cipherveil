import json
import os
from datetime import datetime

LOG_FILE = "logs/events.jsonl"

def log_event(reason, severity, risk_score, extra=None):
    os.makedirs("logs", exist_ok=True)
    event = {
        "timestamp": datetime.now().isoformat(),
        "reason": reason,
        "severity": severity,
        "risk_score": risk_score
    }
    if extra:
        event.update(extra)

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")

    return event