"""
Enumerations for Sketch2STEP Enterprise.
"""

from enum import Enum


class JobState(str, Enum):
    """Core pipeline state machine states."""
    UPLOADED = "UPLOADED"
    PREPROCESSED = "PREPROCESSED"
    EXTRACTED = "EXTRACTED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    CONFIRMED = "CONFIRMED"
    MODELLED = "MODELLED"
    VALIDATED = "VALIDATED"
    SIGNED_OFF = "SIGNED_OFF"
    EXPORTED = "EXPORTED"
    FAILED = "FAILED"


class OrganizationRole(str, Enum):
    """Role-based access control roles."""
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    ENGINEER = "ENGINEER"
    REVIEWER = "REVIEWER"  # approve only
    VIEWER = "VIEWER"


class DimensionType(str, Enum):
    """Geometric dimension types."""
    LINEAR = "linear"
    DIAMETER = "diameter"
    RADIUS = "radius"
    ANGLE = "angle"
    DEPTH = "depth"
    THREAD = "thread"


class DimensionSource(str, Enum):
    """Origin source of the extracted dimension."""
    PRINTED = "printed"
    INFERRED = "inferred"
    MISSING = "missing"


class DimensionStatus(str, Enum):
    """
    Accuracy status per dimension:
    - verified_auto: pass A, pass B, and OCR all agree exactly
    - needs_human: discrepancy, low confidence, inferred, or missing
    - human_confirmed: human verified an unconfirmed value
    - human_entered: human manually typed in a missing/unreadable value
    """
    VERIFIED_AUTO = "verified_auto"
    NEEDS_HUMAN = "needs_human"
    HUMAN_CONFIRMED = "human_confirmed"
    HUMAN_ENTERED = "human_entered"


class ViewType(str, Enum):
    """Drawing projection views."""
    FRONT = "front"
    TOP = "top"
    SIDE = "side"
    ISOMETRIC = "isometric"
    DETAIL = "detail"
    SECTION = "section"
    UNKNOWN = "unknown"


class FeatureType(str, Enum):
    """Supported CAD parametric features."""
    PLATE = "plate"
    BLOCK = "block"
    CYLINDER = "cylinder"
    STEPPED_SHAFT = "stepped_shaft"
    FLANGE = "flange"
    BRACKET_L = "bracket_l"
    BRACKET_U = "bracket_u"
    HOLE_THROUGH = "hole_through"
    HOLE_BLIND = "hole_blind"
    HOLE_COUNTERBORE = "hole_counterbore"
    HOLE_COUNTERSINK = "hole_countersink"
    HOLE_PATTERN_LINEAR = "hole_pattern_linear"
    HOLE_PATTERN_CIRCULAR = "hole_pattern_circular"
    HOLE_PATTERN_GRID = "hole_pattern_grid"
    SLOT = "slot"
    POCKET_RECT = "pocket_rect"
    POCKET_CIRCLE = "pocket_circle"
    POCKET_OBROUND = "pocket_obround"
    BOSS = "boss"
    FILLET = "fillet"
    CHAMFER = "chamfer"
    THREAD_COSMETIC = "thread_cosmetic"
    THREAD_MODELLED = "thread_modelled"
    KEYWAY = "keyway"
