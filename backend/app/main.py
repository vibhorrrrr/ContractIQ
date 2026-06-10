"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.contracts import router as contracts_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.health import router as health_router

app = FastAPI(
    title="ContractIQ",
    description="AI-Powered Contract Intelligence Platform",
    version="1.0.0",
)

# CORS — allow frontend in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(health_router, tags=["health"])
app.include_router(contracts_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
