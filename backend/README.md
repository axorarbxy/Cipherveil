# Ransomware Early-Warning System — Backend (Member 5 scope)

FastAPI + MySQL (SQLite-compatible for local demo) backend that connects the ML engine,
monitoring agent, and rule/canary engine to persistent storage and the admin dashboard.

Covers everything in Member 5's role: FastAPI REST APIs, MySQL storage, JWT
authentication, device management, event storage, alert storage, and incident
management — plus the glue that ties ML + monitoring + dashboard together.

## 1. Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # edit as needed
python run.py                    # http://localhost:8000
```

Interactive API docs: `http://localhost:8000/docs`

By default it runs on **SQLite** (`ransomware_ews.db`, zero setup — good for the judge
demo laptop). To use **MySQL** instead, run `init_mysql.sql` against your server, then
set `DATABASE_URL` in `.env` to:

```
mysql+pymysql://ews_user:ews_password@localhost:3306/ransomware_ews
```

## 2. Two auth paths

| Caller | Auth method | Header |
|---|---|---|
| Admin / dashboard user | JWT (login via `/auth/login`) | `Authorization: Bearer <token>` |
| Monitoring agent / ML engine / rule engine | Per-device API key | `X-Device-Key: <device.api_key>` |

Register a device once (as an admin) to get its `api_key`; the agent/ML process on
that machine then uses that key for every `/events` and `/alerts` POST — no user
login needed on constrained hardware (Raspberry Pi).

## 3. First run walkthrough

```bash
# 1. Create an admin account
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@institution.edu.in","password":"ChangeMe123!","role":"admin"}'

# 2. Log in to get a JWT
curl -X POST http://localhost:8000/auth/login \
  -d "username=admin&password=ChangeMe123!"
# -> {"access_token": "...", "token_type": "bearer"}

# 3. Register a device (sidecar / SMB share) as that admin
curl -X POST http://localhost:8000/devices \
  -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
  -d '{"device_name":"INST-NAS-01","ip_address":"192.168.1.104","mac_address":"b8:27:eb:aa:01:4f","location":"SMB Share: \\\\INST-NAS-01\\\\Shared Documents"}'
# -> returns device.api_key, save it for the agent / ML engine
```

## 4. Integration points for other members

**Member 3 (Monitoring Agent)** pushes raw telemetry:
```
POST /events                 (X-Device-Key: <device api_key>)
{
  "event_type": "file_modified",
  "file_path": "\\INST-NAS-01\\Shared Documents\\report.xlsx",
  "process_name": "svchost.exe",
  "features": {"entropy_delta": 0.42, "mod_burst_rate": 14, "extension_anomaly": 1}
}
```

**Member 2 (ML Engineer) / Member 4 (Security & Response)** push the fused risk result
after running `evaluate_ml_risk()` + rule checks:
```
POST /alerts                 (X-Device-Key: <device api_key>)
{
  "event_id": "<uuid from /events response, optional>",
  "reason": "Canary trip detected + Mass entropy delta",
  "base_risk": 60,
  "ml_score": 78.5,
  "shap_explanation": {"Entropy": 0.42, "ModRate": 0.31, "Canary": 0.18, "Heartbeat": 0.02}
}
```
The backend applies the same fusion formula as the prototype's `trigger_alert()`:
`final_risk = min(100, base_risk + ml_score * 0.3)`, buckets it into
NORMAL (0–30) / SUSPICIOUS (31–75) / CRITICAL (76–100), and on CRITICAL:
- flips the device's `is_isolated` flag (simulated only — no real network commands, per
  the SIH safe-prototype boundary)
- auto-creates a draft CERT-In incident from the CERT-In 9-field mapping

**Member 6 (Frontend & Dashboard)** reads:
```
GET /dashboard/overview   -> live risk score, alert-band counts, isolation status
GET /dashboard/timeline   -> chronological alerts for the attack-timeline chart
GET /alerts               -> alert list + SHAP explanations for the explainability UI
GET /incidents            -> CERT-In incident list
GET /incidents/{id}/cert-in-export  -> formatted 9-field JSON for submission
```

## 5. Endpoint reference

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/auth/register` | none | Create a dashboard user |
| POST | `/auth/login` | none | Get a JWT |
| GET | `/auth/me` | JWT | Current user info |
| POST | `/devices` | JWT (admin) | Register endpoint, returns api_key |
| GET | `/devices` | JWT | List devices |
| GET | `/devices/{id}` | JWT | Device detail |
| DELETE | `/devices/{id}` | JWT (admin) | Remove device |
| POST | `/devices/heartbeat` | device key | Dead-man's-switch ping |
| POST | `/devices/{id}/isolate` | JWT (admin) | Manually simulate isolation |
| POST | `/devices/{id}/restore` | JWT (admin) | Clear isolation flag |
| POST | `/events` | device key | Ingest file/process telemetry |
| GET | `/events` | JWT | List/filter telemetry |
| POST | `/alerts` | device key | Ingest fused risk score + SHAP |
| GET | `/alerts` | JWT | List/filter alerts |
| PATCH | `/alerts/{id}/status` | JWT | Manually re-triage an alert |
| GET | `/incidents` | JWT | List CERT-In incidents |
| PATCH | `/incidents/{id}/status` | JWT (admin) | Update incident status |
| GET | `/incidents/{id}/cert-in-export` | JWT | 9-field CERT-In JSON export |
| GET | `/dashboard/overview` | JWT | Aggregated live stats |
| GET | `/dashboard/timeline` | JWT | Alert timeline feed |

## 6. Project structure

```
backend/
├── app/
│   ├── main.py          # FastAPI app + router wiring
│   ├── config.py         # env-driven settings
│   ├── database.py        # SQLAlchemy engine/session
│   ├── models.py          # User, Device, Event, Alert, Incident
│   ├── schemas.py          # Pydantic request/response models
│   ├── security.py          # password hashing + JWT
│   ├── deps.py               # auth dependencies (JWT + device api key)
│   └── routers/
│       ├── auth.py
│       ├── devices.py
│       ├── events.py
│       ├── alerts.py
│       ├── incidents.py
│       └── dashboard.py
├── requirements.txt
├── .env.example
├── init_mysql.sql
└── run.py
```

## 7. Notes

- Tables auto-create on startup via `Base.metadata.create_all()` — fine for the
  prototype/demo; swap in Alembic migrations for a long-lived deployment.
- All network-isolation actions are **simulated flags only**, matching the project's
  safe-prototype boundary — this backend never issues real network commands.
