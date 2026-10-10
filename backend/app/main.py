from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import auth, devices, events, alerts, incidents, dashboard

# Create tables on startup (fine for SQLite demo / MySQL prototype; use Alembic
# migrations instead for a long-lived production deployment).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Backend for the Ransomware Early-Warning System — connects the ML engine "
        "(RanSAP/RanSMAP + SHAP), the monitoring agent, and the rule/canary engine "
        "to persistent storage and the admin dashboard. Member 5 scope: FastAPI, "
        "MySQL, JWT auth, device/event/alert/incident management."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(devices.router)
app.include_router(events.router)
app.include_router(alerts.router)
app.include_router(incidents.router)
app.include_router(dashboard.router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": settings.APP_NAME}
