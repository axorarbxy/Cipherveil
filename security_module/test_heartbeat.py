import time
from heartbeat import HeartbeatMonitor

monitor = HeartbeatMonitor(timeout_seconds=5)
monitor.start()

print("Sending heartbeats normally for 8 seconds...")
for _ in range(8):
    monitor.beat()
    time.sleep(1)

print("Now going silent — no more heartbeats sent. Watch for the timeout alert...")
time.sleep(10)