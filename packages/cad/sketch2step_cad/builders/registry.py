"""
Registry mapping FeatureType enums to deterministic feature builder implementations.
"""

from typing import Dict, Type
from sketch2step_spec.enums import FeatureType
from .base import FeatureBuilder
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
)

BUILDER_REGISTRY: Dict[FeatureType, Type[FeatureBuilder]] = {
    FeatureType.PLATE: PlateBuilder,
    FeatureType.BLOCK: BlockBuilder,
    FeatureType.CYLINDER: CylinderBuilder,
    FeatureType.STEPPED_SHAFT: SteppedShaftBuilder,
    FeatureType.FLANGE: FlangeBuilder,
    FeatureType.BRACKET_L: BracketLBuilder,
    FeatureType.BRACKET_U: BracketUBuilder,
    FeatureType.HOLE_THROUGH: HoleThroughBuilder,
    FeatureType.HOLE_BLIND: HoleBlindBuilder,
    FeatureType.HOLE_COUNTERBORE: HoleCounterboreBuilder,
    FeatureType.HOLE_COUNTERSINK: HoleCountersinkBuilder,
    FeatureType.HOLE_PATTERN_LINEAR: HolePatternLinearBuilder,
    FeatureType.HOLE_PATTERN_CIRCULAR: HolePatternCircularBuilder,
    FeatureType.HOLE_PATTERN_GRID: HolePatternGridBuilder,
    FeatureType.SLOT: SlotBuilder,
    FeatureType.POCKET_RECT: PocketRectBuilder,
    FeatureType.POCKET_CIRCLE: PocketCircleBuilder,
    FeatureType.POCKET_OBROUND: PocketObroundBuilder,
    FeatureType.BOSS: BossBuilder,
    FeatureType.FILLET: FilletBuilder,
    FeatureType.CHAMFER: ChamferBuilder,
    FeatureType.THREAD_COSMETIC: ThreadCosmeticBuilder,
    FeatureType.THREAD_MODELLED: ThreadModelledBuilder,
    FeatureType.KEYWAY: KeywayBuilder,
}


def get_builder(feature_type: FeatureType | str) -> FeatureBuilder:
    """Instantiate and return the deterministic builder for a given feature type."""
    if isinstance(feature_type, str):
        try:
            feature_type = FeatureType(feature_type)
        except ValueError as err:
            raise ValueError(f"Unknown CAD feature type: '{feature_type}'") from err

    builder_cls = BUILDER_REGISTRY.get(feature_type)
    if not builder_cls:
        raise ValueError(f"No builder registered for feature type: '{feature_type}'")
    return builder_cls()
