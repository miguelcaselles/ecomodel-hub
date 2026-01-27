from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    simulations,
    models,
    scenarios,
    parameters,
    organizations,
    users,
    reports,
)

api_router = APIRouter()

# Authentication
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Organizations & Users (Admin)
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# Economic Models & Parameters (Admin creates, all read)
api_router.include_router(models.router, prefix="/models", tags=["Economic Models"])
api_router.include_router(parameters.router, prefix="/parameters", tags=["Parameters"])

# Scenarios (User CRUD within org)
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["Scenarios"])

# Simulations (User runs on scenarios)
api_router.include_router(simulations.router, prefix="/simulations", tags=["Simulations"])

# Reports (PDF and Excel export)
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
