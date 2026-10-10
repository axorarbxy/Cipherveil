import json
import os
from datetime import datetime
from logger import log_event

STATE_FILE = "logs/state.json"

def get_state():
    if not os.path.exists(STATE_FILE):
        return {"status": "PROTECTED", "risk": 0, "isolated": False}
    try:
        with open(STATE_FILE) as f:
            content = f.read().strip()
            if not content:
                return {"status": "PROTECTED", "risk": 0, "isolated": False}
            return json.loads(content)
    except json.JSONDecodeError:
        return {"status": "PROTECTED", "risk": 0, "isolated": False}

def save_state(state):
    os.makedirs("logs", exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def isolate(reason, risk_score):
    state = get_state()
    state["status"] = "ISOLATED"
    state["risk"] = risk_score
    state["isolated"] = True
    state["isolated_at"] = datetime.now().isoformat()
    state["reason"] = reason
    save_state(state)

    log_event(
        reason=f"AUTOMATED ISOLATION SIMULATION: {reason}",
        severity="CRITICAL",
        risk_score=risk_score,
        extra={"action": "isolate_simulated"}
    )
    print(f"[RESPONSE] Isolation simulation activated. Reason: {reason}")

def reset():
    state = {"status": "PROTECTED", "risk": 0, "isolated": False}
    save_state(state)
    print("[RESPONSE] State reset to PROTECTED.")