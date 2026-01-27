from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.session import get_db
from app.core.permissions import get_current_user
from app.schemas.simulation import SimulationRequest, SimulationResponse
from app.models.user import User
from app.models.simulation import Simulation, SimulationType, SimulationStatus
from app.models.scenario import Scenario
from engine.markov.core import run_markov_analysis
from engine.sensitivity.deterministic import tornado_analysis
from engine.sensitivity.probabilistic import run_psa
from datetime import datetime
import time

router = APIRouter()


@router.post("/deterministic", response_model=SimulationResponse)
async def run_deterministic_simulation(
    request: SimulationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Run deterministic (base case) simulation
    """
    # Get scenario
    scenario = db.query(Scenario).filter(Scenario.id == request.scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Check permissions (user must belong to same organization or be admin)
    if current_user.role != "global_admin" and current_user.organization_id != scenario.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Create simulation record
    simulation = Simulation(
        scenario_id=request.scenario_id,
        simulation_type=SimulationType.DETERMINISTIC,
        status=SimulationStatus.RUNNING,
        input_snapshot=scenario.parameter_values,
        created_by_id=current_user.id
    )
    db.add(simulation)
    db.commit()
    db.refresh(simulation)

    try:
        # Run Markov model
        start_time = time.time()
        results = run_markov_analysis(scenario.parameter_values)
        execution_time = int((time.time() - start_time) * 1000)

        # Update simulation with results
        simulation.status = SimulationStatus.COMPLETED
        simulation.results = results
        simulation.execution_time_ms = execution_time
        simulation.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(simulation)

    except Exception as e:
        simulation.status = SimulationStatus.FAILED
        simulation.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

    return SimulationResponse.from_orm(simulation)


@router.post("/tornado", response_model=SimulationResponse)
async def run_tornado_analysis_endpoint(
    request: SimulationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Run tornado diagram (one-way sensitivity) analysis
    """
    scenario = db.query(Scenario).filter(Scenario.id == request.scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Create simulation record
    simulation = Simulation(
        scenario_id=request.scenario_id,
        simulation_type=SimulationType.TORNADO,
        status=SimulationStatus.RUNNING,
        input_snapshot=scenario.parameter_values,
        created_by_id=current_user.id
    )
    db.add(simulation)
    db.commit()
    db.refresh(simulation)

    try:
        # Define parameter ranges for sensitivity analysis
        base_params = scenario.parameter_values
        param_ranges = {
            "cost_drug_a": (base_params.get("cost_drug_a", 3500) * 0.8, base_params.get("cost_drug_a", 3500) * 1.2),
            "cost_drug_b": (base_params.get("cost_drug_b", 500) * 0.8, base_params.get("cost_drug_b", 500) * 1.2),
            "prob_s_to_p_a": (base_params.get("prob_s_to_p_a", 0.10) * 0.8, base_params.get("prob_s_to_p_a", 0.10) * 1.2),
            "prob_s_to_p_b": (base_params.get("prob_s_to_p_b", 0.25) * 0.8, base_params.get("prob_s_to_p_b", 0.25) * 1.2),
        }

        start_time = time.time()
        tornado_results = tornado_analysis(base_params, param_ranges)
        execution_time = int((time.time() - start_time) * 1000)

        # Also run base case
        base_results = run_markov_analysis(base_params)

        simulation.status = SimulationStatus.COMPLETED
        simulation.results = base_results
        simulation.sensitivity_results = {"tornado": tornado_results}
        simulation.execution_time_ms = execution_time
        simulation.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(simulation)

    except Exception as e:
        simulation.status = SimulationStatus.FAILED
        simulation.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

    return SimulationResponse.from_orm(simulation)


@router.post("/psa", response_model=SimulationResponse)
async def run_psa_simulation(
    request: SimulationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Run Probabilistic Sensitivity Analysis (Monte Carlo)
    Note: In production, this should use Celery for async processing
    """
    scenario = db.query(Scenario).filter(Scenario.id == request.scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    iterations = request.iterations or 1000

    # Create simulation record
    simulation = Simulation(
        scenario_id=request.scenario_id,
        simulation_type=SimulationType.PSA,
        status=SimulationStatus.RUNNING,
        input_snapshot=scenario.parameter_values,
        created_by_id=current_user.id
    )
    db.add(simulation)
    db.commit()
    db.refresh(simulation)

    try:
        # Define distributions for PSA
        distributions = {
            "cost_drug_a": {"type": "gamma", "shape": 10, "scale": scenario.parameter_values.get("cost_drug_a", 3500) / 10},
            "prob_s_to_p_a": {"type": "beta", "alpha": 10, "beta": 90},
            "utility_stable": {"type": "beta", "alpha": 85, "beta": 15},
            "utility_progression": {"type": "beta", "alpha": 50, "beta": 50},
        }

        start_time = time.time()
        psa_results = run_psa(
            scenario.parameter_values,
            distributions,
            n_iterations=iterations,
            seed=request.seed
        )
        execution_time = int((time.time() - start_time) * 1000)

        # Also run base case
        base_results = run_markov_analysis(scenario.parameter_values)

        simulation.status = SimulationStatus.COMPLETED
        simulation.results = base_results
        simulation.sensitivity_results = {"psa": psa_results}
        simulation.execution_time_ms = execution_time
        simulation.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(simulation)

    except Exception as e:
        simulation.status = SimulationStatus.FAILED
        simulation.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

    return SimulationResponse.from_orm(simulation)


@router.get("/{simulation_id}", response_model=SimulationResponse)
async def get_simulation(
    simulation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get simulation results by ID
    """
    simulation = db.query(Simulation).filter(Simulation.id == simulation_id).first()
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    return SimulationResponse.from_orm(simulation)
