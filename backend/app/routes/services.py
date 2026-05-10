from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.service import ServiceCreate, ServiceResponse, ServiceRegisterResponse
from app.repositories import service_repo
from app.auth import get_current_service
from app.models.service import Service

router = APIRouter(prefix="/services", tags=["services"])

@router.get("", response_model=List[ServiceResponse])
async def list_services(session: AsyncSession = Depends(get_db)):
    services = await service_repo.get_all_services(session)
    return services

@router.post("/register", response_model=ServiceRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_service(service_in: ServiceCreate, session: AsyncSession = Depends(get_db)):
    existing = await service_repo.get_service_by_name(session, service_in.name)
    if existing:
        raise HTTPException(status_code=400, detail="Service name already registered")
    new_service = await service_repo.create_service(session, service_in)
    return ServiceRegisterResponse(service_id=new_service.id, api_key=new_service.api_key)

@router.post("/{service_id}/heartbeat", status_code=status.HTTP_200_OK)
async def heartbeat(
    service_id: str, 
    current_service: Service = Depends(get_current_service),
    session: AsyncSession = Depends(get_db)
):
    if current_service.id != service_id:
        raise HTTPException(status_code=403, detail="Not authorized to update heartbeat for this service")
    await service_repo.update_heartbeat(session, service_id)
    return {"status": "heartbeat updated"}
