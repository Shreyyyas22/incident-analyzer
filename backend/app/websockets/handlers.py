import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websockets.manager import manager
from app.services.log_service import redis_client
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/ws", tags=["websockets"])

@router.websocket("/logs")
async def websocket_logs_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We don't expect messages from client, but keeping the loop alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error("WebSocket connection error", error=str(e))
        manager.disconnect(websocket)

async def listen_to_redis():
    """Background task to listen to Redis Pub/Sub and broadcast to WebSockets."""
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("logs:all")
    logger.info("Subscribed to Redis channel logs:all")

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = message["data"]
                await manager.broadcast(data)
    except Exception as e:
        logger.error("Redis pubsub listener error", error=str(e))
