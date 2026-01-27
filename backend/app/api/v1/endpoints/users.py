from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.models.user import User
from app.models.organization import Organization
from app.core.permissions import (
    get_current_user,
    require_global_admin,
)
from app.core.security import get_password_hash
from app.schemas import (
    User as UserSchema,
    UserCreate,
    UserUpdate,
    UserMe,
    UserWithOrganization,
)

router = APIRouter()


@router.get("/", response_model=List[UserWithOrganization])
def list_users(
    skip: int = 0,
    limit: int = 100,
    organization_id: UUID | None = None,
    role: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_global_admin),
):
    """
    List all users. Admin only.
    Optional filters: organization_id, role
    """
    query = db.query(User)

    if organization_id:
        query = query.filter(User.organization_id == organization_id)

    if role:
        query = query.filter(User.role == role)

    users = query.offset(skip).limit(limit).all()

    # Build response with organization details
    result = []
    for user in users:
        user_dict = UserSchema.from_orm(user).model_dump()

        if user.organization:
            user_dict["organization_name"] = user.organization.name
            user_dict["organization_country"] = user.organization.country

        result.append(UserWithOrganization(**user_dict))

    return result


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_global_admin),
):
    """Create a new user. Admin only."""
    # Check if email already exists
    existing = db.query(User).filter(User.email == user_data.email).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Verify organization exists
    organization = db.query(Organization).filter(
        Organization.id == user_data.organization_id
    ).first()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Hash password
    hashed_password = get_password_hash(user_data.password)

    # Create user
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        role=user_data.role,
        password_hash=hashed_password,
        organization_id=user_data.organization_id,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return UserSchema.from_orm(user)


@router.get("/me", response_model=UserMe)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """Get current user's profile"""
    return UserMe.from_orm(current_user)


@router.get("/{user_id}", response_model=UserWithOrganization)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific user.
    - Admins can get any user
    - Users can only get themselves or users from their organization
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check access
    if current_user.role != "global_admin":
        # Users can only see themselves or users in their org
        if (str(user.id) != str(current_user.id) and
            str(user.organization_id) != str(current_user.organization_id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

    # Build response with organization details
    user_dict = UserSchema.from_orm(user).model_dump()

    if user.organization:
        user_dict["organization_name"] = user.organization.name
        user_dict["organization_country"] = user.organization.country

    return UserWithOrganization(**user_dict)


@router.patch("/{user_id}", response_model=UserSchema)
def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a user.
    - Admins can update any user
    - Users can only update themselves (limited fields)
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check permissions
    is_self = str(user.id) == str(current_user.id)
    is_admin = current_user.role == "global_admin"

    if not is_self and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Non-admins can only update limited fields
    if not is_admin:
        # Only allow updating own full_name and password
        if user_data.role or user_data.organization_id or user_data.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your full_name and password",
            )

    # Check if email is being changed and if it conflicts
    if user_data.email and user_data.email != user.email:
        existing = db.query(User).filter(User.email == user_data.email).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    # Verify new organization exists if being changed
    if user_data.organization_id:
        organization = db.query(Organization).filter(
            Organization.id == user_data.organization_id
        ).first()

        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )

    # Update fields
    update_data = user_data.dict(exclude_unset=True, exclude={"password"})

    for field, value in update_data.items():
        setattr(user, field, value)

    # Update password if provided
    if user_data.password:
        user.password_hash = get_password_hash(user_data.password)

    db.commit()
    db.refresh(user)

    return UserSchema.from_orm(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_global_admin),
):
    """
    Deactivate a user (soft delete). Admin only.
    We don't hard delete to preserve audit trail.
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Don't allow deactivating self
    if str(user.id) == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account",
        )

    user.is_active = False
    db.commit()

    return None
