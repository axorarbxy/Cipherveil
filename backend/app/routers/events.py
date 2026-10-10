from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.deps import get_current_user, get_device_from_api_key

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("", response_model=schemas.EventOut, status_code=201)
def ingest_event(
    payload: schemas.EventCreate,
    db: Session = Depends(get_db),
    device: models.Device = Depends(get_device_from_api_key),
):
    """
    Ingestion endpoint for the monitoring agent (Member 3): file/process activity
    and raw feature vectors (entropy, mod-rate, extension changes, etc.) that Member 2's
    ML engine and Member 4's rule engine consume to compute risk.
    """
    event = models.Event(device_id=device.id, **payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("", response_model=list[schemas.EventOut])
def list_events(
    device_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db),
    _user: models.User = Depends(get_current_user),
):
    query = db.query(models.Event)
    if device_id:
        query = query.filter(models.Event.device_id == device_id)
    if event_type:
        query = query.filter(models.Event.event_type == event_type)
    return query.order_by(models.Event.timestamp.desc()).limit(limit).all()


@router.get("/{event_id}", response_model=schemas.EventOut)
def get_event(event_id: str, db: Session = Depends(get_db), _user: models.User = Depends(get_current_user)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
