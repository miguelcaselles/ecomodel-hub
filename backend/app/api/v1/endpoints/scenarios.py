from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.models.user import User
from app.models.scenario import Scenario
from app.models.economic_model import EconomicModel
from app.core.permissions import (
    get_current_user,
    filter_by_organization,
    can_edit_resource,
)
from app.schemas import (
    Scenario as ScenarioSchema,
    ScenarioCreate,
    ScenarioUpdate,
    ScenarioClone,
    ScenarioWithDetails,
)

router = APIRouter()


@router.get("/", response_model=List[ScenarioWithDetails])
def list_scenarios(
    skip: int = 0,
    limit: int = 100,
    model_id: UUID | None = None,
    country_code: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List scenarios filtered by user's organization.
    Admins see all scenarios.
    """
    query = db.query(Scenario)

    # Filter by organization (admins see all)
    query = filter_by_organization(query, Scenario, current_user)

    # Apply optional filters
    if model_id:
        query = query.filter(Scenario.model_id == model_id)

    if country_code:
        query = query.filter(Scenario.country_code == country_code)

    scenarios = query.offset(skip).limit(limit).all()

    # Build response with details
    result = []
    for scenario in scenarios:
        scenario_dict = ScenarioSchema.from_orm(scenario).model_dump()

        # Add related entity details
        if scenario.model:
            scenario_dict["model_name"] = scenario.model.name

        if scenario.organization:
            scenario_dict["organization_name"] = scenario.organization.name

        if scenario.created_by_user:
            scenario_dict["created_by_name"] = scenario.created_by_user.full_name

        scenario_dict["simulation_count"] = len(scenario.simulations)

        result.append(ScenarioWithDetails(**scenario_dict))

    return result


@router.post("/", response_model=ScenarioSchema, status_code=status.HTTP_201_CREATED)
def create_scenario(
    scenario_data: ScenarioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new scenario. Users can only create for their organization."""
    # Verify model exists and is published
    model = db.query(EconomicModel).filter(
        EconomicModel.id == scenario_data.model_id
    ).first()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Economic model not found",
        )

    if not model.is_published and current_user.role != "global_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create scenario from unpublished model",
        )

    # Validate parameter values against model parameters
    model_param_names = {p.name for p in model.parameters}
    scenario_param_names = set(scenario_data.parameter_values.keys())

    if not scenario_param_names.issubset(model_param_names):
        invalid_params = scenario_param_names - model_param_names
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameters: {invalid_params}",
        )

    scenario = Scenario(
        **scenario_data.dict(exclude={"model_id"}),
        model_id=scenario_data.model_id,
        organization_id=current_user.organization_id,
        created_by_id=current_user.id,
        is_locked=False,
    )

    db.add(scenario)
    db.commit()
    db.refresh(scenario)

    return ScenarioSchema.from_orm(scenario)


@router.get("/{scenario_id}", response_model=ScenarioWithDetails)
def get_scenario(
    scenario_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific scenario"""
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found",
        )

    # Check organization access
    if (current_user.role != "global_admin" and
        str(scenario.organization_id) != str(current_user.organization_id)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Scenario belongs to different organization.",
        )

    # Build response with details
    scenario_dict = ScenarioSchema.from_orm(scenario).model_dump()

    if scenario.model:
        scenario_dict["model_name"] = scenario.model.name

    if scenario.organization:
        scenario_dict["organization_name"] = scenario.organization.name

    if scenario.created_by_user:
        scenario_dict["created_by_name"] = scenario.created_by_user.full_name

    scenario_dict["simulation_count"] = len(scenario.simulations)

    return ScenarioWithDetails(**scenario_dict)


@router.patch("/{scenario_id}", response_model=ScenarioSchema)
def update_scenario(
    scenario_id: UUID,
    scenario_data: ScenarioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a scenario.
    Users can only edit their own scenarios in their organization.
    Admins can edit any scenario.
    """
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found",
        )

    # Check if locked
    if scenario.is_locked and current_user.role != "global_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Scenario is locked and cannot be edited",
        )

    # Check edit permissions
    if not can_edit_resource(scenario, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. You can only edit scenarios you created.",
        )

    # Validate parameter values if provided
    if scenario_data.parameter_values is not None:
        model_param_names = {p.name for p in scenario.model.parameters}
        scenario_param_names = set(scenario_data.parameter_values.keys())

        if not scenario_param_names.issubset(model_param_names):
            invalid_params = scenario_param_names - model_param_names
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid parameters: {invalid_params}",
            )

    # Update fields
    update_data = scenario_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(scenario, field, value)

    db.commit()
    db.refresh(scenario)

    return ScenarioSchema.from_orm(scenario)


@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scenario(
    scenario_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a scenario.
    Users can only delete their own scenarios.
    Admins can delete any scenario.
    """
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found",
        )

    # Check if locked
    if scenario.is_locked and current_user.role != "global_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Scenario is locked and cannot be deleted",
        )

    # Check delete permissions
    if not can_edit_resource(scenario, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. You can only delete scenarios you created.",
        )

    # Check if scenario has simulations
    if len(scenario.simulations) > 0 and current_user.role != "global_admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete scenario with existing simulations",
        )

    db.delete(scenario)
    db.commit()

    return None


@router.post("/{scenario_id}/clone", response_model=ScenarioSchema, status_code=status.HTTP_201_CREATED)
def clone_scenario(
    scenario_id: UUID,
    clone_data: ScenarioClone,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Clone an existing scenario with a new name.
    Users can clone scenarios from their organization.
    """
    original = db.query(Scenario).filter(Scenario.id == scenario_id).first()

    if not original:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found",
        )

    # Check organization access
    if (current_user.role != "global_admin" and
        str(original.organization_id) != str(current_user.organization_id)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Cannot clone scenario from different organization.",
        )

    # Create clone
    cloned = Scenario(
        name=clone_data.name,
        description=clone_data.description or f"Cloned from {original.name}",
        model_id=original.model_id,
        organization_id=current_user.organization_id,  # Always user's org
        created_by_id=current_user.id,
        country_code=original.country_code,
        parameter_values=original.parameter_values.copy(),  # Deep copy parameters
        is_base_case=False,  # Clones are never base case
        is_locked=False,
    )

    db.add(cloned)
    db.commit()
    db.refresh(cloned)

    return ScenarioSchema.from_orm(cloned)
