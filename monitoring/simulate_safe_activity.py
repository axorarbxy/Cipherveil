from pathlib import Path
import time

ROOT = Path(__file__).resolve().parent / "monitored_test"
ROOT.mkdir(exist_ok=True)

# Safe demo activity only. It operates only inside ./monitored_test.
for i in range(20):
    p = ROOT / f"demo_{i}.txt"
    p.write_text("normal demo data\n", encoding="utf-8")
    time.sleep(0.05)

for i in range(10):
    p = ROOT / f"demo_{i}.txt"
    p.write_text("modified demo data\n", encoding="utf-8")
    time.sleep(0.05)

print("Safe demo activity completed.")
