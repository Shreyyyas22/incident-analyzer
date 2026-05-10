from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    environment: str

class ServiceResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    environment: str
    last_seen_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class ServiceRegisterResponse(BaseModel):
    service_id: str
    api_key: str
