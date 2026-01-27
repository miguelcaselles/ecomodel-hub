from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey

from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base
from app.db.compat import GUID, JSONType

class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    model_id = Column(GUID, ForeignKey("economic_models.id"), nullable=False)
    organization_id = Column(GUID, ForeignKey("organizations.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    country_code = Column(String(2))  # ISO 3166-1 alpha-2
    parameter_values = Column(JSONType, default={})  # {param_uuid: value}
    is_base_case = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)  # For viewers
    created_by_id = Column(GUID, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    model = relationship("EconomicModel", back_populates="scenarios")
    organization = relationship("Organization", back_populates="scenarios")
    created_by_user = relationship("User", back_populates="scenarios")
    simulations = relationship("Simulation", back_populates="scenario")
