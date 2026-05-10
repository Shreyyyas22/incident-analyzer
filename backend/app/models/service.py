from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
import uuid
from app.database import Base

class Service(Base):
    __tablename__ = "services"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    environment = Column(String, nullable=False)
    api_key = Column(String, unique=True, index=True, nullable=False)
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
