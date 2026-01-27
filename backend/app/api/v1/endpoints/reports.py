"""
Reports API endpoints
Handles PDF and Excel report generation
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.permissions import get_current_user
from app.models.user import User
from app.models.scenario import Scenario
from app.models.simulation import Simulation
from app.services.report_service import report_service

router = APIRouter()


@router.post("/pdf/{simulation_id}")
def generate_pdf_report(
    simulation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate PDF report for a simulation

    Returns PDF file as download
    """
    # Get simulation
    simulation = db.query(Simulation).filter(Simulation.id == simulation_id).first()
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    # Check permission
    scenario = db.query(Scenario).filter(Scenario.id == simulation.scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    if current_user.role != "global_admin" and scenario.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Prepare data
    scenario_name = scenario.name
    organization = current_user.organization.name if current_user.organization else "N/A"
    parameters = simulation.input_snapshot or scenario.parameter_values

    # Get results
    results = simulation.results or {}

    # Extract drug A and drug B results
    # Assuming results structure has both strategies
    results_drug_a = {
        'total_costs': results.get('drug_a', {}).get('total_costs', 0),
        'total_qalys': results.get('drug_a', {}).get('total_qalys', 0),
        'life_years': results.get('drug_a', {}).get('life_years', 0),
        'discounted_costs': results.get('drug_a', {}).get('discounted_costs', 0),
        'discounted_qalys': results.get('drug_a', {}).get('discounted_qalys', 0),
    }

    results_drug_b = {
        'total_costs': results.get('drug_b', {}).get('total_costs', 0),
        'total_qalys': results.get('drug_b', {}).get('total_qalys', 0),
        'life_years': results.get('drug_b', {}).get('life_years', 0),
        'discounted_costs': results.get('drug_b', {}).get('discounted_costs', 0),
        'discounted_qalys': results.get('drug_b', {}).get('discounted_qalys', 0),
    }

    # PSA results if available
    psa_results = None
    if simulation.simulation_type == "PSA" and simulation.sensitivity_results:
        psa_results = {
            'mean_icer': simulation.sensitivity_results.get('mean_icer', 0),
            'percentiles': {
                'p2_5': simulation.sensitivity_results.get('percentiles', {}).get('p2_5', 0),
                'p50': simulation.sensitivity_results.get('percentiles', {}).get('p50', 0),
                'p97_5': simulation.sensitivity_results.get('percentiles', {}).get('p97_5', 0),
            },
            'prob_cost_effective': simulation.sensitivity_results.get('prob_cost_effective', 0),
            'n_iterations': simulation.sensitivity_results.get('n_iterations', 1000),
        }

    # Generate PDF
    try:
        pdf_bytes = report_service.generate_pdf_report(
            scenario_name=scenario_name,
            user_email=current_user.email,
            organization=organization,
            parameters=parameters,
            results_drug_a=results_drug_a,
            results_drug_b=results_drug_b,
            psa_results=psa_results
        )

        # Return PDF as download
        filename = f"ecomodel_report_{scenario.name.replace(' ', '_')}_{simulation_id[:8]}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


@router.post("/excel/{simulation_id}")
def generate_excel_report(
    simulation_id: str,
    include_psa: bool = False,
    include_tornado: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate Excel report for a simulation

    Args:
        simulation_id: ID of simulation
        include_psa: Include PSA sheet if available
        include_tornado: Include Tornado sheet if available

    Returns Excel file as download
    """
    # Get simulation
    simulation = db.query(Simulation).filter(Simulation.id == simulation_id).first()
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    # Check permission
    scenario = db.query(Scenario).filter(Scenario.id == simulation.scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    if current_user.role != "global_admin" and scenario.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Prepare data
    scenario_name = scenario.name
    parameters = simulation.input_snapshot or scenario.parameter_values

    # Get results
    results = simulation.results or {}

    results_drug_a = {
        'total_costs': results.get('drug_a', {}).get('total_costs', 0),
        'total_qalys': results.get('drug_a', {}).get('total_qalys', 0),
        'life_years': results.get('drug_a', {}).get('life_years', 0),
        'discounted_costs': results.get('drug_a', {}).get('discounted_costs', 0),
        'discounted_qalys': results.get('drug_a', {}).get('discounted_qalys', 0),
    }

    results_drug_b = {
        'total_costs': results.get('drug_b', {}).get('total_costs', 0),
        'total_qalys': results.get('drug_b', {}).get('total_qalys', 0),
        'life_years': results.get('drug_b', {}).get('life_years', 0),
        'discounted_costs': results.get('drug_b', {}).get('discounted_costs', 0),
        'discounted_qalys': results.get('drug_b', {}).get('discounted_qalys', 0),
    }

    # Optional results
    psa_results = None
    tornado_results = None

    if include_psa and simulation.simulation_type == "PSA" and simulation.sensitivity_results:
        psa_results = {
            'mean_icer': simulation.sensitivity_results.get('mean_icer', 0),
            'percentiles': {
                'p2_5': simulation.sensitivity_results.get('percentiles', {}).get('p2_5', 0),
                'p50': simulation.sensitivity_results.get('percentiles', {}).get('p50', 0),
                'p97_5': simulation.sensitivity_results.get('percentiles', {}).get('p97_5', 0),
            },
            'prob_cost_effective': simulation.sensitivity_results.get('prob_cost_effective', 0),
            'n_iterations': simulation.sensitivity_results.get('n_iterations', 1000),
        }

    if include_tornado and simulation.simulation_type == "TORNADO" and simulation.sensitivity_results:
        tornado_results = simulation.sensitivity_results

    # Generate Excel
    try:
        excel_bytes = report_service.generate_excel_report(
            scenario_name=scenario_name,
            user_email=current_user.email,
            parameters=parameters,
            results_drug_a=results_drug_a,
            results_drug_b=results_drug_b,
            psa_results=psa_results,
            tornado_results=tornado_results
        )

        # Return Excel as download
        filename = f"ecomodel_report_{scenario.name.replace(' ', '_')}_{simulation_id[:8]}.xlsx"
        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Excel: {str(e)}")


@router.post("/pdf/scenario/{scenario_id}")
def generate_pdf_from_scenario(
    scenario_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate PDF report from scenario's last simulation

    If no simulation exists, runs deterministic analysis first
    """
    # Get scenario
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Check permission
    if current_user.role != "global_admin" and scenario.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get most recent simulation for this scenario
    simulation = db.query(Simulation)\
        .filter(Simulation.scenario_id == scenario_id)\
        .filter(Simulation.status == "COMPLETED")\
        .order_by(Simulation.created_at.desc())\
        .first()

    if not simulation:
        raise HTTPException(
            status_code=404,
            detail="No completed simulation found for this scenario. Please run an analysis first."
        )

    # Redirect to simulation PDF endpoint
    return generate_pdf_report(simulation.id, db, current_user)
