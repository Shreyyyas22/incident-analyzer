from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timezone, timedelta
from app.models.log import Log, LogLevel

ANOMALY_THRESHOLD_COUNT = 10
ANOMALY_WINDOW_SECONDS = 60

async def check_anomaly(session: AsyncSession, service_id: str) -> bool:
    """
    Checks if a service has more than ANOMALY_THRESHOLD_COUNT errors
    in the last ANOMALY_WINDOW_SECONDS.
    """
    time_threshold = datetime.now(timezone.utc) - timedelta(seconds=ANOMALY_WINDOW_SECONDS)
    
    stmt = select(func.count(Log.id)).where(
        Log.service_id == service_id,
        Log.log_level.in_([LogLevel.ERROR, LogLevel.CRITICAL]),
        Log.timestamp >= time_threshold
    )
    
    result = await session.execute(stmt)
    error_count = result.scalar() or 0
    
    return error_count > ANOMALY_THRESHOLD_COUNT
