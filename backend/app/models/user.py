from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.db.base import Base
from app.db.compat import GUID, JSONType

class UserRole(str, enum.Enum):
    GLOBAL_ADMIN = "global_admin"
    LOCAL_USER = "local_user"
    VIEWER = "viewer"

class User(Base):
    __tablename__ = "users"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    # Use String type to avoid enum mapping issues, validation will use UserRole enum
    role = Column(String, nullable=False, default="local_user")
    is_active = Column(Boolean, default=True)
    organization_id = Column(GUID, ForeignKey("organizations.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="users")
    scenarios = relationship("Scenario", back_populates="created_by_user")
    simulations = relationship("Simulation", back_populates="created_by_user")
    created_models = relationship("EconomicModel", back_populates="created_by")
