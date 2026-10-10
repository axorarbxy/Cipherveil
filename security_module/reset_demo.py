import os
import json
from response import reset

def reset_canary_files():
    with open("config.json") as f:
        config = json.load(f)
    for path in config["canary_files"]:
        with open(path, "w") as f:
            f.write("")  # clear back to empty/clean state
    print("Canary files reset.")

if __name__ == "__main__":
    reset()
    reset_canary_files()