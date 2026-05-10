from fastapi import Depends, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.service import Service
from app.repositories import service_repo

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_current_service(
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_db)
) -> Service:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key"
        )
    service = await service_repo.get_service_by_api_key(session, api_key)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return service
