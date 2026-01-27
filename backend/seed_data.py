"""
Seed demo data for EcoModel Hub
Creates organizations, users, economic model, and sample scenarios
"""
import sys
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.base import Base
from app.models import User, Organization, EconomicModel, Parameter, Scenario
from app.models.user import UserRole
from app.models.economic_model import ModelType
from app.models.parameter import DataType, InputType
from app.core.security import get_password_hash
import uuid


def seed_database():
    db: Session = SessionLocal()

    try:
        print("🌱 Seeding database...")

        # Create Organizations
        org_spain = Organization(
            name="Hospital Vall d'Hebron",
            country="ES",
            settings={}
        )
        org_germany = Organization(
            name="Charité Universitätsmedizin",
            country="DE",
            settings={}
        )
        db.add_all([org_spain, org_germany])
        db.commit()
        print("✓ Organizations created")

        # Create Users
        admin_user = User(
            email="admin@ecomodel.com",
            password_hash=get_password_hash("admin123"),
            full_name="Global Administrator",
            role=UserRole.GLOBAL_ADMIN,
            is_active=True
        )

        spain_user = User(
            email="spain@ecomodel.com",
            password_hash=get_password_hash("spain123"),
            full_name="Maria Garcia",
            role=UserRole.LOCAL_USER,
            organization_id=org_spain.id,
            is_active=True
        )

        germany_user = User(
            email="germany@ecomodel.com",
            password_hash=get_password_hash("germany123"),
            full_name="Hans Mueller",
            role=UserRole.LOCAL_USER,
            organization_id=org_germany.id,
            is_active=True
        )

        viewer_user = User(
            email="viewer@ecomodel.com",
            password_hash=get_password_hash("viewer123"),
            full_name="Investor Viewer",
            role=UserRole.VIEWER,
            is_active=True
        )

        db.add_all([admin_user, spain_user, germany_user, viewer_user])
        db.commit()
        print("✓ Users created")
        print(f"  - Admin: admin@ecomodel.com / admin123")
        print(f"  - Spain User: spain@ecomodel.com / spain123")
        print(f"  - Germany User: germany@ecomodel.com / germany123")
        print(f"  - Viewer: viewer@ecomodel.com / viewer123")

        # Create Economic Model (Oncology)
        oncology_model = EconomicModel(
            name="Oncology Treatment Model",
            description="Three-state Markov model comparing new oncology drug vs standard therapy",
            model_type=ModelType.MARKOV,
            config={
                "cycle_length": 1,
                "time_horizon": 10,
                "discount_rate_costs": 0.03,
                "discount_rate_outcomes": 0.03,
                "currency": "EUR",
                "states": ["Stable", "Progression", "Death"],
                "comparators": ["Drug_A_New", "Drug_B_Standard"]
            },
            version=1,
            is_published=True,
            created_by_id=admin_user.id
        )
        db.add(oncology_model)
        db.commit()
        print("✓ Economic model created")

        # Create Parameters
        parameters = [
            # General Parameters
            Parameter(
                model_id=oncology_model.id,
                name="time_horizon",
                display_name="Time Horizon (Years)",
                description="Duration of the analysis",
                category="General",
                data_type=DataType.INT,
                input_type=InputType.NUMBER,
                default_value=10,
                constraints={"min": 1, "max": 50, "step": 1},
                display_order=1,
                unit="years",
                is_editable_by_local=False
            ),
            Parameter(
                model_id=oncology_model.id,
                name="discount_rate",
                display_name="Discount Rate",
                description="Annual discount rate for costs and outcomes",
                category="General",
                data_type=DataType.PERCENTAGE,
                input_type=InputType.SLIDER,
                default_value=0.03,
                constraints={"min": 0.00, "max": 0.10, "step": 0.01},
                display_order=2,
                unit="%",
                is_editable_by_local=True
            ),
            Parameter(
                model_id=oncology_model.id,
                name="cohort_size",
                display_name="Cohort Size",
                description="Number of patients in simulation",
                category="General",
                data_type=DataType.INT,
                input_type=InputType.NUMBER,
                default_value=1000,
                constraints={"min": 100, "max": 10000, "step": 100},
                display_order=3,
                unit="patients",
                is_editable_by_local=False
            ),

            # Cost Parameters
            Parameter(
                model_id=oncology_model.id,
                name="cost_drug_a",
                display_name="Drug A Annual Cost",
                description="Annual cost of new drug (Drug A)",
                category="Costs",
                data_type=DataType.CURRENCY,
                input_type=InputType.NUMBER,
                default_value=3500.0,
                constraints={"min": 0, "max": 100000, "step": 100},
                distribution={"type": "gamma", "shape": 10, "scale": 350},
                display_order=10,
                unit="EUR",
                is_country_specific=True,
                is_editable_by_local=True
            ),
            Parameter(
                model_id=oncology_model.id,
                name="cost_drug_b",
                display_name="Drug B Annual Cost",
                description="Annual cost of standard therapy (Drug B)",
                category="Costs",
                data_type=DataType.CURRENCY,
                input_type=InputType.NUMBER,
                default_value=500.0,
                constraints={"min": 0, "max": 10000, "step": 50},
                distribution={"type": "gamma", "shape": 5, "scale": 100},
                display_order=11,
                unit="EUR",
                is_country_specific=True,
                is_editable_by_local=True
            ),
            Parameter(
                model_id=oncology_model.id,
                name="cost_state_s",
                display_name="Monitoring Cost (Stable)",
                description="Annual monitoring cost for stable patients",
                category="Costs",
                data_type=DataType.CURRENCY,
                input_type=InputType.NUMBER,
                default_value=200.0,
                constraints={"min": 0, "max": 5000, "step": 50},
                display_order=12,
                unit="EUR",
                is_country_specific=True,
                is_editable_by_local=True
            ),
            Parameter(
                model_id=oncology_model.id,
                name="cost_state_p",
                display_name="Event Cost (Progression)",
                description="Cost per progression event including hospitalization",
                category="Costs",
                data_type=DataType.CURRENCY,
                input_type=InputType.NUMBER,
                default_value=4500.0,
                constraints={"min": 0, "max": 50000, "step": 500},
                display_order=13,
                unit="EUR",
                is_country_specific=True,
                is_editable_by_local=True
            ),

            # Utilities
            Parameter(
                model_id=oncology_model.id,
                name="utility_stable",
                display_name="Utility: Stable State",
                description="Quality of life utility for stable patients",
                category="Utilities",
                data_type=DataType.FLOAT,
                input_type=InputType.SLIDER,
                default_value=0.85,
                constraints={"min": 0.0, "max": 1.0, "step": 0.01},
                distribution={"type": "beta", "alpha": 85, "beta": 15},
                display_order=20,
                unit="utility",
                is_editable_by_local=False
            ),
            Parameter(
                model_id=oncology_model.id,
                name="utility_progression",
                display_name="Utility: Progression State",
                description="Quality of life utility for progression patients",
                category="Utilities",
                data_type=DataType.FLOAT,
                input_type=InputType.SLIDER,
                default_value=0.50,
                constraints={"min": 0.0, "max": 1.0, "step": 0.01},
                distribution={"type": "beta", "alpha": 50, "beta": 50},
                display_order=21,
                unit="utility",
                is_editable_by_local=False
            ),

            # Probabilities Drug A
            Parameter(
                model_id=oncology_model.id,
                name="prob_s_to_p_a",
                display_name="Progression Rate (Drug A)",
                description="Annual probability of progressing from Stable to Progression with Drug A",
                category="Probabilities",
                data_type=DataType.PERCENTAGE,
                input_type=InputType.SLIDER,
                default_value=0.10,
                constraints={"min": 0.0, "max": 1.0, "step": 0.01},
                distribution={"type": "beta", "alpha": 10, "beta": 90},
                display_order=30,
                unit="probability",
                is_editable_by_local=False
            ),

            # Probabilities Drug B
            Parameter(
                model_id=oncology_model.id,
                name="prob_s_to_p_b",
                display_name="Progression Rate (Drug B)",
                description="Annual probability of progressing from Stable to Progression with Drug B",
                category="Probabilities",
                data_type=DataType.PERCENTAGE,
                input_type=InputType.SLIDER,
                default_value=0.25,
                constraints={"min": 0.0, "max": 1.0, "step": 0.01},
                distribution={"type": "beta", "alpha": 25, "beta": 75},
                display_order=31,
                unit="probability",
                is_editable_by_local=False
            ),

            # Mortality rates
            Parameter(
                model_id=oncology_model.id,
                name="prob_s_to_d",
                display_name="Mortality from Stable",
                description="Annual mortality rate from stable state",
                category="Probabilities",
                data_type=DataType.PERCENTAGE,
                input_type=InputType.SLIDER,
                default_value=0.02,
                constraints={"min": 0.0, "max": 0.5, "step": 0.01},
                distribution={"type": "beta", "alpha": 2, "beta": 98},
                display_order=32,
                unit="probability",
                is_editable_by_local=False
            ),
            Parameter(
                model_id=oncology_model.id,
                name="prob_p_to_d",
                display_name="Mortality from Progression",
                description="Annual mortality rate from progression state",
                category="Probabilities",
                data_type=DataType.PERCENTAGE,
                input_type=InputType.SLIDER,
                default_value=0.15,
                constraints={"min": 0.0, "max": 1.0, "step": 0.01},
                distribution={"type": "beta", "alpha": 15, "beta": 85},
                display_order=33,
                unit="probability",
                is_editable_by_local=False
            ),
        ]

        db.add_all(parameters)
        db.commit()
        print(f"✓ {len(parameters)} parameters created")

        # Create Base Scenario for Spain
        spain_scenario = Scenario(
            model_id=oncology_model.id,
            organization_id=org_spain.id,
            name="Spain Base Case",
            description="Base case scenario with Spanish pricing",
            country_code="ES",
            parameter_values={
                "time_horizon": 10,
                "discount_rate": 0.03,
                "cohort_size": 1000,
                "cost_drug_a": 3200.0,  # Spain-specific pricing
                "cost_drug_b": 450.0,
                "cost_state_s": 180.0,
                "cost_state_p": 4200.0,
                "utility_stable": 0.85,
                "utility_progression": 0.50,
                "prob_s_to_p_a": 0.10,
                "prob_s_to_p_b": 0.25,
                "prob_s_to_d": 0.02,
                "prob_p_to_d": 0.15,
            },
            is_base_case=True,
            created_by_id=spain_user.id
        )

        # Create Optimistic Scenario for Spain
        spain_optimistic = Scenario(
            model_id=oncology_model.id,
            organization_id=org_spain.id,
            name="Spain Optimistic",
            description="Optimistic scenario with negotiated pricing",
            country_code="ES",
            parameter_values={
                "time_horizon": 10,
                "discount_rate": 0.03,
                "cohort_size": 1000,
                "cost_drug_a": 2800.0,  # Discounted price
                "cost_drug_b": 450.0,
                "cost_state_s": 180.0,
                "cost_state_p": 4200.0,
                "utility_stable": 0.85,
                "utility_progression": 0.50,
                "prob_s_to_p_a": 0.08,  # Better efficacy
                "prob_s_to_p_b": 0.25,
                "prob_s_to_d": 0.02,
                "prob_p_to_d": 0.15,
            },
            created_by_id=spain_user.id
        )

        # Create Germany Scenario
        germany_scenario = Scenario(
            model_id=oncology_model.id,
            organization_id=org_germany.id,
            name="Germany Base Case",
            description="Base case scenario with German pricing",
            country_code="DE",
            parameter_values={
                "time_horizon": 10,
                "discount_rate": 0.03,
                "cohort_size": 1000,
                "cost_drug_a": 3800.0,  # Germany-specific pricing
                "cost_drug_b": 550.0,
                "cost_state_s": 220.0,
                "cost_state_p": 5000.0,
                "utility_stable": 0.85,
                "utility_progression": 0.50,
                "prob_s_to_p_a": 0.10,
                "prob_s_to_p_b": 0.25,
                "prob_s_to_d": 0.02,
                "prob_p_to_d": 0.15,
            },
            is_base_case=True,
            created_by_id=germany_user.id
        )

        db.add_all([spain_scenario, spain_optimistic, germany_scenario])
        db.commit()
        print("✓ Sample scenarios created")

        print("\n✅ Database seeded successfully!")
        print("\n📊 Summary:")
        print(f"  - 2 Organizations")
        print(f"  - 4 Users (1 Admin, 2 Local Users, 1 Viewer)")
        print(f"  - 1 Economic Model (Oncology)")
        print(f"  - {len(parameters)} Parameters")
        print(f"  - 3 Scenarios (2 Spain, 1 Germany)")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
