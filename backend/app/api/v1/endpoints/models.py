from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.models.user import User
from app.models.economic_model import EconomicModel
from app.models.parameter import Parameter
from app.core.permissions import (
    get_current_user,
    require_global_admin,
    require_local_user_or_admin,
)
from app.schemas import (
    Model,
    ModelCreate,
    ModelUpdate,
    ModelWithStats,
    ModelPublish,
    Parameter as ParameterSchema,
)
import hashlib

router = APIRouter()


@router.get("/", response_model=List[ModelWithStats])
def list_models(
    skip: int = 0,
    limit: int = 100,
    show_unpublished: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List economic models.
    - Regular users only see published models
    - Admins can see all models with show_unpublished=true
    """
    query = db.query(EconomicModel)

    # Non-admins only see published models
    if current_user.role != "global_admin" or not show_unpublished:
        query = query.filter(EconomicModel.is_published == True)

    models = query.offset(skip).limit(limit).all()

    # Add stats
    result = []
    for model in models:
        model_dict = Model.from_orm(model).model_dump()
        model_dict["parameter_count"] = len(model.parameters)
        model_dict["scenario_count"] = len(model.scenarios)

        # Get creator name
        if model.created_by:
            model_dict["created_by_name"] = model.created_by.full_name

        result.append(ModelWithStats(**model_dict))

    return result


@router.post("/", response_model=Model, status_code=status.HTTP_201_CREATED)
def create_model(
    model_data: ModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_global_admin),
):
    """Create a new economic model. Admin only."""
    # Calculate script hash if script provided
    script_hash = None
    if model_data.script_content:
        script_hash = hashlib.sha256(model_data.script_content.encode()).hexdigest()

    model = EconomicModel(
        **model_data.dict(exclude={"script_content"}),
        script_content=model_data.script_content,
        script_hash=script_hash,
        created_by_id=current_user.id,
        is_published=False,  # New models start unpublished
    )

    db.add(model)
    db.commit()
    db.refresh(model)

    return Model.from_orm(model)


@router.get("/{model_id}", response_model=ModelWithStats)
def get_model(
    model_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific model by ID"""
    model = db.query(EconomicModel).filter(EconomicModel.id == model_id).first()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    # Non-admins can only see published models
    if current_user.role != "global_admin" and not model.is_published:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Model not published.",
        )

    # Build response with stats
    model_dict = Model.from_orm(model).model_dump()
    model_dict["parameter_count"] = len(model.parameters)
    model_dict["scenario_count"] = len(model.scenarios)

    if model.created_by:
        model_dict["created_by_name"] = model.created_by.full_name

    return ModelWithStats(**model_dict)


@router.patch("/{model_id}", response_model=Model)
def update_model(
    model_id: UUID,
    model_data: ModelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_global_admin),
):
    """Update a model. Admin only."""
    model = db.query(EconomicModel).filter(EconomicModel.id == model_id).first()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    # Update fields
    update_data = model_data.dict(exclude_unset=True)

    # Recalculate hash if script changed
    if "script_content" in update_data and update_data["script_content"]:
        update_data["script_hash"] = hashlib.sha256(
            update_data["script_content"].encode()
        ).hexdigest()

    for field, value in update_data.items():
        setattr(model, field, value)

    db.commit()
    db.refresh(model)

    return Model.from_orm(model)


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model(
    model_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_global_admin),
):
    """
    Soft delete a model (unpublish it). Admin only.
    We don't hard delete to preserve referential integrity.
    """
    model = db.query(EconomicModel).filter(EconomicModel.id == model_id).first()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    # Soft delete: just unpublish
    model.is_published = False
    db.commit()

    return None


@router.post("/{model_id}/publish", response_model=Model)
def publish_model(
    model_id: UUID,
    publish_data: ModelPublish,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_global_admin),
):
    """Publish or unpublish a model. Admin only."""
    model = db.query(EconomicModel).filter(EconomicModel.id == model_id).first()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    # Check if model has parameters before publishing
    if publish_data.is_published and len(model.parameters) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot publish model without parameters",
        )

    model.is_published = publish_data.is_published
    db.commit()
    db.refresh(model)

    return Model.from_orm(model)


@router.get("/{model_id}/parameters", response_model=List[ParameterSchema])
def get_model_parameters(
    model_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all parameters for a specific model"""
    model = db.query(EconomicModel).filter(EconomicModel.id == model_id).first()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    # Non-admins can only see published models
    if current_user.role != "global_admin" and not model.is_published:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Model not published.",
        )

    # Return parameters sorted by display_order
    parameters = sorted(model.parameters, key=lambda p: p.display_order)

    return [ParameterSchema.from_orm(p) for p in parameters]
