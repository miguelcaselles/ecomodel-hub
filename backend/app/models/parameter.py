from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, Enum as SQLEnum

from sqlalchemy.orm import relationship
import uuid
import enum
from app.db.base import Base
from app.db.compat import GUID, JSONType

class DataType(str, enum.Enum):
    FLOAT = "float"
    INT = "int"
    PERCENTAGE = "percentage"
    CURRENCY = "currency"
    BOOLEAN = "boolean"

class InputType(str, enum.Enum):
    SLIDER = "slider"
    NUMBER = "number"
    SELECT = "select"
    CHECKBOX = "checkbox"

class Parameter(Base):
    __tablename__ = "parameters"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    model_id = Column(GUID, ForeignKey("economic_models.id"), nullable=False)
    name = Column(String, nullable=False)  # Internal variable name
    display_name = Column(String, nullable=False)  # UI label
    description = Column(Text)
    category = Column(String)  # For accordion grouping: "Costes", "Utilidades", etc.
    data_type = Column(SQLEnum(DataType), nullable=False, default=DataType.FLOAT)
    input_type = Column(SQLEnum(InputType), nullable=False, default=InputType.NUMBER)
    default_value = Column(JSONType, nullable=True)
    constraints = Column(JSONType, default={})  # {min, max, step, options}
    distribution = Column(JSONType)  # For PSA: {type: "beta", alpha: 10, beta: 90}
    is_country_specific = Column(Boolean, default=False)
    is_editable_by_local = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    unit = Column(String)  # "EUR", "%", "days"

    # Relationships
    model = relationship("EconomicModel", back_populates="parameters")
