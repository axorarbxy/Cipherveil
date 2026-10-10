import json
import os
import platform
import queue
import threading
import time
from collections import Counter, deque
from datetime import datetime, timezone
from pathlib import Path

import psutil
import requests
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

BASE = Path(__file__).resolve().parent
with open(BASE / "config.json", "r", encoding="utf-8") as f:
    CFG = json.load(f)

WATCH_PATHS = [str((BASE / p).resolve()) if not os.path.isabs(p) else p
               for p in CFG["watch_paths"]]
WINDOW = float(CFG.get("window_seconds", 1))
API_URL = CFG.get("api_url", "").strip()
DEVICE_ID = CFG.get("device_id", platform.node() or "UNKNOWN")
MAX_QUEUE = int(CFG.get("max_event_queue", 10000))

event_q = queue.Queue(maxsize=MAX_QUEUE)
recent_processes = deque(maxlen=500)
lock = threading.Lock()


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def extension(path):
    suffix = Path(path).suffix.lower()
    return suffix[1:] if suffix else "[none]"


class Handler(FileSystemEventHandler):
    def _put(self, operation, src, dest=None):
        event = {
            "timestamp": now_iso(),
            "operation": operation,
            "path": src,
            "dest_path": dest,
            "extension": extension(src),
        }
        try:
            event_q.put_nowait(event)
        except queue.Full:
            pass

    def on_created(self, event):
        if not event.is_directory:
            self._put("create", event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._put("modify", event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self._put("delete", event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._put("rename", event.src_path, event.dest_path)


def process_snapshot():
    rows = []
    for p in psutil.process_iter(["pid", "name", "username", "cpu_percent"]):
        try:
            info = p.info
            rows.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return rows


def telemetry_loop():
    out = BASE / "telemetry.jsonl"
    while True:
        started = time.monotonic()
        counts = Counter()
        ext = Counter()
        touched = set()

        while time.monotonic() - started < WINDOW:
            timeout = max(0.01, WINDOW - (time.monotonic() - started))
            try:
                e = event_q.get(timeout=timeout)
                counts[e["operation"]] += 1
                ext[e["extension"]] += 1
                touched.add(e["path"])
            except queue.Empty:
                break

        procs = process_snapshot()
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent

        top_process = None
        if procs:
            # This is a system-level snapshot, not attribution of file events to a process.
            top_process = max(
                procs,
                key=lambda x: (x.get("cpu_percent") or 0)
            ).get("name")

        record = {
            "timestamp": now_iso(),
            "device_id": DEVICE_ID,
            "platform": platform.platform(),
            "window_seconds": WINDOW,
            "file_created": counts["create"],
            "file_modified": counts["modify"],
            "file_deleted": counts["delete"],
            "file_renamed": counts["rename"],
            "operations_per_sec": round(sum(counts.values()) / WINDOW, 2),
            "unique_files": len(touched),
            "unique_extensions": len(ext),
            "extension_counts": dict(ext),
            "process_count": len(procs),
            "top_cpu_process": top_process,
            "cpu_percent": cpu,
            "memory_percent": mem,
        }

        with open(out, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

        if API_URL:
            try:
                r = requests.post(
                    API_URL.rstrip("/") + "/telemetry",
                    json=record,
                    timeout=2
                )
                r.raise_for_status()
            except requests.RequestException as exc:
                print(f"[API offline] {exc}")

        print(
            f"[{record['timestamp']}] "
            f"ops/s={record['operations_per_sec']:<7} "
            f"create={record['file_created']:<3} "
            f"modify={record['file_modified']:<3} "
            f"rename={record['file_renamed']:<3} "
            f"delete={record['file_deleted']:<3} "
            f"cpu={record['cpu_percent']:.1f}%"
        )


def main():
    for path in WATCH_PATHS:
        Path(path).mkdir(parents=True, exist_ok=True)

    observer = Observer()
    handler = Handler()
    for path in WATCH_PATHS:
        observer.schedule(handler, path, recursive=True)
        print(f"Monitoring: {path}")

    observer.start()
    t = threading.Thread(target=telemetry_loop, daemon=True)
    t.start()

    print(f"Device: {DEVICE_ID}")
    print("Monitoring started. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()
