from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class ParameterBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    name: str = Field(..., min_length=1, max_length=100, description="Code name for parameter")
    display_name: str = Field(..., min_length=1, max_length=200, description="Human-readable name")
    description: Optional[str] = None
    category: str = Field(default="general", max_length=100, description="e.g., 'costs', 'probabilities', 'utilities'")
    data_type: str = Field(default="FLOAT", pattern="^(FLOAT|INT|PERCENTAGE|CURRENCY|BOOLEAN|float|int|percentage|currency|boolean)$")
    input_type: str = Field(default="NUMBER", pattern="^(SLIDER|NUMBER|SELECT|CHECKBOX|slider|number|select|checkbox)$")
    constraints: Optional[dict] = Field(default_factory=dict, description="min, max, step, options")
    default_value: Optional[float] = None
    distribution: Optional[dict] = Field(default_factory=dict, description="type, params for PSA")
    is_country_specific: bool = Field(default=False)
    is_editable_by_local: bool = Field(default=True)
    unit: Optional[str] = Field(None, max_length=20, description="e.g., 'EUR', '%'")
    display_order: int = Field(default=0)


class ParameterCreate(ParameterBase):
    model_id: UUID


class ParameterBulkCreate(BaseModel):
    model_id: UUID
    parameters: List[ParameterBase]


class ParameterUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    display_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    data_type: Optional[str] = Field(None, pattern="^(FLOAT|INT|PERCENTAGE|CURRENCY|BOOLEAN)$")
    input_type: Optional[str] = Field(None, pattern="^(SLIDER|NUMBER|SELECT|CHECKBOX)$")
    constraints: Optional[dict] = None
    default_value: Optional[float] = None
    distribution: Optional[dict] = None
    is_country_specific: Optional[bool] = None
    is_editable_by_local: Optional[bool] = None
    unit: Optional[str] = Field(None, max_length=20)
    display_order: Optional[int] = None


class ParameterInDB(ParameterBase):
    id: UUID
    model_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Parameter(ParameterInDB):
    pass


class ParameterWithModel(Parameter):
    """Parameter with model details"""
    model_name: Optional[str] = None
