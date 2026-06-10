"""Contract API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.contract import (
    ContractDetail,
    ContractListItem,
    ContractStatusResponse,
    ContractUploadResponse,
)
from app.services.contract_service import ContractService

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.post("/upload", response_model=ContractUploadResponse)
async def upload_contract(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ContractUploadResponse:
    """Upload a contract file for analysis."""
    service = ContractService(db)
    return await service.upload(file, user)


@router.get("", response_model=list[ContractListItem])
async def list_contracts(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ContractListItem]:
    """List all contracts for the authenticated user's company."""
    service = ContractService(db)
    return await service.list_contracts(user)


@router.get("/{contract_id}", response_model=ContractDetail)
async def get_contract(
    contract_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ContractDetail:
    """Get full contract detail with clauses and risks."""
    service = ContractService(db)
    return await service.get_detail(contract_id, user)


@router.get("/{contract_id}/status", response_model=ContractStatusResponse)
async def get_contract_status(
    contract_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ContractStatusResponse:
    """Poll contract processing status."""
    service = ContractService(db)
    return await service.get_status(contract_id, user)


@router.delete("/{contract_id}")
async def delete_contract(
    contract_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Delete a contract and all related data."""
    service = ContractService(db)
    await service.delete_contract(contract_id, user)
    return {"detail": "Contract deleted."}
