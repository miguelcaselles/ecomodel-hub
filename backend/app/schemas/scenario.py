from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class ScenarioBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    country_code: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2")
    parameter_values: dict = Field(default_factory=dict, description="Parameter values as key-value pairs")
    is_base_case: bool = Field(default=False)


class ScenarioCreate(ScenarioBase):
    model_id: UUID


class ScenarioClone(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Name for cloned scenario")
    description: Optional[str] = None


class ScenarioUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    country_code: Optional[str] = Field(None, min_length=2, max_length=2)
    parameter_values: Optional[dict] = None
    is_base_case: Optional[bool] = None
    is_locked: Optional[bool] = None


class ScenarioInDB(ScenarioBase):
    id: UUID
    model_id: UUID
    organization_id: UUID
    created_by_id: UUID
    is_locked: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Scenario(ScenarioInDB):
    pass


class ScenarioWithDetails(Scenario):
    """Scenario with related entity details"""
    model_name: Optional[str] = None
    organization_name: Optional[str] = None
    created_by_name: Optional[str] = None
    simulation_count: int = 0


class ScenarioCompare(BaseModel):
    """Request to compare multiple scenarios"""
    scenario_ids: list[UUID] = Field(..., min_items=2, max_items=5)
