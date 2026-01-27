from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    country: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code")
    settings: Optional[dict] = Field(default_factory=dict)


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    country: Optional[str] = Field(None, min_length=2, max_length=2)
    settings: Optional[dict] = None


class OrganizationInDB(OrganizationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Organization(OrganizationInDB):
    pass


class OrganizationWithUsers(Organization):
    """Organization with user count"""
    user_count: int = 0
    scenario_count: int = 0
