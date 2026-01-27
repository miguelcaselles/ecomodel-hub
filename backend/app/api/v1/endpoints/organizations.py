from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.models.user import User
from app.models.organization import Organization
from app.core.permissions import (
    get_current_user,
    require_global_admin,
)
from app.schemas import (
    Organization as OrganizationSchema,
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationWithUsers,
    User as UserSchema,
)

router = APIRouter()


@router.get("/", response_model=List[OrganizationWithUsers])
def list_organizations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List organizations.
    - Admins see all organizations
    - Regular users only see their own organization
    """
    if current_user.role == "global_admin":
        query = db.query(Organization)
    else:
        query = db.query(Organization).filter(
            Organization.id == current_user.organization_id
        )

    organizations = query.offset(skip).limit(limit).all()

    # Add stats
    result = []
    for org in organizations:
        org_dict = OrganizationSchema.from_orm(org).model_dump()
        org_dict["user_count"] = len(org.users)
        org_dict["scenario_count"] = len(org.scenarios)
        result.append(OrganizationWithUsers(**org_dict))

    return result


@router.post("/", response_model=OrganizationSchema, status_code=status.HTTP_201_CREATED)
def create_organization(
    org_data: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_global_admin),
):
    """Create a new organization. Admin only."""
    # Check if organization name already exists
    existing = db.query(Organization).filter(
        Organization.name == org_data.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Organization '{org_data.name}' already exists",
        )

    organization = Organization(**org_data.model_dump())

    db.add(organization)
    db.commit()
    db.refresh(organization)

    return OrganizationSchema.from_orm(organization)


@router.get("/{organization_id}", response_model=OrganizationWithUsers)
def get_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific organization"""
    organization = db.query(Organization).filter(
        Organization.id == organization_id
    ).first()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Non-admins can only see their own organization
    if (current_user.role != "global_admin" and
        str(organization.id) != str(current_user.organization_id)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Build response with stats
    org_dict = OrganizationSchema.from_orm(organization).model_dump()
    org_dict["user_count"] = len(organization.users)
    org_dict["scenario_count"] = len(organization.scenarios)

    return OrganizationWithUsers(**org_dict)


@router.patch("/{organization_id}", response_model=OrganizationSchema)
def update_organization(
    organization_id: UUID,
    org_data: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_global_admin),
):
    """Update an organization. Admin only."""
    organization = db.query(Organization).filter(
        Organization.id == organization_id
    ).first()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Check if name is being changed and if it conflicts
    if org_data.name and org_data.name != organization.name:
        existing = db.query(Organization).filter(
            Organization.name == org_data.name
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Organization '{org_data.name}' already exists",
            )

    # Update fields
    update_data = org_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(organization, field, value)

    db.commit()
    db.refresh(organization)

    return OrganizationSchema.from_orm(organization)


@router.get("/{organization_id}/users", response_model=List[UserSchema])
def list_organization_users(
    organization_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List users in an organization.
    - Admins can see users in any organization
    - Regular users can only see users in their organization
    """
    # Check access
    if (current_user.role != "global_admin" and
        str(organization_id) != str(current_user.organization_id)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    organization = db.query(Organization).filter(
        Organization.id == organization_id
    ).first()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    users = db.query(User).filter(
        User.organization_id == organization_id
    ).offset(skip).limit(limit).all()

    return [UserSchema.from_orm(u) for u in users]
