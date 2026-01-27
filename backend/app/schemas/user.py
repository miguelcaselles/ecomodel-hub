from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=200)
    role: str = Field(..., pattern="^(global_admin|local_user|viewer)$")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    organization_id: UUID


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    role: Optional[str] = Field(None, pattern="^(global_admin|local_user|viewer)$")
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    organization_id: Optional[UUID] = None


class UserInDB(UserBase):
    id: UUID
    organization_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class User(UserInDB):
    """User response without sensitive data"""
    pass


class UserWithOrganization(User):
    """User with organization details"""
    organization_name: Optional[str] = None
    organization_country: Optional[str] = None


class UserMe(User):
    """Current user profile"""
    pass
