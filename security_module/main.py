import json
import os
import sys
import argparse
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from heartbeat import HeartbeatMonitor
from logger import log_event
from response import isolate
from rules import MassChangeDetector
from rotation import rotate_canaries_live, random_suffix
from backend_reporter import BackendReporter

rotation_lock = threading.Event()


def load_config(config_file):
    with open(config_file) as f:
        return json.load(f)


class CanaryHandler(FileSystemEventHandler):
    def __init__(self, canary_paths, mass_detector, rotation_lock, reporter=None):
        self.canary_paths = [str(p).replace("\\", "/") for p in canary_paths]
        self.mass_detector = mass_detector
        self.rotation_lock = rotation_lock
        self.reporter = reporter

    def on_modified(self, event):
        self._check_event(event)

    def on_moved(self, event):
        self._check_event(event)

    def on_deleted(self, event):
        self._check_event(event)

    def _check_event(self, event):
        if self.rotation_lock.is_set():
            return

        event_path = event.src_path.replace("\\", "/")
        self.mass_detector.record_event(event_path)

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
        print(f"[CRITICAL] Canary file event detected! File: {canary_path} | Logged: {event['timestamp']}")
        isolate("CANARY FILE MODIFIED", 100)

        if self.reporter:
            event_result = self.reporter.send_event(
                event_type="canary_trip",
                file_path=canary_path
            )
            event_id = event_result["id"] if event_result else None
            self.reporter.send_alert(
                reason="CANARY FILE MODIFIED",
                base_risk=100,
                event_id=event_id
            )


def parse_args():
    parser = argparse.ArgumentParser(description="Ransomware Early-Warning Security Module")
    parser.add_argument("config", nargs="?", default="config.json",
                         help="Path to config file (default: config.json)")
    parser.add_argument("--reset", action="store_true",
                         help="Reset state and canary files, then exit")
    parser.add_argument("--rotate", action="store_true",
                         help="Manually rotate canaries once, then exit")
    parser.add_argument("--simulate-heartbeat-loss", action="store_true",
                         help="Start the sidecar but never send heartbeats, to test the dead-man's-switch")
    return parser.parse_args()


def main():
    args = parse_args()
    config_file = args.config

    if args.reset:
        from response import reset
        reset()
        config = load_config(config_file)
        for path in config["canary_files"]:
            with open(path, "w") as f:
                f.write("")
        print("Canary files and state reset.")
        return

    if args.rotate:
        cfg = load_config(config_file)

        backend_url = cfg.get("backend_url")
        backend_api_key = cfg.get("backend_api_key")
        reporter = BackendReporter(backend_url, backend_api_key) if backend_url and backend_api_key else None

        new_paths = []
        for old_path in cfg["canary_files"]:
            if not os.path.exists(old_path):
                print(f"[WARN] Canary not found, skipping: {old_path}")
                new_paths.append(old_path)
                continue
            directory = os.path.dirname(old_path)
            ext = os.path.splitext(old_path)[1]
            new_name = f"Doc_{random_suffix()}{ext}"
            new_path = os.path.join(directory, new_name).replace("\\", "/")
            os.rename(old_path, new_path)
            new_paths.append(new_path)
            print(f"[ROTATION] {old_path} -> {new_path}")
        cfg["canary_files"] = new_paths
        with open(config_file, "w") as f:
            json.dump(cfg, f, indent=2)

        if reporter:
            reporter.send_event(event_type="canary_rotation")

        print("Manual rotation complete.")
        return

    config = load_config(config_file)

    missing = [p for p in config["canary_files"] if not os.path.exists(p)]
    if missing:
        print("[STARTUP ERROR] The following canary files do not exist:")
        for m in missing:
            print(f"  - {m}")
        print("Fix config.json or recreate these files before starting the sidecar.")
        return

    backend_url = config.get("backend_url")
    backend_api_key = config.get("backend_api_key")
    reporter = BackendReporter(backend_url, backend_api_key) if backend_url and backend_api_key else None

    watch_path = config["shared_drive_path"]
    canary_paths = config["canary_files"]
    timeout = config.get("heartbeat_timeout_seconds", 5)
    mass_threshold = config.get("mass_change_threshold", 10)
    mass_window = config.get("mass_change_window_seconds", 10)
    rotation_interval = config.get("canary_rotation_interval_seconds", 0)

    heartbeat = HeartbeatMonitor(timeout_seconds=timeout, reporter=reporter)
    heartbeat.start()

    mass_detector = MassChangeDetector(threshold=mass_threshold, window_seconds=mass_window, reporter=reporter)
    event_handler = CanaryHandler(canary_paths, mass_detector, rotation_lock, reporter)
    observer = Observer()
    observer.schedule(event_handler, watch_path, recursive=False)
    observer.start()

    def auto_rotate_loop():
        while True:
            time.sleep(rotation_interval)
            rotate_canaries_live(event_handler, rotation_lock, config_file, reporter)

    if rotation_interval > 0:
        rotation_thread = threading.Thread(target=auto_rotate_loop, daemon=True)
        rotation_thread.start()
        print(f"Auto-rotation enabled: every {rotation_interval}s")

    print(f"Sidecar running. Watching: {watch_path} | Canaries: {canary_paths} | Heartbeat timeout: {timeout}s")
    if reporter:
        print(f"Backend reporting enabled: {backend_url}")
    print("Press Ctrl+C to stop.")

    if args.simulate_heartbeat_loss:
        print("[TEST MODE] Heartbeat will NOT be sent. Waiting for dead-man's-switch to fire...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            heartbeat.stop()
        observer.join()
        return

    try:
        while True:
            heartbeat.beat()
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        heartbeat.stop()
    observer.join()


if __name__ == "__main__":
    main()