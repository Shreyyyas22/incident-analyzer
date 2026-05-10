"""
Celery worker task for AI-powered incident analysis.
Dispatched automatically when an incident is created.
"""
import asyncio
from app.workers.celery_app import celery_app
from app.services.ai_analysis_service import analyze_incident
import structlog

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

logger = structlog.get_logger()


def _make_session():
    """Create a fresh engine + session factory per task invocation."""
    engine = create_async_engine(settings.DATABASE_URL, pool_size=5, max_overflow=2)
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False), engine


async def async_analyze_incident(incident_id: str):
    SessionLocal, engine = _make_session()
    async with SessionLocal() as session:
        result = await analyze_incident(session, incident_id)
        if result:
            logger.info("AI analysis stored", incident_id=incident_id, severity=result.get("severity"))
        else:
            logger.warning("AI analysis returned no result", incident_id=incident_id)
    await engine.dispose()


@celery_app.task(
    name="analyze_incident",
    bind=True,
    max_retries=3,
    default_retry_delay=10,
)
def analyze_incident_task(self, incident_id: str):
    try:
        asyncio.run(async_analyze_incident(incident_id))
    except Exception as exc:
        logger.error("AI analysis task failed, retrying", incident_id=incident_id, error=str(exc), retry=self.request.retries)
        raise self.retry(exc=exc, countdown=10 * (self.request.retries + 1))
