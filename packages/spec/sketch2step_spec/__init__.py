"""
Shared specification schemas for Sketch2STEP Enterprise.
"""

from .enums import (
    DimensionSource,
    DimensionStatus,
    DimensionType,
    FeatureType,
    JobState,
    OrganizationRole,
    ViewType,
)
from .drawing import (
    BoundingBox,
    DimensionEvidence,
    DimensionSpec,
    FeatureSpec,
    DrawingSpec,
    DrawingSanityCheckResult,
)
from .tenant import (
    UserBase,
    UserCreate,
    UserResponse,
    OrganizationBase,
    OrganizationCreate,
    OrganizationResponse,
    TokenPayload,
    TokenResponse,
)
from .job import (
    JobCreate,
    JobResponse,
    JobUpdate,
    JobStateTransition,
    ValidationReport,
    VisualDiffResult,
)
from .diff import (
    DimensionChange,
    GeometryDiff,
    JobVersionDiff,
    compute_spec_diff,
    compute_geometry_diff,
)
from .rules_engine import (
    run_all_sanity_checks,
    check_dimension_positivity,
    check_tolerance_bounds,
    check_unit_consistency,
    check_overall_vs_segment_sums,
    check_hole_placement_and_margins,
    check_fillet_chamfer_proportions,
    check_iso_thread_standards,
    check_pattern_spacing_feasibility,
)

__all__ = [
    "DimensionSource",
    "DimensionStatus",
    "DimensionType",
    "FeatureType",
    "JobState",
    "OrganizationRole",
    "ViewType",
    "BoundingBox",
    "DimensionEvidence",
    "DimensionSpec",
    "FeatureSpec",
    "DrawingSpec",
    "DrawingSanityCheckResult",
    "UserBase",
    "UserCreate",
    "UserResponse",
    "OrganizationBase",
    "OrganizationCreate",
    "OrganizationResponse",
    "TokenPayload",
    "TokenResponse",
    "JobCreate",
    "JobResponse",
    "JobUpdate",
    "JobStateTransition",
    "ValidationReport",
    "VisualDiffResult",
]
