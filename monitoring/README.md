# RansomGuard Monitoring Starter

Defensive endpoint telemetry collector for a ransomware early-warning project.

## Components
- Watchdog: file create/modify/delete/rename events
- psutil: process count and system CPU/memory telemetry
- 1-second aggregation: converts events into ML-ready feature windows
- JSONL storage: simple local dataset format
- FastAPI: optional central telemetry receiver
- Safe simulator: generates benign test activity only inside `monitored_test/`

## Run locally

1. Create a virtual environment.
2. Install:
   `pip install -r requirements.txt`
3. Start monitoring:
   `python monitor.py`
4. In another terminal:
   `python simulate_safe_activity.py`

The collector writes `telemetry.jsonl`.

## Run the central API

Install FastAPI and Uvicorn:
`pip install fastapi uvicorn`

Start:
`uvicorn api:app --reload`

Then set `api_url` in `config.json` to:
`http://127.0.0.1:8000`

Restart `monitor.py`.

## ML integration point

Each line of `telemetry.jsonl` is one feature window. Use the numeric fields as model features:
- file_created
- file_modified
- file_deleted
- file_renamed
- operations_per_sec
- unique_files
- unique_extensions
- process_count
- cpu_percent
- memory_percent

Do not train on `device_id`, timestamps, file paths, or process names directly unless deliberately engineered.

## Safety

This starter does not execute, detect, or contain real ransomware. Use a sandbox and benign simulations for demonstrations. Add real endpoint isolation only after validating false positives and obtaining authorization.
