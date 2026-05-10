from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.incident import IncidentResponse, IncidentAnalysisResponse, IncidentAnalysis
from app.repositories import incident_repo

router = APIRouter(prefix="/incidents", tags=["incidents"])

@router.get("", response_model=List[IncidentResponse])
async def list_incidents(session: AsyncSession = Depends(get_db)):
    incidents = await incident_repo.get_all_incidents(session)
    return incidents

@router.get("/{incident_id}/analysis", response_model=IncidentAnalysisResponse)
async def get_incident_analysis(incident_id: str, session: AsyncSession = Depends(get_db)):
    incident = await incident_repo.get_incident_by_id(session, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    analysis = None
    if incident.analysis:
        analysis = IncidentAnalysis(**incident.analysis)
    
    return IncidentAnalysisResponse(
        incident_id=incident.id,
        status=incident.status,
        analysis=analysis
    )
