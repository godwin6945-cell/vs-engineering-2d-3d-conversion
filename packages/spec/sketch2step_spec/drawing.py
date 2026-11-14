"""
Drawing and dimension schemas with full Pydantic v2 validation.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator
from .enums import (
    DimensionSource,
    DimensionStatus,
    DimensionType,
    FeatureType,
    ViewType,
)


class BoundingBox(BaseModel):
    """
    Normalized bounding box coordinates [0.0 - 1.0] on the drawing image
    to allow interactive highlight and zoom in the UI.
    """
    x_min: float = Field(ge=0.0, le=1.0, description="Normalized left")
    y_min: float = Field(ge=0.0, le=1.0, description="Normalized top")
    x_max: float = Field(ge=0.0, le=1.0, description="Normalized right")
    y_max: float = Field(ge=0.0, le=1.0, description="Normalized bottom")

    @model_validator(mode="after")
    def validate_bounds(self) -> "BoundingBox":
        if self.x_max < self.x_min or self.y_max < self.y_min:
            raise ValueError("Bounding box max bounds must be greater than or equal to min bounds")
        return self


class DimensionEvidence(BaseModel):
    """
    Audit evidence tracking the three independent reading passes.
    """
    claude_pass_a: Optional[float] = None
    claude_pass_b: Optional[float] = None
    ocr_reading: Optional[float] = None
    agreement_score: float = Field(default=0.0, ge=0.0, le=1.0)
    raw_ocr_text: Optional[str] = None


class DimensionSpec(BaseModel):
    """
    Individual dimension specification.
    Guarantees no value enters the 3D model without verification or human sign-off.
    """
    id: str = Field(description="Unique identifier e.g. 'dim_01'")
    name: str = Field(description="Descriptive name e.g. 'Overall Length'")
    value: Optional[float] = Field(
        default=None,
        description="Nominal numeric value. Null if missing/unreadable."
    )
    unit: str = Field(default="mm", description="Measurement unit (e.g., mm, in, deg)")
    tol_plus: float = Field(default=0.0, description="Upper tolerance (+tol)")
    tol_minus: float = Field(default=0.0, description="Lower tolerance (-tol)")
    type: DimensionType = Field(default=DimensionType.LINEAR)
    source: DimensionSource = Field(default=DimensionSource.PRINTED)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    bbox: Optional[BoundingBox] = None
    view: ViewType = Field(default=ViewType.FRONT)
    status: DimensionStatus = Field(default=DimensionStatus.NEEDS_HUMAN)
    evidence: Optional[DimensionEvidence] = None
    notes: Optional[str] = None
    confirmed_by_user_id: Optional[str] = None

    @property
    def is_verified(self) -> bool:
        return self.status in (
            DimensionStatus.VERIFIED_AUTO,
            DimensionStatus.HUMAN_CONFIRMED,
            DimensionStatus.HUMAN_ENTERED,
        ) and self.value is not None


class FeatureSpec(BaseModel):
    """
    Parametric feature referencing confirmed dimension IDs.
    """
    id: str = Field(description="Feature ID e.g. 'feat_hole_01'")
    type: FeatureType = Field(description="CAD feature type")
    dimension_ids: List[str] = Field(
        default_factory=list,
        description="Dimension IDs that drive this feature"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Resolved parameters (e.g. diameter, depth, x, y, z, count)"
    )
    parent_feature_id: Optional[str] = None


class DrawingSanityCheckResult(BaseModel):
    """Result of pure Python engineering sanity checks."""
    rule_id: str
    passed: bool
    severity: str = "ERROR"  # "ERROR" or "WARNING"
    message: str
    affected_dimension_ids: List[str] = Field(default_factory=list)


class DrawingSpec(BaseModel):
    """
    Complete structured engineering drawing specification.
    Produced by the extraction pipeline and reviewed by engineers.
    """
    drawing_number: Optional[str] = None
    title: Optional[str] = None
    revision: Optional[str] = None
    unit: str = Field(default="mm")
    material: Optional[str] = None
    general_tolerance: str = Field(default="ISO 2768-m")
    dimensions: List[DimensionSpec] = Field(default_factory=list)
    features: List[FeatureSpec] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)
    ambiguities: List[str] = Field(default_factory=list)
    sanity_checks: List[DrawingSanityCheckResult] = Field(default_factory=list)

    @property
    def all_dimensions_verified(self) -> bool:
        """Accuracy rule: True only if every single dimension is verified."""
        if not self.dimensions:
            return False
        return all(d.is_verified for d in self.dimensions)

    @property
    def pending_human_dimensions(self) -> List[DimensionSpec]:
        """Dimensions that strictly block geometry generation."""
        return [d for d in self.dimensions if not d.is_verified]
