from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
import secrets
from datetime import datetime, timezone
from app.models.service import Service
from app.schemas.service import ServiceCreate

async def get_service_by_api_key(session: AsyncSession, api_key: str) -> Service | None:
    stmt = select(Service).where(Service.api_key == api_key)
    result = await session.execute(stmt)
    return result.scalars().first()

async def get_service_by_name(session: AsyncSession, name: str) -> Service | None:
    stmt = select(Service).where(Service.name == name)
    result = await session.execute(stmt)
    return result.scalars().first()

async def create_service(session: AsyncSession, service_in: ServiceCreate) -> Service:
    api_key = f"sk_{service_in.environment}_{secrets.token_urlsafe(32)}"
    new_service = Service(
        name=service_in.name,
        description=service_in.description,
        environment=service_in.environment,
        api_key=api_key
    )
    session.add(new_service)
    await session.commit()
    await session.refresh(new_service)
    return new_service

async def update_heartbeat(session: AsyncSession, service_id: str):
    stmt = update(Service).where(Service.id == service_id).values(last_seen_at=datetime.now(timezone.utc))
    await session.execute(stmt)
    await session.commit()

async def get_all_services(session: AsyncSession, limit: int = 100) -> list[Service]:
    stmt = select(Service).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()
