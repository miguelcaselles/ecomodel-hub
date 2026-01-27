from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base
from app.db.compat import GUID, JSONType


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    country = Column(String(2), nullable=False)  # ISO 3166-1 alpha-2
    settings = Column(JSONType, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="organization")
    scenarios = relationship("Scenario", back_populates="organization")
