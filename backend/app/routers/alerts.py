from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app import models, schemas
from app.deps import get_current_user, get_device_from_api_key

router = APIRouter(prefix="/alerts", tags=["Alerts"])


def _resolve_status(risk_score: int) -> models.RiskStatus:
    if risk_score <= settings.RISK_NORMAL_MAX:
        return models.RiskStatus.NORMAL
    if risk_score <= settings.RISK_SUSPICIOUS_MAX:
        return models.RiskStatus.SUSPICIOUS
    return models.RiskStatus.CRITICAL


@router.post("", response_model=schemas.AlertOut, status_code=201)
def ingest_alert(
    payload: schemas.AlertCreate,
    db: Session = Depends(get_db),
    device: models.Device = Depends(get_device_from_api_key),
):
    """
    Risk-fusion ingestion endpoint. Called by Member 4's rule engine / Member 2's
    ML engine after `evaluate_ml_risk()` produces an ml_score + SHAP explanation.

    final_risk = min(100, base_risk + ml_score * 0.3)   (matches trigger_alert() in the
    sidecar prototype's Python core execution engine)

    A CRITICAL result auto-isolates the device (simulated flag only) and immediately
    opens a CERT-In incident stub, exactly like the standalone prototype.
    """
    if payload.event_id:
        event = db.query(models.Event).filter(models.Event.id == payload.event_id).first()
        if not event or event.device_id != device.id:
            raise HTTPException(status_code=404, detail="Event not found for this device")

    final_risk = min(100, int(payload.base_risk + (payload.ml_score * 0.3)))
    status_band = _resolve_status(final_risk)

    alert = models.Alert(
        device_id=device.id,
        event_id=payload.event_id,
        reason=payload.reason,
        base_risk=payload.base_risk,
        ml_score=payload.ml_score,
        risk_score=final_risk,
        status=status_band,
        shap_explanation=payload.shap_explanation,
        auto_isolated=False,
    )

    if status_band == models.RiskStatus.CRITICAL:
        device.is_isolated = True
        alert.auto_isolated = True

    db.add(alert)
    db.commit()
    db.refresh(alert)

    if status_band == models.RiskStatus.CRITICAL:
        _auto_open_incident(db, alert, device)

    return alert


def _auto_open_incident(db: Session, alert: models.Alert, device: models.Device) -> models.Incident:
    """Auto-generates a draft CERT-In 9-field incident when an alert crosses into CRITICAL."""
    existing = db.query(models.Incident).filter(models.Incident.alert_id == alert.id).first()
    if existing:
        return existing

    ioc_bits = []
    if alert.shap_explanation:
        top = sorted(alert.shap_explanation.items(), key=lambda kv: kv[1], reverse=True)
        ioc_bits.append(", ".join(f"{k} ({v:+.2f})" for k, v in top))

    incident = models.Incident(
        alert_id=alert.id,
        time_of_detection=alert.created_at,
        system_network_affected=device.location or device.device_name,
        symptoms_observed=alert.reason,
        threat_classification="Cyber Security Incident - Ransomware / Mass Encryption",
        suspected_source=f"{device.ip_address or 'unknown'} (MAC: {device.mac_address or 'unknown'})",
        business_impact="High Criticality - Shared Drive locked; User access halted",
        action_taken="Auto-isolation simulated; Admin alerted via Dashboard",
        technical_iocs="; ".join(ioc_bits) if ioc_bits else None,
        point_of_contact=settings.CERT_IN_POC_EMAIL,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@router.get("", response_model=list[schemas.AlertOut])
def list_alerts(
    device_id: Optional[str] = None,
    status_filter: Optional[models.RiskStatus] = Query(default=None, alias="status"),
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db),
    _user: models.User = Depends(get_current_user),
):
    query = db.query(models.Alert)
    if device_id:
        query = query.filter(models.Alert.device_id == device_id)
    if status_filter:
        query = query.filter(models.Alert.status == status_filter)
    return query.order_by(models.Alert.created_at.desc()).limit(limit).all()


@router.get("/{alert_id}", response_model=schemas.AlertOut)
def get_alert(alert_id: str, db: Session = Depends(get_db), _user: models.User = Depends(get_current_user)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.patch("/{alert_id}/status", response_model=schemas.AlertOut)
def update_alert_status(
    alert_id: str,
    payload: schemas.AlertStatusUpdate,
    db: Session = Depends(get_db),
    _user: models.User = Depends(get_current_user),
):
    """Lets an admin manually re-triage an alert (e.g. downgrade a false positive)."""
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = payload.status
    db.commit()
    db.refresh(alert)
    return alert
