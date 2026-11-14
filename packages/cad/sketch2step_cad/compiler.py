"""
Deterministic CAD Feature Compiler.
Compiles structured, confirmed DrawingSpec into a parametric CadQuery solid model.
"""

from typing import Dict, List, Optional
import cadquery as cq
from sketch2step_spec.drawing import DimensionSpec, DrawingSpec, FeatureSpec
from sketch2step_spec.enums import FeatureType
from .builders.registry import get_builder


class CompilationError(Exception):
    """Raised when CAD compilation fails geometric or logical constraints."""
    pass


class FeatureCompiler:
    """
    Deterministic Feature Compiler.
    Compiles features in topological order:
    1. Base primitive (plate, block, cylinder, shaft, flange, bracket)
    2. Subtractive cavities (pockets, slots, keyways)
    3. Holes and patterns (through, blind, cbore, csink, pcd, grid)
    4. Dress-up features (bosses, fillets, chamfers)
    """

    BASE_TYPES = {
        FeatureType.PLATE,
        FeatureType.BLOCK,
        FeatureType.CYLINDER,
        FeatureType.STEPPED_SHAFT,
        FeatureType.FLANGE,
        FeatureType.BRACKET_L,
        FeatureType.BRACKET_U,
    }

    SUBTRACTIVE_TYPES = {
        FeatureType.POCKET_RECT,
        FeatureType.POCKET_CIRCLE,
        FeatureType.POCKET_OBROUND,
        FeatureType.SLOT,
        FeatureType.KEYWAY,
    }

    HOLE_TYPES = {
        FeatureType.HOLE_THROUGH,
        FeatureType.HOLE_BLIND,
        FeatureType.HOLE_COUNTERBORE,
        FeatureType.HOLE_COUNTERSINK,
        FeatureType.HOLE_PATTERN_LINEAR,
        FeatureType.HOLE_PATTERN_CIRCULAR,
        FeatureType.HOLE_PATTERN_GRID,
        FeatureType.THREAD_COSMETIC,
        FeatureType.THREAD_MODELLED,
    }

    DRESSUP_TYPES = {
        FeatureType.BOSS,
        FeatureType.FILLET,
        FeatureType.CHAMFER,
    }

    def compile(self, spec: DrawingSpec) -> cq.Workplane:
        """
        Compiles the DrawingSpec into a validated CadQuery Workplane solid.
        Enforces Accuracy Rule: All dimensions must be verified before compilation.
        """
        if not spec.all_dimensions_verified:
            pending_ids = [d.id for d in spec.pending_human_dimensions]
            raise CompilationError(
                f"Accuracy Rule violation: Cannot compile CAD model with unverified dimensions: {pending_ids}"
            )

        # Build dimension lookup map: {id: numeric_value}
        dim_map: Dict[str, float] = {
            d.id: d.value for d in spec.dimensions if d.value is not None
        }

        # Sort features into execution stages
        base_features = [f for f in spec.features if f.type in self.BASE_TYPES]
        subtractive_features = [f for f in spec.features if f.type in self.SUBTRACTIVE_TYPES]
        hole_features = [f for f in spec.features if f.type in self.HOLE_TYPES]
        dressup_features = [f for f in spec.features if f.type in self.DRESSUP_TYPES]

        if not base_features:
            raise CompilationError("DrawingSpec must define at least one base structural feature")

        solid: Optional[cq.Workplane] = None

        # Stage 1: Build Base Solid
        for feat in base_features:
            resolved_params = self._resolve_parameters(feat, dim_map)
            builder = get_builder(feat.type)
            solid = builder.build(base=solid, **resolved_params)

        # Stage 2: Cut Cavities and Pockets
        for feat in subtractive_features:
            resolved_params = self._resolve_parameters(feat, dim_map)
            builder = get_builder(feat.type)
            solid = builder.build(base=solid, **resolved_params)

        # Stage 3: Drill Holes and Hole Patterns
        for feat in hole_features:
            resolved_params = self._resolve_parameters(feat, dim_map)
            builder = get_builder(feat.type)
            solid = builder.build(base=solid, **resolved_params)

        # Stage 4: Apply Dressup (Fillets, Chamfers, Bosses)
        for feat in dressup_features:
            resolved_params = self._resolve_parameters(feat, dim_map)
            builder = get_builder(feat.type)
            solid = builder.build(base=solid, **resolved_params)

        if solid is None:
            raise CompilationError("Compilation resulted in empty geometry")

        return solid

    def _resolve_parameters(
        self, feat: FeatureSpec, dim_map: Dict[str, float]
    ) -> Dict[str, any]:
        """Resolves feature parameters, injecting dimension values for bound dimension IDs."""
        resolved = dict(feat.parameters)

        # Direct parameter mapping if dimensions are mapped to parameter names
        for dim_id in feat.dimension_ids:
            if dim_id in dim_map:
                # If param has matching key or prefix
                val = dim_map[dim_id]
                # Default inject into parameter if named similarly
                for p_key in list(resolved.keys()):
                    if resolved[p_key] == dim_id:
                        resolved[p_key] = val

        return resolved
