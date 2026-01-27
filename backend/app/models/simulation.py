from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Enum as SQLEnum

from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.db.base import Base
from app.db.compat import GUID, JSONType

class SimulationType(str, enum.Enum):
    DETERMINISTIC = "deterministic"
    ONE_WAY_SA = "one_way_sa"
    TORNADO = "tornado"
    PSA = "psa"

class SimulationStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    scenario_id = Column(GUID, ForeignKey("scenarios.id"), nullable=False)
    simulation_type = Column(SQLEnum(SimulationType), nullable=False, default=SimulationType.DETERMINISTIC)
    status = Column(SQLEnum(SimulationStatus), nullable=False, default=SimulationStatus.PENDING)
    celery_task_id = Column(String)
    input_snapshot = Column(JSONType, default={})  # Inputs at execution time
    results = Column(JSONType, default={})  # {drug_a, drug_b, incremental}
    sensitivity_results = Column(JSONType)  # For SA/PSA: tornado, psa_iterations, ceac_data
    execution_time_ms = Column(Integer)
    error_message = Column(Text)
    created_by_id = Column(GUID, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    # Relationships
    scenario = relationship("Scenario", back_populates="simulations")
    created_by_user = relationship("User", back_populates="simulations")
