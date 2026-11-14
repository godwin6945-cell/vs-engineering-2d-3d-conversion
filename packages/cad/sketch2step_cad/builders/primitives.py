"""
Parametric builders for base primitive shapes: plates, blocks, cylinders, and stepped shafts.
"""

from typing import Any, List, Optional, Union
import cadquery as cq
from .base import FeatureBuilder, require_positive


class PlateBuilder(FeatureBuilder):
    """Parametric flat plate builder with length, width, and thickness."""

    def build(self, base: Optional[cq.Workplane] = None, **params: Any) -> cq.Workplane:
        length = require_positive("length", params.get("length"))
        width = require_positive("width", params.get("width"))
        thickness = require_positive("thickness", params.get("thickness"))
        centered = params.get("centered", True)

        wp = base if base is not None else cq.Workplane("XY")
        return wp.box(length, width, thickness, centered=centered)


class BlockBuilder(FeatureBuilder):
    """Parametric rectangular block builder with length, width, and height."""

    def build(self, base: Optional[cq.Workplane] = None, **params: Any) -> cq.Workplane:
        length = require_positive("length", params.get("length"))
        width = require_positive("width", params.get("width"))
        height = require_positive("height", params.get("height"))
        centered = params.get("centered", True)

        wp = base if base is not None else cq.Workplane("XY")
        return wp.box(length, width, height, centered=centered)


class CylinderBuilder(FeatureBuilder):
    """Parametric cylinder builder with diameter/radius and height."""

    def build(self, base: Optional[cq.Workplane] = None, **params: Any) -> cq.Workplane:
        if "diameter" in params and params["diameter"] is not None:
            diameter = require_positive("diameter", params["diameter"])
            radius = diameter / 2.0
        elif "radius" in params and params["radius"] is not None:
            radius = require_positive("radius", params["radius"])
        else:
            raise ValueError("CylinderBuilder requires either 'diameter' or 'radius'")

        height = require_positive("height", params.get("height"))
        both = params.get("centered", False)

        wp = base if base is not None else cq.Workplane("XY")
        return wp.circle(radius).extrude(height, both=both)


class SteppedShaftBuilder(FeatureBuilder):
    """
    Parametric stepped shaft builder (turned parts).
    Takes an ordered sequence of turned shaft steps: [{'diameter': d, 'length': l}, ...]
    Builds concentric turned cylinders stacked along the Z-axis.
    """

    def build(self, base: Optional[cq.Workplane] = None, **params: Any) -> cq.Workplane:
        steps = params.get("steps")
        if not steps or not isinstance(steps, list):
            raise ValueError("SteppedShaftBuilder requires a non-empty list of 'steps'")

        solid: Optional[cq.Workplane] = None
        current_z = 0.0

        for idx, step in enumerate(steps):
            d = require_positive(f"steps[{idx}].diameter", step.get("diameter"))
            l = require_positive(f"steps[{idx}].length", step.get("length"))
            radius = d / 2.0

            # Create step on XY workplane offset at current_z
            step_solid = (
                cq.Workplane("XY")
                .workplane(offset=current_z)
                .circle(radius)
                .extrude(l)
            )

            if solid is None:
                solid = step_solid
            else:
                solid = solid.union(step_solid)

            current_z += l

        return solid if solid is not None else cq.Workplane("XY")
