"""Contract request/response schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ContractUploadResponse(BaseModel):
    """Response after uploading a contract."""
    contract_id: UUID
    status: str = "pending"


class ContractStatusResponse(BaseModel):
    """Polling response for contract processing status."""
    status: str
    progress_percent: int = 0
    error_message: Optional[str] = None


class ContractListItem(BaseModel):
    """Single item in the contracts list."""
    id: UUID
    filename: str
    status: str
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    upload_date: datetime

    model_config = {"from_attributes": True}


class ContractDetail(BaseModel):
    """Full contract detail with clauses and risks."""
    id: UUID
    filename: str
    file_size: Optional[int] = None
    page_count: Optional[int] = None
    status: str
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    summary: Optional[str] = None
    error_message: Optional[str] = None
    upload_date: datetime
    completed_at: Optional[datetime] = None
    clauses: list["ClauseResponse"] = []
    risks: list["RiskResponse"] = []

    model_config = {"from_attributes": True}


class ClauseResponse(BaseModel):
    """Clause data in contract detail."""
    id: UUID
    clause_type: str
    clause_text: str
    risk_level: Optional[str] = None
    page_number: Optional[int] = None

    model_config = {"from_attributes": True}


class RiskResponse(BaseModel):
    """Risk data in contract detail."""
    id: UUID
    risk_type: str
    severity: str
    finding: str
    explanation: str
    recommendation: str
    source_text: str
    confidence: Optional[float] = None
    clause_id: Optional[UUID] = None

    model_config = {"from_attributes": True}


class DashboardStats(BaseModel):
    """Aggregate dashboard statistics."""
    total_contracts: int = 0
    risk_distribution: dict[str, int] = Field(default_factory=dict)
    recent_uploads: list[ContractListItem] = []
    avg_risk_score: Optional[float] = None
