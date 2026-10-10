from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, EmailStr, ConfigDict

from app.models import UserRole, RiskStatus, IncidentStatus


# ---------- Auth / Users ----------

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.viewer


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    username: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Devices ----------

class DeviceCreate(BaseModel):
    device_name: str
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    location: Optional[str] = None


class DeviceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    device_name: str
    ip_address: Optional[str]
    mac_address: Optional[str]
    location: Optional[str]
    api_key: str
    is_isolated: bool
    last_seen: Optional[datetime]
    registered_at: datetime


class DeviceHeartbeat(BaseModel):
    status_note: Optional[str] = None


# ---------- Events ----------

class EventCreate(BaseModel):
    event_type: str                       # file_modified | file_renamed | file_deleted | heartbeat | canary_trip
    file_path: Optional[str] = None
    process_name: Optional[str] = None
    features: Optional[dict[str, Any]] = None   # raw feature vector for the ML engine


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    device_id: str
    event_type: str
    file_path: Optional[str]
    process_name: Optional[str]
    features: Optional[dict[str, Any]]
    timestamp: datetime


# ---------- Alerts ----------

class AlertCreate(BaseModel):
    """Payload the ML engine (Member 2) / rule engine (Member 4) POST to ingest a scored event."""
    event_id: Optional[str] = None
    reason: str
    base_risk: float = 0.0
    ml_score: float = 0.0                        # 0-100 confidence from RanSAP/RanSMAP
    shap_explanation: Optional[dict[str, float]] = None


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    device_id: str
    event_id: Optional[str]
    reason: str
    base_risk: float
    ml_score: float
    risk_score: int
    status: RiskStatus
    shap_explanation: Optional[dict[str, Any]]
    auto_isolated: bool
    created_at: datetime


class AlertStatusUpdate(BaseModel):
    status: RiskStatus


# ---------- Incidents ----------

class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    alert_id: str
    time_of_detection: datetime
    system_network_affected: str
    symptoms_observed: str
    threat_classification: str
    suspected_source: Optional[str]
    business_impact: str
    action_taken: str
    technical_iocs: Optional[str]
    point_of_contact: str
    status: IncidentStatus
    created_at: datetime
    updated_at: datetime


class IncidentStatusUpdate(BaseModel):
    status: IncidentStatus


# ---------- Dashboard ----------

class DashboardOverview(BaseModel):
    total_devices: int
    isolated_devices: int
    total_events_24h: int
    alert_counts: dict[str, int]      # {"NORMAL": x, "SUSPICIOUS": y, "CRITICAL": z}
    latest_risk_score: Optional[int]
    latest_status: Optional[str]
    open_incidents: int
