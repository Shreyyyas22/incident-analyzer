from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.log import LogLevel

class LogCreate(BaseModel):
    service_name: str
    log_level: LogLevel
    message: str = Field(..., max_length=10000)
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = None
