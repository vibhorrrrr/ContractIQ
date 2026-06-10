"""Contract repository — all database operations for contracts."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.contract import Contract


class ContractRepository:
    """Database access layer for contracts. Every query filters by company_id."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, contract: Contract) -> Contract:
        """Insert a new contract row."""
        self.db.add(contract)
        await self.db.flush()
        await self.db.refresh(contract)
        return contract

    async def get_by_id(self, contract_id: UUID, company_id: UUID) -> Optional[Contract]:
        """Get a single contract with clauses and risks loaded."""
        result = await self.db.execute(
            select(Contract)
            .options(selectinload(Contract.clauses), selectinload(Contract.risks))
            .where(Contract.id == contract_id, Contract.company_id == company_id)
        )
        return result.scalar_one_or_none()

    async def list_by_company(self, company_id: UUID) -> list[Contract]:
        """List all contracts for a company, newest first."""
        result = await self.db.execute(
            select(Contract)
            .where(Contract.company_id == company_id)
            .order_by(Contract.upload_date.desc())
        )
        return list(result.scalars().all())

    async def get_recent(self, company_id: UUID, limit: int = 5) -> list[Contract]:
        """Get the most recent contracts for a company."""
        result = await self.db.execute(
            select(Contract)
            .where(Contract.company_id == company_id)
            .order_by(Contract.upload_date.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_status(
        self,
        contract_id: UUID,
        company_id: UUID,
        status: str,
        error_message: Optional[str] = None,
        risk_score: Optional[float] = None,
        risk_level: Optional[str] = None,
        summary: Optional[str] = None,
    ) -> None:
        """Update contract processing status and optional fields."""
        values: dict = {"status": status}
        if error_message is not None:
            values["error_message"] = error_message
        if risk_score is not None:
            values["risk_score"] = risk_score
        if risk_level is not None:
            values["risk_level"] = risk_level
        if summary is not None:
            values["summary"] = summary
        if status == "completed":
            values["completed_at"] = datetime.utcnow()

        await self.db.execute(
            update(Contract)
            .where(Contract.id == contract_id, Contract.company_id == company_id)
            .values(**values)
        )

    async def delete(self, contract_id: UUID, company_id: UUID) -> bool:
        """Delete a contract (cascades to clauses and risks)."""
        contract = await self.get_by_id(contract_id, company_id)
        if contract is None:
            return False
        await self.db.delete(contract)
        return True

    async def count_by_company(self, company_id: UUID) -> int:
        """Count total contracts for a company."""
        result = await self.db.execute(
            select(func.count()).select_from(Contract).where(Contract.company_id == company_id)
        )
        return result.scalar() or 0

    async def avg_risk_score(self, company_id: UUID) -> Optional[float]:
        """Calculate average risk score for completed contracts."""
        result = await self.db.execute(
            select(func.avg(Contract.risk_score))
            .where(Contract.company_id == company_id, Contract.status == "completed")
        )
        val = result.scalar()
        return round(val, 2) if val is not None else None

    async def risk_distribution(self, company_id: UUID) -> dict[str, int]:
        """Count contracts by risk level."""
        result = await self.db.execute(
            select(Contract.risk_level, func.count())
            .where(Contract.company_id == company_id, Contract.risk_level.isnot(None))
            .group_by(Contract.risk_level)
        )
        return {row[0]: row[1] for row in result.all()}
