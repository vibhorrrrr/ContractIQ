"""Models package — import all models for Alembic discovery."""

from app.models.user import User
from app.models.company import Company
from app.models.contract import Contract
from app.models.clause import Clause
from app.models.risk import Risk
from app.models.benchmark import Benchmark

__all__ = ["User", "Company", "Contract", "Clause", "Risk", "Benchmark"]
