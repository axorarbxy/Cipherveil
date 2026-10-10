import json
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from logger import log_event
def load_config():
    with open("config.json") as f:
        return json.load(f)

class CanaryHandler(FileSystemEventHandler):
    def __init__(self, canary_paths):
        # Normalize paths for reliable comparison
        self.canary_paths = [str(p).replace("\\", "/") for p in canary_paths]

    def on_modified(self, event):
        self._check_event(event)

    def on_moved(self, event):
        self._check_event(event)

    def on_deleted(self, event):
        self._check_event(event)

    def _check_event(self, event):
        event_path = event.src_path.replace("\\", "/")
        for canary in self.canary_paths:
            if canary in event_path:
                self.trigger_alert(canary, event.event_type)

    def trigger_alert(self, canary_path, event_type):
        event = log_event(
            reason="CANARY FILE MODIFIED",
            severity="CRITICAL",
            risk_score=100,
            extra={"file": canary_path, "event_type": event_type}
        )
        print(f"[CRITICAL] Canary file event detected!")
        print(f"  File: {canary_path}")
        print(f"  Event type: {event_type}")
        print(f"  Risk Score: 100")
        print(f"  Logged: {event['timestamp']}")

def main():
    config = load_config()
    watch_path = config["shared_drive_path"]
    canary_paths = config["canary_files"]

    event_handler = CanaryHandler(canary_paths)
    observer = Observer()
    observer.schedule(event_handler, watch_path, recursive=False)
    observer.start()

    print(f"Watching folder: {watch_path}")
    print(f"Canary file(s): {canary_paths}")
    print("Waiting for events... (Ctrl+C to stop)")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()