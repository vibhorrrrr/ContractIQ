"""Contract service — business logic for contract operations."""

import logging
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.contract import Contract
from app.models.user import User
from app.repositories.contract_repo import ContractRepository
from app.schemas.contract import (
    ContractDetail,
    ContractListItem,
    ContractStatusResponse,
    ContractUploadResponse,
    DashboardStats,
)
from app.services.storage_service import StorageService

logger = logging.getLogger(__name__)

storage = StorageService()


class ContractService:
    """Orchestrates contract upload, retrieval, deletion, and dashboard stats."""

    def __init__(self, db: AsyncSession) -> None:
        self.repo = ContractRepository(db)
        self.db = db

    async def upload(self, file: UploadFile, user: User) -> ContractUploadResponse:
        """Validate, store, and enqueue a contract for processing."""
        self._validate_file(file)

        if user.company_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not associated with a company.",
            )

        file_path, file_size = await storage.save_file(file)

        contract = Contract(
            company_id=user.company_id,
            uploaded_by=user.id,
            filename=file.filename or "unknown",
            file_path=file_path,
            file_size=file_size,
            status="pending",
        )
        contract = await self.repo.create(contract)

        # Push to Redis queue (handled by worker)
        await self._enqueue_analysis(contract.id, user.company_id)

        return ContractUploadResponse(contract_id=contract.id, status="pending")

    async def list_contracts(self, user: User) -> list[ContractListItem]:
        """List all contracts for the user's company."""
        contracts = await self.repo.list_by_company(user.company_id)
        return [ContractListItem.model_validate(c) for c in contracts]

    async def get_detail(self, contract_id: UUID, user: User) -> ContractDetail:
        """Get full contract detail with clauses and risks."""
        contract = await self.repo.get_by_id(contract_id, user.company_id)
        if contract is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found.",
            )
        return ContractDetail.model_validate(contract)

    async def get_status(self, contract_id: UUID, user: User) -> ContractStatusResponse:
        """Get processing status for polling."""
        contract = await self.repo.get_by_id(contract_id, user.company_id)
        if contract is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found.",
            )

        progress = 0
        if contract.status == "processing":
            progress = 50
        elif contract.status == "completed":
            progress = 100
        elif contract.status == "failed":
            progress = 100

        return ContractStatusResponse(
            status=contract.status,
            progress_percent=progress,
            error_message=contract.error_message,
        )

    async def delete_contract(self, contract_id: UUID, user: User) -> None:
        """Delete a contract and its stored file."""
        contract = await self.repo.get_by_id(contract_id, user.company_id)
        if contract is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found.",
            )

        await storage.delete_file(contract.file_path)
        await self.repo.delete(contract_id, user.company_id)

    async def get_dashboard_stats(self, user: User) -> DashboardStats:
        """Aggregate dashboard statistics for the user's company."""
        total = await self.repo.count_by_company(user.company_id)
        avg_score = await self.repo.avg_risk_score(user.company_id)
        distribution = await self.repo.risk_distribution(user.company_id)
        recent = await self.repo.get_recent(user.company_id, limit=5)

        return DashboardStats(
            total_contracts=total,
            risk_distribution=distribution,
            recent_uploads=[ContractListItem.model_validate(c) for c in recent],
            avg_risk_score=avg_score,
        )

    def _validate_file(self, file: UploadFile) -> None:
        """Validate file type and size constraints."""
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required.",
            )

        ext = Path(file.filename).suffix.lower().lstrip(".")
        if ext not in settings.allowed_extensions_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: .{ext}. Allowed: {settings.ALLOWED_EXTENSIONS}",
            )

        if file.size is not None and file.size > settings.max_file_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File exceeds maximum size of {settings.MAX_FILE_SIZE_MB}MB.",
            )

        if file.size is not None and file.size < 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File appears to be empty or too small.",
            )

    async def _enqueue_analysis(self, contract_id: UUID, company_id: UUID) -> None:
        """Push analysis job to Redis queue."""
        import redis.asyncio as aioredis

        r = aioredis.from_url(settings.REDIS_URL)
        try:
            await r.lpush(
                "contractiq:analysis_queue",
                f"{contract_id}:{company_id}",
            )
        finally:
            await r.aclose()
