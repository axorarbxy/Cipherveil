import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Integer, Float, DateTime, ForeignKey, JSON, Enum, Boolean, Text
)
from sqlalchemy.orm import relationship

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UserRole(str, enum.Enum):
    admin = "admin"
    security_team = "security_team"
    viewer = "viewer"


class RiskStatus(str, enum.Enum):
    NORMAL = "NORMAL"
    SUSPICIOUS = "SUSPICIOUS"
    CRITICAL = "CRITICAL"


class IncidentStatus(str, enum.Enum):
    open = "open"
    contained = "contained"
    closed = "closed"


class User(Base):
    """Admin / Security Team accounts (dashboard login)."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=_uuid)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.viewer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)


class Device(Base):
    """
    A monitored endpoint / institutional SMB share / sidecar appliance.
    Each device gets an api_key used by the monitoring agent (Member 3) and
    ML engine (Member 2) to push telemetry without a user login.
    """
    __tablename__ = "devices"

    id = Column(String(36), primary_key=True, default=_uuid)
    device_name = Column(String(120), nullable=False)
    ip_address = Column(String(45), nullable=True)
    mac_address = Column(String(20), nullable=True)
    location = Column(String(120), nullable=True)          # e.g. "SMB Share: \\INST-NAS-01\\Shared Documents"
    api_key = Column(String(64), unique=True, index=True, default=lambda: uuid.uuid4().hex)
    is_isolated = Column(Boolean, default=False)             # simulated network isolation flag
    last_seen = Column(DateTime, nullable=True)               # last heartbeat
    registered_at = Column(DateTime, default=_utcnow)

    events = relationship("Event", back_populates="device", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="device", cascade="all, delete-orphan")


class Event(Base):
    """
    Raw telemetry ingested from the monitoring agent (file/process/heartbeat activity)
    and/or feature vectors ingested from the ML engine before scoring.
    """
    __tablename__ = "events"

    id = Column(String(36), primary_key=True, default=_uuid)
    device_id = Column(String(36), ForeignKey("devices.id"), nullable=False)
    event_type = Column(String(40), nullable=False)   # file_modified | file_renamed | file_deleted | heartbeat | canary_trip
    file_path = Column(String(500), nullable=True)
    process_name = Column(String(200), nullable=True)
    features = Column(JSON, nullable=True)             # raw feature vector for the ML engine (entropy, mod-rate, ...)
    timestamp = Column(DateTime, default=_utcnow, index=True)

    device = relationship("Device", back_populates="events")


class Alert(Base):
    """
    Risk-fusion output: Tier-1 deterministic result + Tier-2 ML/SHAP result combined
    into a single 0-100 risk score and status band (NORMAL/SUSPICIOUS/CRITICAL).
    """
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=_uuid)
    device_id = Column(String(36), ForeignKey("devices.id"), nullable=False)
    event_id = Column(String(36), ForeignKey("events.id"), nullable=True)

    reason = Column(String(255), nullable=False)          # e.g. "Canary trip detected + Mass entropy delta"
    base_risk = Column(Float, default=0.0)
    ml_score = Column(Float, default=0.0)                  # 0-100 confidence from RanSAP/RanSMAP
    risk_score = Column(Integer, nullable=False)            # final fused 0-100 score
    status = Column(Enum(RiskStatus), nullable=False)
    shap_explanation = Column(JSON, nullable=True)          # {"Entropy": 0.42, "ModRate": 0.31, ...}
    auto_isolated = Column(Boolean, default=False)           # True if CRITICAL band triggered simulated isolation
    created_at = Column(DateTime, default=_utcnow, index=True)

    device = relationship("Device", back_populates="alerts")
    incident = relationship("Incident", back_populates="alert", uselist=False, cascade="all, delete-orphan")


class Incident(Base):
    """
    CERT-In mandatory 9-field incident record, generated from a CRITICAL (or manually
    escalated) alert. Mirrors cert_in_formatter.py from the sidecar prototype so the
    backend is the single source of truth for exportable incident reports.
    """
    __tablename__ = "incidents"

    id = Column(String(36), primary_key=True, default=_uuid)
    alert_id = Column(String(36), ForeignKey("alerts.id"), unique=True, nullable=False)

    # --- CERT-In 9 mandatory fields ---
    time_of_detection = Column(DateTime, nullable=False)
    system_network_affected = Column(String(255), nullable=False)
    symptoms_observed = Column(Text, nullable=False)
    threat_classification = Column(String(120), default="Cyber Security Incident - Ransomware / Mass Encryption")
    suspected_source = Column(String(120), nullable=True)     # "IP (MAC: ..)"
    business_impact = Column(Text, nullable=False)
    action_taken = Column(Text, nullable=False)
    technical_iocs = Column(Text, nullable=True)
    point_of_contact = Column(String(120), nullable=False)

    status = Column(Enum(IncidentStatus), default=IncidentStatus.open)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    alert = relationship("Alert", back_populates="incident")
