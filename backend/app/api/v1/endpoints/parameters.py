from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.models.user import User
from app.models.parameter import Parameter
from app.models.economic_model import EconomicModel
from app.core.permissions import (
    get_current_user,
    require_global_admin,
)
from app.schemas import (
    Parameter as ParameterSchema,
    ParameterCreate,
    ParameterUpdate,
    ParameterBulkCreate,
    ParameterWithModel,
)

router = APIRouter()


@router.get("/", response_model=List[ParameterWithModel])
def list_parameters(
    skip: int = 0,
    limit: int = 100,
    model_id: UUID | None = None,
    category: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List parameters with optional filters"""
    query = db.query(Parameter)

    if model_id:
        query = query.filter(Parameter.model_id == model_id)

    if category:
        query = query.filter(Parameter.category == category)

    # Order by display_order
    query = query.order_by(Parameter.display_order)

    parameters = query.offset(skip).limit(limit).all()

    # Build response with model details
    result = []
    for param in parameters:
        param_dict = ParameterSchema.from_orm(param).model_dump()

        if param.model:
            param_dict["model_name"] = param.model.name

        result.append(ParameterWithModel(**param_dict))

    return result


@router.post("/", response_model=ParameterSchema, status_code=status.HTTP_201_CREATED)
def create_parameter(
    parameter_data: ParameterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_global_admin),
):
    """Create a new parameter. Admin only."""
    # Verify model exists
    model = db.query(EconomicModel).filter(
        EconomicModel.id == parameter_data.model_id
    ).first()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Economic model not found",
        )

    # Check if parameter name already exists in this model
    existing = db.query(Parameter).filter(
        Parameter.model_id == parameter_data.model_id,
        Parameter.name == parameter_data.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Parameter '{parameter_data.name}' already exists in this model",
        )

    parameter = Parameter(**parameter_data.model_dump())

    db.add(parameter)
    db.commit()
    db.refresh(parameter)

    return ParameterSchema.from_orm(parameter)


@router.post("/bulk", response_model=List[ParameterSchema], status_code=status.HTTP_201_CREATED)
def create_parameters_bulk(
    bulk_data: ParameterBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_global_admin),
):
    """Create multiple parameters at once. Admin only."""
    # Verify model exists
    model = db.query(EconomicModel).filter(
        EconomicModel.id == bulk_data.model_id
    ).first()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Economic model not found",
        )

    # Check for duplicate names in request
    param_names = [p.name for p in bulk_data.parameters]
    if len(param_names) != len(set(param_names)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate parameter names in request",
        )

    # Check for existing names in DB
    existing_names = db.query(Parameter.name).filter(
        Parameter.model_id == bulk_data.model_id,
        Parameter.name.in_(param_names)
    ).all()

    if existing_names:
        existing = [name[0] for name in existing_names]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Parameters already exist: {existing}",
        )

    # Create all parameters
    created_params = []
    for param_data in bulk_data.parameters:
        parameter = Parameter(
            **param_data.model_dump(),
            model_id=bulk_data.model_id
        )
        db.add(parameter)
        created_params.append(parameter)

    db.commit()

    # Refresh all
    for param in created_params:
        db.refresh(param)

    return [ParameterSchema.from_orm(p) for p in created_params]


@router.get("/{parameter_id}", response_model=ParameterWithModel)
def get_parameter(
    parameter_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific parameter"""
    parameter = db.query(Parameter).filter(Parameter.id == parameter_id).first()

    if not parameter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parameter not found",
        )

    # Build response with model details
    param_dict = ParameterSchema.from_orm(parameter).model_dump()

    if parameter.model:
        param_dict["model_name"] = parameter.model.name

    return ParameterWithModel(**param_dict)


@router.patch("/{parameter_id}", response_model=ParameterSchema)
def update_parameter(
    parameter_id: UUID,
    parameter_data: ParameterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_global_admin),
):
    """Update a parameter. Admin only."""
    parameter = db.query(Parameter).filter(Parameter.id == parameter_id).first()

    if not parameter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parameter not found",
        )

    # Check if name is being changed and if it conflicts
    if parameter_data.name and parameter_data.name != parameter.name:
        existing = db.query(Parameter).filter(
            Parameter.model_id == parameter.model_id,
            Parameter.name == parameter_data.name
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Parameter '{parameter_data.name}' already exists in this model",
            )

    # Update fields
    update_data = parameter_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(parameter, field, value)

    db.commit()
    db.refresh(parameter)

    return ParameterSchema.from_orm(parameter)


@router.delete("/{parameter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_parameter(
    parameter_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_global_admin),
):
    """
    Delete a parameter. Admin only.
    Note: This may affect existing scenarios that reference this parameter.
    """
    parameter = db.query(Parameter).filter(Parameter.id == parameter_id).first()

    if not parameter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parameter not found",
        )

    # Check if model is published
    if parameter.model.is_published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete parameters from published model. Unpublish first.",
        )

    db.delete(parameter)
    db.commit()

    return None
