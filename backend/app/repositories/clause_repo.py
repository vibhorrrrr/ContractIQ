"""Clause repository — all database operations for clauses."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clause import Clause
from app.models.risk import Risk


class ClauseRepository:
    """Database access layer for clauses and risks."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def bulk_create_clauses(self, clauses: list[Clause]) -> list[Clause]:
        """Insert multiple clauses at once."""
        self.db.add_all(clauses)
        await self.db.flush()
        return clauses

    async def bulk_create_risks(self, risks: list[Risk]) -> list[Risk]:
        """Insert multiple risks at once."""
        self.db.add_all(risks)
        await self.db.flush()
        return risks

    async def get_clauses_by_contract(
        self, contract_id: UUID, company_id: UUID
    ) -> list[Clause]:
        """Get all clauses for a contract (company_id verified via join)."""
        from app.models.contract import Contract

        result = await self.db.execute(
            select(Clause)
            .join(Contract, Clause.contract_id == Contract.id)
            .where(Clause.contract_id == contract_id, Contract.company_id == company_id)
            .order_by(Clause.page_number, Clause.position_start)
        )
        return list(result.scalars().all())

    async def get_risks_by_contract(
        self, contract_id: UUID, company_id: UUID
    ) -> list[Risk]:
        """Get all risks for a contract (company_id verified via join)."""
        from app.models.contract import Contract

        result = await self.db.execute(
            select(Risk)
            .join(Contract, Risk.contract_id == Contract.id)
            .where(Risk.contract_id == contract_id, Contract.company_id == company_id)
            .order_by(Risk.created_at)
        )
        return list(result.scalars().all())
