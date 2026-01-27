from pydantic import BaseModel
from typing import Dict, Optional
from uuid import UUID
from app.models.simulation import SimulationType, SimulationStatus


class SimulationRequest(BaseModel):
    scenario_id: UUID
    simulation_type: SimulationType = SimulationType.DETERMINISTIC
    iterations: Optional[int] = None  # For PSA
    seed: Optional[int] = None  # For reproducibility


class SimulationResponse(BaseModel):
    id: UUID
    scenario_id: UUID
    simulation_type: SimulationType
    status: SimulationStatus
    results: Optional[Dict] = None
    sensitivity_results: Optional[Dict] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
