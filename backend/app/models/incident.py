from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.database import Base

class IncidentStatus(str, enum.Enum):
    OPEN = "OPEN"
    ANALYZING = "ANALYZING"
    ANALYZED = "ANALYZED"
    RESOLVED = "RESOLVED"
    IGNORED = "IGNORED"

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    service_id = Column(String, ForeignKey("services.id"), nullable=False, index=True)
    status = Column(Enum(IncidentStatus), nullable=False, default=IncidentStatus.OPEN, index=True)
    summary = Column(String, nullable=True)
    severity = Column(String, nullable=True)
    analysis = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    service = relationship("Service")

