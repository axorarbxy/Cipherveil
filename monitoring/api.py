from datetime import datetime, timezone
from pathlib import Path
import json

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="RansomGuard Monitoring API", version="0.1")

BASE = Path(__file__).resolve().parent
STORE = BASE / "server_telemetry.jsonl"


class Telemetry(BaseModel):
    timestamp: str
    device_id: str
    window_seconds: float = Field(gt=0)
    file_created: int = 0
    file_modified: int = 0
    file_deleted: int = 0
    file_renamed: int = 0
    operations_per_sec: float = 0
    unique_files: int = 0
    unique_extensions: int = 0
    process_count: int = 0
    top_cpu_process: str | None = None
    cpu_percent: float = 0
    memory_percent: float = 0


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/telemetry")
def telemetry(data: Telemetry):
    row = data.model_dump()
    row["received_at"] = datetime.now(timezone.utc).isoformat()
    with open(STORE, "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    return {"accepted": True, "device_id": data.device_id}


@app.get("/telemetry/latest")
def latest():
    if not STORE.exists():
        return []
    lines = STORE.read_text(encoding="utf-8").splitlines()
    return [json.loads(x) for x in lines[-20:]]
