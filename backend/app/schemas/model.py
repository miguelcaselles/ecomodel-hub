from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class ModelBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    model_type: str = Field(..., pattern="^(MARKOV|DECISION_TREE|PARTITION_SURVIVAL|markov|decision_tree|partition_survival)$")
    script_content: Optional[str] = None
    config: Optional[dict] = Field(default_factory=dict)
    version: str = Field(default="1.0")


class ModelCreate(ModelBase):
    pass


class ModelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    model_type: Optional[str] = Field(None, pattern="^(MARKOV|DECISION_TREE|PARTITION_SURVIVAL|markov|decision_tree|partition_survival)$")
    script_content: Optional[str] = None
    config: Optional[dict] = None
    version: Optional[str] = None


class ModelInDB(ModelBase):
    id: UUID
    is_published: bool
    script_hash: Optional[str] = None
    created_by_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Model(ModelInDB):
    pass


class ModelWithStats(Model):
    """Model with parameter and scenario counts"""
    parameter_count: int = 0
    scenario_count: int = 0
    created_by_name: Optional[str] = None


class ModelPublish(BaseModel):
    """Request to publish/unpublish a model"""
    is_published: bool
