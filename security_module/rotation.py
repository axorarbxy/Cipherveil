import json
import os
import random
import string
from logger import log_event

def random_suffix(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def rotate_canaries_live(canary_handler, rotation_lock, config_file="config.json", reporter=None):
    rotation_lock.set()

    with open(config_file) as f:
        config = json.load(f)

    old_paths = config["canary_files"]
    new_paths = []

    for old_path in old_paths:
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

    config["canary_files"] = new_paths
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    canary_handler.canary_paths = [str(p).replace("\\", "/") for p in new_paths]

    log_event(
        reason="Canary rotation performed (auto)",
        severity="INFO",
        risk_score=0,
        extra={"old_paths": old_paths, "new_paths": new_paths, "config_file": config_file}
    )

    if reporter:
        reporter.send_event(event_type="canary_rotation")
    
    print("[ROTATION] Live rotation complete.")

    import time
    time.sleep(1)
    rotation_lock.clear()