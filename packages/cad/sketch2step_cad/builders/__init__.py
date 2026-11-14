"""
Deterministic CAD feature builders package.
"""

from .base import FeatureBuilder, require_positive, require_non_negative
from .primitives import PlateBuilder, BlockBuilder, CylinderBuilder, SteppedShaftBuilder
from .structural import FlangeBuilder, BracketLBuilder, BracketUBuilder
from .holes import (
    HoleThroughBuilder,
    HoleBlindBuilder,
    HoleCounterboreBuilder,
    HoleCountersinkBuilder,
)
from .patterns import (
    HolePatternLinearBuilder,
    HolePatternCircularBuilder,
    HolePatternGridBuilder,
)
from .cuts_and_cavities import (
    SlotBuilder,
    PocketRectBuilder,
    PocketCircleBuilder,
    PocketObroundBuilder,
    KeywayBuilder,
)
from .dressup import (
    BossBuilder,
    FilletBuilder,
    ChamferBuilder,
    ThreadCosmeticBuilder,
    ThreadModelledBuilder,
    ISO_METRIC_TAP_DRILL,
)
from .registry import BUILDER_REGISTRY, get_builder

__all__ = [
    "FeatureBuilder",
    "require_positive",
    "require_non_negative",
    "PlateBuilder",
    "BlockBuilder",
    "CylinderBuilder",
    "SteppedShaftBuilder",
    "FlangeBuilder",
    "BracketLBuilder",
    "BracketUBuilder",
    "HoleThroughBuilder",
    "HoleBlindBuilder",
    "HoleCounterboreBuilder",
    "HoleCountersinkBuilder",
    "HolePatternLinearBuilder",
    "HolePatternCircularBuilder",
    "HolePatternGridBuilder",
    "SlotBuilder",
    "PocketRectBuilder",
    "PocketCircleBuilder",
    "PocketObroundBuilder",
    "KeywayBuilder",
    "BossBuilder",
    "FilletBuilder",
    "ChamferBuilder",
    "ThreadCosmeticBuilder",
    "ThreadModelledBuilder",
    "ISO_METRIC_TAP_DRILL",
    "BUILDER_REGISTRY",
    "get_builder",
]
