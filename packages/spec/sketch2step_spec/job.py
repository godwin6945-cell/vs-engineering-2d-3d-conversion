"""
Job lifecycle, state transitions, validation and diff schemas.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from .enums import JobState
from .drawing import DrawingSpec


class JobCreate(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    drawing_filename: str
    drawing_content_type: str = "image/png"
    target_units: str = "mm"
    project_id: Optional[str] = None


class JobStateTransition(BaseModel):
    from_state: JobState
    to_state: JobState
    transitioned_by_user_id: Optional[str] = None
    reason: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class GeometryMeasurement(BaseModel):
    name: str
    dimension_id: Optional[str] = None
    specified_value: float
    measured_value: float
    tolerance_plus: float = 0.05
    tolerance_minus: float = 0.05
    deviation: float
    passed: bool
    source_attribution: str  # e.g. "verified_auto (Claude A + OCR)" or "human_entered by user_123"


class ValidationReport(BaseModel):
    is_valid_solid: bool
    is_shell_closed: bool
    has_self_intersections: bool
    bounding_box_x: float
    bounding_box_y: float
    bounding_box_z: float
    volume_mm3: float
    surface_area_mm2: float
    face_count: int
    edge_count: int
    hole_count: int
    step_roundtrip_ok: bool
    measurements: List[GeometryMeasurement] = Field(default_factory=list)
    overall_passed: bool = False


class VisualDiffResult(BaseModel):
    match_percentage: float = Field(ge=0.0, le=100.0)
    identified_discrepancies: List[str] = Field(default_factory=list)
    rendered_ortho_urls: Dict[str, str] = Field(default_factory=dict)  # front, top, side view URLs


class JobResponse(BaseModel):
    id: str
    org_id: str
    project_id: Optional[str] = None
    title: str
    state: JobState
    drawing_file_url: str
    spec: Optional[DrawingSpec] = None
    validation_report: Optional[ValidationReport] = None
    visual_diff: Optional[VisualDiffResult] = None
    step_file_url: Optional[str] = None
    cad_script_url: Optional[str] = None
    inspection_report_pdf_url: Optional[str] = None
    signed_off_by_user_id: Optional[str] = None
    signed_off_at: Optional[datetime] = None
    version: int = 1
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobUpdate(BaseModel):
    title: Optional[str] = None
    spec: Optional[DrawingSpec] = None
    state: Optional[JobState] = None
