from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.database import get_db
from app.schemas.log import LogCreate
from app.repositories import log_repo
from app.auth import get_current_service
from app.models.service import Service
from app.services.log_service import check_rate_limit, redis_client
from app.repositories import incident_repo
from app.workers.ai_worker import analyze_incident_task
from app.models.log import LogLevel

router = APIRouter(prefix="/logs", tags=["logs"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def ingest_log(
    log_in: LogCreate,
    background_tasks: BackgroundTasks,
    current_service: Service = Depends(get_current_service),
    session: AsyncSession = Depends(get_db)
):
    await check_rate_limit(current_service.id)
    
    new_log = await log_repo.create_log(session, current_service.id, log_in)
    
    log_data = {
        "id": new_log.id,
        "service_name": log_in.service_name,
        "log_level": log_in.log_level.value,
        "message": log_in.message,
        "timestamp": log_in.timestamp.isoformat(),
        "metadata": log_in.metadata,
        "trace_id": log_in.trace_id
    }
    log_data_json = json.dumps(log_data)
    
    async def publish_log(channel: str, message: str):
        await redis_client.publish(channel, message)

    background_tasks.add_task(
        publish_log,
        f"logs:{log_in.service_name}",
        log_data_json
    )
    # Instant Incident for CRITICAL logs
    if log_in.log_level == LogLevel.CRITICAL:
        async def trigger_incident():
            async with session.begin_nested():
                open_incident = await incident_repo.get_open_incident(session, current_service.id)
                if not open_incident:
                    incident = await incident_repo.create_incident(
                        session, 
                        current_service.id, 
                        summary=f"CRITICAL: {log_in.message[:100]}"
                    )
                    analyze_incident_task.delay(incident.id)

        background_tasks.add_task(trigger_incident)

    background_tasks.add_task(
        publish_log,
        "logs:all",
        log_data_json
    )
    
    return {"status": "accepted", "log_id": new_log.id}
