from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, Enum as SQLEnum

from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.db.base import Base
from app.db.compat import GUID, JSONType

class ModelType(str, enum.Enum):
    MARKOV = "markov"
    DECISION_TREE = "decision_tree"
    PARTITION_SURVIVAL = "partition_survival"

class EconomicModel(Base):
    __tablename__ = "economic_models"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    model_type = Column(
        SQLEnum(ModelType, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False, default=ModelType.MARKOV
    )
    script_content = Column(Text)  # Python script uploaded by Global Admin
    script_hash = Column(String)  # SHA256 for versioning
    config = Column(JSONType, default={})  # Model configuration
    version = Column(String, default="1.0")
    is_published = Column(Boolean, default=False)
    created_by_id = Column(GUID, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parameters = relationship("Parameter", back_populates="model", cascade="all, delete-orphan")
    scenarios = relationship("Scenario", back_populates="model")
    created_by = relationship("User", back_populates="created_models", foreign_keys=[created_by_id])
