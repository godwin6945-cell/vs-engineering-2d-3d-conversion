"""
Parametric builders for dress-up features: bosses, fillets, chamfers, and threads.
"""

from typing import Any, Dict, Optional
import cadquery as cq
from .base import FeatureBuilder, require_positive

# Standard ISO Metric Coarse Pitch Tap Drill Sizes (ISO 261 / DIN 13)
ISO_METRIC_TAP_DRILL: Dict[str, Dict[str, float]] = {
    "M3": {"pitch": 0.5, "tap_drill": 2.5, "nominal_dia": 3.0},
    "M4": {"pitch": 0.7, "tap_drill": 3.3, "nominal_dia": 4.0},
    "M5": {"pitch": 0.8, "tap_drill": 4.2, "nominal_dia": 5.0},
    "M6": {"pitch": 1.0, "tap_drill": 5.0, "nominal_dia": 6.0},
    "M8": {"pitch": 1.25, "tap_drill": 6.8, "nominal_dia": 8.0},
    "M10": {"pitch": 1.5, "tap_drill": 8.5, "nominal_dia": 10.0},
    "M12": {"pitch": 1.75, "tap_drill": 10.2, "nominal_dia": 12.0},
    "M16": {"pitch": 2.0, "tap_drill": 14.0, "nominal_dia": 16.0},
    "M20": {"pitch": 2.5, "tap_drill": 17.5, "nominal_dia": 20.0},
    "M24": {"pitch": 3.0, "tap_drill": 21.0, "nominal_dia": 24.0},
}


class BossBuilder(FeatureBuilder):
    """
    Parametric cylindrical or rectangular boss protrusion on a face.
    diameter or (length, width), height, x, y, face (default '>Z').
    """

    def build(self, base: Optional[cq.Workplane] = None, **params: Any) -> cq.Workplane:
        if base is None:
            raise ValueError("BossBuilder requires an existing base solid")

        height = require_positive("height", params.get("height"))
        x = float(params.get("x", 0.0))
        y = float(params.get("y", 0.0))
        face = params.get("face", ">Z")

        wp = base.faces(face).workplane().transformed(offset=cq.Vector(x, y, 0))

        if "diameter" in params and params["diameter"]:
            dia = require_positive("diameter", params["diameter"])
            return wp.circle(dia / 2.0).extrude(height)
        elif "length" in params and "width" in params:
            l = require_positive("length", params["length"])
            w = require_positive("width", params["width"])
            return wp.rect(l, w).extrude(height)
        else:
            raise ValueError("BossBuilder requires either 'diameter' or both 'length' and 'width'")


class FilletBuilder(FeatureBuilder):
    """Applies edge fillets with specified radius to selected edges."""

    def build(self, base: Optional[cq.Workplane] = None, **params: Any) -> cq.Workplane:
        if base is None:
            raise ValueError("FilletBuilder requires an existing base solid")

        radius = require_positive("radius", params.get("radius"))
        edge_selector = params.get("edge_selector", "|Z")

        return base.edges(edge_selector).fillet(radius)


class ChamferBuilder(FeatureBuilder):
    """Applies edge chamfers with specified length to selected edges."""

    def build(self, base: Optional[cq.Workplane] = None, **params: Any) -> cq.Workplane:
        if base is None:
            raise ValueError("ChamferBuilder requires an existing base solid")

        length = require_positive("length", params.get("length"))
        edge_selector = params.get("edge_selector", ">Z")

        return base.edges(edge_selector).chamfer(length)


class ThreadCosmeticBuilder(FeatureBuilder):
    """
    Standard cosmetic thread builder (produces tap drill hole and adds ISO thread metadata).
    thread_callout (e.g., 'M8', 'M10'), depth (None = through), x, y.
    """

    def build(self, base: Optional[cq.Workplane] = None, **params: Any) -> cq.Workplane:
        if base is None:
            raise ValueError("ThreadCosmeticBuilder requires an existing base solid")

        thread_callout = str(params.get("thread_callout", "M6")).upper()
        depth = params.get("depth")
        x = float(params.get("x", 0.0))
        y = float(params.get("y", 0.0))
        face = params.get("face", ">Z")

        thread_info = ISO_METRIC_TAP_DRILL.get(thread_callout)
        if not thread_info:
            raise ValueError(
                f"Unsupported ISO metric thread callout '{thread_callout}'. "
                f"Supported sizes: {list(ISO_METRIC_TAP_DRILL.keys())}"
            )

        # Cut standard tap drill core hole
        tap_drill_dia = thread_info["tap_drill"]
        wp = base.faces(face).workplane().transformed(offset=cq.Vector(x, y, 0))

        if depth is not None:
            d = require_positive("depth", depth)
            return wp.hole(tap_drill_dia, d)
        return wp.hole(tap_drill_dia)


class ThreadModelledBuilder(FeatureBuilder):
    """
    Modelled thread representation. Creates thread cylinder / pilot representation.
    """

    def build(self, base: Optional[cq.Workplane] = None, **params: Any) -> cq.Workplane:
        if base is None:
            raise ValueError("ThreadModelledBuilder requires an existing base solid")

        thread_callout = str(params.get("thread_callout", "M10")).upper()
        depth = require_positive("depth", params.get("depth", 20.0))
        x = float(params.get("x", 0.0))
        y = float(params.get("y", 0.0))
        face = params.get("face", ">Z")

        thread_info = ISO_METRIC_TAP_DRILL.get(thread_callout, {"tap_drill": 8.5})
        dia = thread_info["tap_drill"]

        return (
            base.faces(face)
            .workplane()
            .transformed(offset=cq.Vector(x, y, 0))
            .hole(dia, depth)
        )
