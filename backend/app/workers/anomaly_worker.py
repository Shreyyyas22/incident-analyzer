import asyncio
from app.workers.celery_app import celery_app
from app.services.anomaly_service import check_anomaly
from app.repositories.incident_repo import get_open_incident, create_incident
from app.repositories.service_repo import get_all_services
import structlog
from datetime import datetime, timezone, timedelta
from app.workers.ai_worker import analyze_incident_task

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

logger = structlog.get_logger()

def _make_session():
    """Create a fresh engine + session factory per task invocation to avoid event loop conflicts."""
    engine = create_async_engine(settings.DATABASE_URL, pool_size=5, max_overflow=2)
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False), engine

async def async_run_anomaly_detection():
    SessionLocal, engine = _make_session()
    async with SessionLocal() as session:
        services = await get_all_services(session, limit=1000)
        for service in services:
            # Check for anomalies
            is_anomalous = await check_anomaly(session, service.id)
            if is_anomalous:
                open_incident = await get_open_incident(session, service.id)
                if not open_incident:
                    incident = await create_incident(
                        session, 
                        service.id, 
                        summary="High error rate detected in the last minute."
                    )
                    logger.warning("Incident automatically created", service_id=service.id, incident_id=incident.id)
                    analyze_incident_task.delay(incident.id)
            
            # Check for missing heartbeat (5 minutes)
            if service.last_seen_at:
                time_diff = datetime.now(timezone.utc) - service.last_seen_at.replace(tzinfo=timezone.utc)
                if time_diff > timedelta(minutes=5):
                    open_incident = await get_open_incident(session, service.id)
                    if not open_incident:
                        incident = await create_incident(
                            session, 
                            service.id, 
                            summary="Service has not sent a heartbeat in over 5 minutes."
                        )
                        logger.warning("Incident automatically created (Offline)", service_id=service.id, incident_id=incident.id)
                        analyze_incident_task.delay(incident.id)
    await engine.dispose()

@celery_app.task(name="check_anomalies_and_heartbeats")
def run_anomaly_detection():
    asyncio.run(async_run_anomaly_detection())
