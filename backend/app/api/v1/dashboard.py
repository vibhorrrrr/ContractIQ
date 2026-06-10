"""Dashboard API endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.contract import DashboardStats
from app.services.contract_service import ContractService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DashboardStats:
    """Get aggregate dashboard statistics for the user's company."""
    service = ContractService(db)
    return await service.get_dashboard_stats(user)
