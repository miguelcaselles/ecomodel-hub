from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class ReportGenerateRequest(BaseModel):
    simulation_ids: List[UUID] = Field(..., min_items=1, description="Simulations to include in report")
    template_type: str = Field(default="comprehensive", pattern="^(comprehensive|deterministic|tornado|psa)$")
    title: Optional[str] = Field(None, max_length=200)
    include_charts: bool = Field(default=True, description="Include visualizations")
    include_sensitivity: bool = Field(default=True, description="Include sensitivity analysis if available")


class ReportExcelRequest(BaseModel):
    simulation_ids: List[UUID] = Field(..., min_items=1)
    include_raw_data: bool = Field(default=True)
    include_summary: bool = Field(default=True)


class ReportStatus(BaseModel):
    id: UUID
    status: str = Field(..., pattern="^(PENDING|GENERATING|COMPLETED|FAILED)$")
    progress: int = Field(default=0, ge=0, le=100, description="Generation progress percentage")
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class ReportInDB(BaseModel):
    id: UUID
    created_by_id: UUID
    simulation_ids: List[UUID]
    template_type: str
    title: Optional[str]
    file_path: Optional[str]
    file_size: Optional[int]
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]

    class Config:
        from_attributes = True


class Report(ReportInDB):
    pass


class ReportWithDetails(Report):
    """Report with creator details"""
    created_by_name: Optional[str] = None
    organization_name: Optional[str] = None
