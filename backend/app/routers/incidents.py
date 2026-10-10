from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.deps import get_current_user, require_admin

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("", response_model=list[schemas.IncidentOut])
def list_incidents(db: Session = Depends(get_db), _user: models.User = Depends(get_current_user)):
    return db.query(models.Incident).order_by(models.Incident.created_at.desc()).all()


@router.get("/{incident_id}", response_model=schemas.IncidentOut)
def get_incident(incident_id: str, db: Session = Depends(get_db), _user: models.User = Depends(get_current_user)):
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.patch("/{incident_id}/status", response_model=schemas.IncidentOut)
def update_incident_status(
    incident_id: str,
    payload: schemas.IncidentStatusUpdate,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.status = payload.status
    db.commit()
    db.refresh(incident)
    return incident


@router.get("/{incident_id}/cert-in-export")
def export_cert_in_report(incident_id: str, db: Session = Depends(get_db), _user: models.User = Depends(get_current_user)):
    """
    Returns the incident formatted as the CERT-In mandatory 9-field JSON object,
    ready to hand to cert_in_formatter.py's output stage or attach to a submission email.
    """
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    report = {
        "1_time_of_detection": incident.time_of_detection.isoformat(),
        "2_system_network_affected": incident.system_network_affected,
        "3_symptoms_observed": incident.symptoms_observed,
        "4_threat_classification": incident.threat_classification,
        "5_suspected_source": incident.suspected_source,
        "6_system_business_impact": incident.business_impact,
        "7_action_taken_mitigation": incident.action_taken,
        "8_technical_iocs_artifacts": incident.technical_iocs,
        "9_point_of_contact": incident.point_of_contact,
    }
    return JSONResponse(content=report)
