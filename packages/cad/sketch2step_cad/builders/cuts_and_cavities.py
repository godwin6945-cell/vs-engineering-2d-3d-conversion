"""
Parametric builders for cutouts and cavities: slots, pockets, and keyways.
"""

from typing import Any, Optional
import cadquery as cq
from .base import FeatureBuilder, require_positive


class SlotBuilder(FeatureBuilder):
    """
    Parametric elongated slot (through or blind).
    length: slot total length, width: slot width (slot ends are semicircular or rectangular),
    depth: cut depth (None = through all), angle: rotation angle in degrees.
    """

    def build(self, base: Optional[cq.Workplane] = None, **params: Any) -> cq.Workplane:
        if base is None:
            raise ValueError("SlotBuilder requires an existing base solid")

        length = require_positive("length", params.get("length"))
        width = require_positive("width", params.get("width"))
        depth = params.get("depth")
        x = float(params.get("x", 0.0))
        y = float(params.get("y", 0.0))
        angle = float(params.get("angle", 0.0))
        face = params.get("face", ">Z")

        wp = (
            base.faces(face)
            .workplane()
            .transformed(offset=cq.Vector(x, y, 0), rotate=cq.Vector(0, 0, angle))
            .slot2D(length, width)
        )

        if depth is not None:
            return wp.cutBlind(-require_positive("depth", depth))
        return wp.cutThruAll()


class PocketRectBuilder(FeatureBuilder):
    """
    Parametric rectangular pocket cavity with optional corner radii.
    length, width, depth, corner_radius (optional), x, y.
    """

    def build(self, base: Optional[cq.Workplane] = None, **params: Any) -> cq.Workplane:
        if base is None:
            raise ValueError("PocketRectBuilder requires an existing base solid")

        length = require_positive("length", params.get("length"))
        width = require_positive("width", params.get("width"))
        depth = require_positive("depth", params.get("depth"))
        corner_radius = params.get("corner_radius")
        x = float(params.get("x", 0.0))
        y = float(params.get("y", 0.0))
        face = params.get("face", ">Z")

        wp = (
            base.faces(face)
            .workplane()
            .transformed(offset=cq.Vector(x, y, 0))
            .rect(length, width)
        )

        pocket = wp.cutBlind(-depth)

        if corner_radius and corner_radius > 0:
            cr = float(corner_radius)
            # Apply internal corner fillets
            try:
                pocket = pocket.edges("|Z and <Z").fillet(cr)
            except Exception:
                pass  # Fallback if topology doesn't permit direct edge fillet

        return pocket


class PocketCircleBuilder(FeatureBuilder):
    """Parametric circular pocket cavity with diameter and depth."""

    def build(self, base: Optional[cq.Workplane] = None, **params: Any) -> cq.Workplane:
        if base is None:
            raise ValueError("PocketCircleBuilder requires an existing base solid")

        diameter = require_positive("diameter", params.get("diameter"))
        depth = require_positive("depth", params.get("depth"))
        x = float(params.get("x", 0.0))
        y = float(params.get("y", 0.0))
        face = params.get("face", ">Z")

        return (
            base.faces(face)
            .workplane()
            .transformed(offset=cq.Vector(x, y, 0))
            .circle(diameter / 2.0)
            .cutBlind(-depth)
        )


class PocketObroundBuilder(FeatureBuilder):
    """Parametric obround / stadium pocket cavity."""

    def build(self, base: Optional[cq.Workplane] = None, **params: Any) -> cq.Workplane:
        if base is None:
            raise ValueError("PocketObroundBuilder requires an existing base solid")

        length = require_positive("length", params.get("length"))
        width = require_positive("width", params.get("width"))
        depth = require_positive("depth", params.get("depth"))
        x = float(params.get("x", 0.0))
        y = float(params.get("y", 0.0))
        angle = float(params.get("angle", 0.0))
        face = params.get("face", ">Z")

        return (
            base.faces(face)
            .workplane()
            .transformed(offset=cq.Vector(x, y, 0), rotate=cq.Vector(0, 0, angle))
            .slot2D(length, width)
            .cutBlind(-depth)
        )


class KeywayBuilder(FeatureBuilder):
    """
    Parametric shaft keyway according to DIN 6885 / ISO standards.
    width: key width b, depth: keyway depth t, length: keyway length L.
    """

    def build(self, base: Optional[cq.Workplane] = None, **params: Any) -> cq.Workplane:
        if base is None:
            raise ValueError("KeywayBuilder requires an existing base solid")

        width = require_positive("width", params.get("width"))
        depth = require_positive("depth", params.get("depth"))
        length = require_positive("length", params.get("length"))
        offset_z = float(params.get("offset_z", 0.0))

        # Find outer radius of the shaft from bounding box
        bb = base.val().BoundingBox()
        radius = max(bb.xlen, bb.ylen) / 2.0
        center_z = bb.zmin + (bb.zlen / 2.0) + offset_z

        # Create a workplane tangent to the shaft cylinder on the XZ plane at Y = radius
        # Cut keyway slot into the cylinder along -Y normal
        keyway_cut = (
            cq.Workplane("XZ")
            .workplane(offset=radius)
            .transformed(offset=cq.Vector(0, center_z, 0))
            .slot2D(length, width, 90.0)
            .extrude(-depth)
        )

        return base.cut(keyway_cut)
