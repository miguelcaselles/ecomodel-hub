from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole
from typing import List

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user


def require_role(allowed_roles: List[UserRole]):
    """Decorator to require specific roles"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required roles: {[r.value for r in allowed_roles]}",
            )
        return current_user
    return role_checker


# Convenience dependencies
require_global_admin = require_role([UserRole.GLOBAL_ADMIN])
require_local_user_or_admin = require_role([UserRole.LOCAL_USER, UserRole.GLOBAL_ADMIN])


def require_organization_access(resource_attr: str = "organization_id"):
    """
    Decorator to ensure user can only access resources from their organization.
    Global admins bypass this check.

    Args:
        resource_attr: Name of the attribute containing organization_id on the resource
    """
    def checker(
        resource,
        current_user: User = Depends(get_current_user)
    ):
        # Global admins can access all organizations
        if current_user.role == UserRole.GLOBAL_ADMIN:
            return resource

        # Get organization_id from resource
        resource_org_id = getattr(resource, resource_attr, None)

        if resource_org_id is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Resource does not have {resource_attr} attribute",
            )

        # Check if user belongs to same organization
        if str(resource_org_id) != str(current_user.organization_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Resource belongs to different organization.",
            )

        return resource

    return checker


def filter_by_organization(query, model, current_user: User):
    """
    Filter a SQLAlchemy query to only return resources from user's organization.
    Global admins see all resources.

    Args:
        query: SQLAlchemy query object
        model: Model class being queried (must have organization_id attribute)
        current_user: Current authenticated user

    Returns:
        Filtered query
    """
    if current_user.role == UserRole.GLOBAL_ADMIN:
        return query

    if not hasattr(model, 'organization_id'):
        raise ValueError(f"Model {model.__name__} does not have organization_id attribute")

    return query.filter(model.organization_id == current_user.organization_id)


def can_edit_resource(resource, current_user: User, resource_attr: str = "created_by_id") -> bool:
    """
    Check if user can edit a resource.
    Rules:
    - Global admins can edit anything
    - Local users can edit resources they created in their organization
    - Viewers cannot edit

    Args:
        resource: The resource object
        current_user: Current authenticated user
        resource_attr: Attribute name for creator ID (default: created_by_id)

    Returns:
        bool: True if user can edit, False otherwise
    """
    # Global admins can edit everything
    if current_user.role == UserRole.GLOBAL_ADMIN:
        return True

    # Viewers cannot edit
    if current_user.role == UserRole.VIEWER:
        return False

    # Check organization access
    if hasattr(resource, 'organization_id'):
        if str(resource.organization_id) != str(current_user.organization_id):
            return False

    # Local users can edit their own resources
    if hasattr(resource, resource_attr):
        creator_id = getattr(resource, resource_attr)
        return str(creator_id) == str(current_user.id)

    return False
