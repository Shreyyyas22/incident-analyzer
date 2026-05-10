from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from sqlalchemy.orm import selectinload
from app.models.incident import Incident, IncidentStatus

async def get_open_incident(session: AsyncSession, service_id: str) -> Incident | None:
    stmt = select(Incident).where(
        Incident.service_id == service_id,
        Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.ANALYZING])
    )
    result = await session.execute(stmt)
    return result.scalars().first()

async def get_incident_by_id(session: AsyncSession, incident_id: str) -> Incident | None:
    stmt = select(Incident).options(selectinload(Incident.service)).where(Incident.id == incident_id)
    result = await session.execute(stmt)
    return result.scalars().first()

async def create_incident(session: AsyncSession, service_id: str, summary: str = None) -> Incident:
    new_incident = Incident(
        service_id=service_id,
        status=IncidentStatus.OPEN,
        summary=summary
    )
    session.add(new_incident)
    await session.commit()
    await session.refresh(new_incident)
    return new_incident

async def update_incident_status(session: AsyncSession, incident_id: str, status: IncidentStatus):
    stmt = update(Incident).where(Incident.id == incident_id).values(status=status)
    await session.execute(stmt)
    await session.commit()

async def update_incident_analysis(session: AsyncSession, incident_id: str, analysis: dict, severity: str = None):
    values = {"analysis": analysis, "status": IncidentStatus.ANALYZED}
    if severity:
        values["severity"] = severity
    stmt = update(Incident).where(Incident.id == incident_id).values(**values)
    await session.execute(stmt)
    await session.commit()

async def get_all_incidents(session: AsyncSession, limit: int = 100, offset: int = 0):
    stmt = select(Incident).order_by(Incident.created_at.desc()).limit(limit).offset(offset)
    result = await session.execute(stmt)
    return result.scalars().all()
