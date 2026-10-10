from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview", response_model=schemas.DashboardOverview)
def overview(db: Session = Depends(get_db), _user: models.User = Depends(get_current_user)):
    """
    Single aggregated endpoint the dashboard (Member 6) can poll for the live risk
    score, alert-count breakdown by band, and open-incident count — everything needed
    to drive the Chart.js risk-tier widgets and the top-line status banner.
    """
    total_devices = db.query(func.count(models.Device.id)).scalar() or 0
    isolated_devices = db.query(func.count(models.Device.id)).filter(models.Device.is_isolated.is_(True)).scalar() or 0

    since = datetime.now(timezone.utc) - timedelta(hours=24)
    total_events_24h = db.query(func.count(models.Event.id)).filter(models.Event.timestamp >= since).scalar() or 0

    counts_raw = (
        db.query(models.Alert.status, func.count(models.Alert.id))
        .group_by(models.Alert.status)
        .all()
    )
    alert_counts = {"NORMAL": 0, "SUSPICIOUS": 0, "CRITICAL": 0}
    for status_val, count in counts_raw:
        alert_counts[status_val.value if hasattr(status_val, "value") else status_val] = count

    latest_alert = db.query(models.Alert).order_by(models.Alert.created_at.desc()).first()

    open_incidents = (
        db.query(func.count(models.Incident.id))
        .filter(models.Incident.status == models.IncidentStatus.open)
        .scalar()
        or 0
    )

    return schemas.DashboardOverview(
        total_devices=total_devices,
        isolated_devices=isolated_devices,
        total_events_24h=total_events_24h,
        alert_counts=alert_counts,
        latest_risk_score=latest_alert.risk_score if latest_alert else None,
        latest_status=latest_alert.status.value if latest_alert else None,
        open_incidents=open_incidents,
    )


@router.get("/timeline", response_model=list[schemas.AlertOut])
def timeline(
    hours: int = Query(default=24, le=168),
    db: Session = Depends(get_db),
    _user: models.User = Depends(get_current_user),
):
    """Chronological alert feed for the attack-timeline chart on the dashboard."""
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    return (
        db.query(models.Alert)
        .filter(models.Alert.created_at >= since)
        .order_by(models.Alert.created_at.asc())
        .all()
    )
