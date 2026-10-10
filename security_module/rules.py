import time
from collections import deque
from logger import log_event
from response import isolate

class MassChangeDetector:
    def __init__(self, threshold=10, window_seconds=10, reporter=None):
        self.threshold = threshold
        self.window_seconds = window_seconds
        self.event_times = deque()
        self.reporter = reporter

    def record_event(self, filepath):
        now = time.time()
        self.event_times.append(now)
        self._trim_old(now)

        if len(self.event_times) >= self.threshold:
            self.trigger_mass_change_alert(len(self.event_times))
            self.event_times.clear()

    def _trim_old(self, now):
        while self.event_times and now - self.event_times[0] > self.window_seconds:
            self.event_times.popleft()

    def trigger_mass_change_alert(self, count):
        event = log_event(
            reason="Mass file-change pattern detected",
            severity="HIGH",
            risk_score=92,
            extra={"event_count": count, "window_seconds": self.window_seconds}
        )
        print(f"[HIGH] Mass file-change pattern detected! {count} changes in {self.window_seconds}s")
        print(f"  Risk Score: 92")
        print(f"  Logged: {event['timestamp']}")
        isolate("Mass file-change pattern detected", 92)

        if self.reporter:
            event_result = self.reporter.send_event(event_type="file_modified")
            event_id = event_result["id"] if event_result else None
            self.reporter.send_alert(
                reason="Mass file-change pattern detected",
                base_risk=92,
                event_id=event_id
            )