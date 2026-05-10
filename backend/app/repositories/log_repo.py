from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone, timedelta
from app.models.log import Log, LogLevel
from app.schemas.log import LogCreate

async def create_log(session: AsyncSession, service_id: str, log_in: LogCreate) -> Log:
    new_log = Log(
        service_id=service_id,
        log_level=log_in.log_level,
        message=log_in.message,
        timestamp=log_in.timestamp,
        metadata_=log_in.metadata,
        trace_id=log_in.trace_id
    )
    session.add(new_log)
    await session.commit()
    await session.refresh(new_log)
    return new_log

async def get_recent_error_logs(session: AsyncSession, service_id: str, limit: int = 20) -> list[Log]:
    """Get the most recent ERROR/CRITICAL logs for a service."""
    stmt = (
        select(Log)
        .where(
            Log.service_id == service_id,
            Log.log_level.in_([LogLevel.ERROR, LogLevel.CRITICAL])
        )
        .order_by(Log.timestamp.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()

async def get_warning_logs_before(
    session: AsyncSession, service_id: str, before_time: datetime, minutes: int = 5
) -> list[Log]:
    """Get WARNING logs from a time window before the incident."""
    start_time = before_time - timedelta(minutes=minutes)
    stmt = (
        select(Log)
        .where(
            Log.service_id == service_id,
            Log.log_level == LogLevel.WARNING,
            Log.timestamp >= start_time,
            Log.timestamp <= before_time,
        )
        .order_by(Log.timestamp.desc())
        .limit(20)
    )
    result = await session.execute(stmt)
    return result.scalars().all()
