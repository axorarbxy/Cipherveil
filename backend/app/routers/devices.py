from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.deps import get_current_user, require_admin, get_device_from_api_key

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.post("", response_model=schemas.DeviceOut, status_code=status.HTTP_201_CREATED)
def register_device(
    payload: schemas.DeviceCreate,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    """Admin registers a new institutional endpoint / sidecar appliance and receives its API key."""
    device = models.Device(**payload.model_dump())
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


@router.get("", response_model=list[schemas.DeviceOut])
def list_devices(db: Session = Depends(get_db), _user: models.User = Depends(get_current_user)):
    return db.query(models.Device).order_by(models.Device.registered_at.desc()).all()


@router.get("/{device_id}", response_model=schemas.DeviceOut)
def get_device(device_id: str, db: Session = Depends(get_db), _user: models.User = Depends(get_current_user)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(device_id: str, db: Session = Depends(get_db), _admin: models.User = Depends(require_admin)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    db.delete(device)
    db.commit()


@router.post("/heartbeat", response_model=schemas.DeviceOut)
def heartbeat(
    payload: schemas.DeviceHeartbeat,
    db: Session = Depends(get_db),
    device: models.Device = Depends(get_device_from_api_key),
):
    """
    Dead-man's-switch heartbeat. The sidecar / monitoring agent calls this on a
    regular interval; a missed heartbeat window is treated as CRITICAL upstream
    (Member 4's risk-fusion logic) since last_seen will stop advancing.
    """
    device.last_seen = datetime.now(timezone.utc)
    db.commit()
    db.refresh(device)
    return device


@router.post("/{device_id}/isolate", response_model=schemas.DeviceOut)
def simulate_isolation(device_id: str, db: Session = Depends(get_db), _admin: models.User = Depends(require_admin)):
    """
    Manually trigger the SAFE, simulated network isolation flag for a device
    (mirrors isolate_network_segment() in the sidecar prototype — no real network
    commands are executed, matching the SIH safe-prototype boundary).
    """
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    device.is_isolated = True
    db.commit()
    db.refresh(device)
    return device


@router.post("/{device_id}/restore", response_model=schemas.DeviceOut)
def restore_from_isolation(device_id: str, db: Session = Depends(get_db), _admin: models.User = Depends(require_admin)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    device.is_isolated = False
    db.commit()
    db.refresh(device)
    return device
