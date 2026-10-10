import time
import threading
from logger import log_event
from response import isolate

class HeartbeatMonitor:
    def __init__(self, timeout_seconds=5, reporter=None):
        self.timeout_seconds = timeout_seconds
        self.last_beat = time.time()
        self.alive = True
        self._stop_flag = False
        self.reporter = reporter

    def beat(self):
        """Call this periodically to signal 'monitoring is alive'."""
        self.last_beat = time.time()
        if not self.alive:
            self.alive = True
            print("[INFO] Heartbeat restored.")

    def _watch_loop(self):
        while not self._stop_flag:
            elapsed = time.time() - self.last_beat
            if elapsed > self.timeout_seconds and self.alive:
                self.alive = False
                self.trigger_heartbeat_loss(elapsed)
            time.sleep(1)

    def trigger_heartbeat_loss(self, elapsed):
        event = log_event(
            reason="DEAD-MAN'S-SWITCH: heartbeat timeout",
            severity="CRITICAL",
            risk_score=98,
            extra={"elapsed_seconds": round(elapsed, 2)}
        )
        print(f"[CRITICAL] Heartbeat lost! No signal for {elapsed:.1f}s")
        print(f"  Risk Score: 98")
        print(f"  Logged: {event['timestamp']}")
        isolate("DEAD-MAN'S-SWITCH: heartbeat timeout", 98)

        if self.reporter:
            event_result = self.reporter.send_event(event_type="heartbeat")
            event_id = event_result["id"] if event_result else None
            self.reporter.send_alert(
                reason="DEAD-MAN'S-SWITCH: heartbeat timeout",
                base_risk=98,
                event_id=event_id
            )

    def start(self):
        thread = threading.Thread(target=self._watch_loop, daemon=True)
        thread.start()

    def stop(self):
        self._stop_flag = True