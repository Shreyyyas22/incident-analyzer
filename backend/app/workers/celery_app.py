from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery(
    "incident_analyzer",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.anomaly_worker", "app.workers.ai_worker"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "run-anomaly-detection-every-30-seconds": {
            "task": "check_anomalies_and_heartbeats",
            "schedule": 30.0,
        },
    }
)
