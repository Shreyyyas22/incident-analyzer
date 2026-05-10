from fastapi import FastAPI
from app.config import settings
import structlog

logger = structlog.get_logger()

app = FastAPI(title="AI Incident Analyzer", version="1.0.0")

from app.routes import services, logs, incidents
from app.websockets import handlers
import asyncio

app.include_router(services.router)
app.include_router(logs.router)
app.include_router(incidents.router)
app.include_router(handlers.router)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up FastAPI...", environment=settings.ENVIRONMENT)
    asyncio.create_task(handlers.listen_to_redis())

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "postgres": "ok",
        "redis": "ok"
    }
