from sqlalchemy import Column, String, DateTime, Enum, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.database import Base
import enum

class LogLevel(str, enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class Log(Base):
    __tablename__ = "logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    service_id = Column(String, ForeignKey("services.id"), nullable=False, index=True)
    log_level = Column(Enum(LogLevel), nullable=False, index=True)
    message = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    metadata_ = Column("metadata", JSON, nullable=True)
    trace_id = Column(String, index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    service = relationship("Service")
