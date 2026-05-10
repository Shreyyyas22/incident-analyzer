from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.incident import IncidentStatus

class IncidentAnalysis(BaseModel):
    summary: Optional[str] = None
    root_cause: Optional[str] = None
    severity: Optional[str] = None
    contributing_factors: Optional[List[str]] = None
    suggested_fixes: Optional[List[str]] = None
    confidence_score: Optional[float] = None

class IncidentResponse(BaseModel):
    id: str
    service_id: str
    status: IncidentStatus
    summary: Optional[str]
    severity: Optional[str]
    analysis: Optional[dict] = None
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True

class IncidentAnalysisResponse(BaseModel):
    incident_id: str
    status: IncidentStatus
    analysis: Optional[IncidentAnalysis] = None
