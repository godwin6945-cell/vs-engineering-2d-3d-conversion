"""
Parametric builders for hole features: through, blind, counterbore, and countersink.
"""

from typing import Any, Optional
import cadquery as cq
from .base import FeatureBuilder, require_positive


class HoleThroughBuilder(FeatureBuilder):
    """Cuts a through hole at specified (x, y) coordinates."""

    def build(self, base: Optional[cq.Workplane] = None, **params: Any) -> cq.Workplane:
        if base is None:
            raise ValueError("HoleThroughBuilder requires an existing base solid")

        diameter = require_positive("diameter", params.get("diameter"))
        x = float(params.get("x", 0.0))
        y = float(params.get("y", 0.0))
        face = params.get("face", ">Z")

        return (
            base.faces(face)
            .workplane()
            .transformed(offset=cq.Vector(x, y, 0))
            .hole(diameter)
        )


class HoleBlindBuilder(FeatureBuilder):
    """Cuts a blind hole to a specified depth at (x, y)."""

    def build(self, base: Optional[cq.Workplane] = None, **params: Any) -> cq.Workplane:
        if base is None:
            raise ValueError("HoleBlindBuilder requires an existing base solid")

        diameter = require_positive("diameter", params.get("diameter"))
        depth = require_positive("depth", params.get("depth"))
        x = float(params.get("x", 0.0))
        y = float(params.get("y", 0.0))
        face = params.get("face", ">Z")

        return (
            base.faces(face)
            .workplane()
            .transformed(offset=cq.Vector(x, y, 0))
            .hole(diameter, depth)
        )


class HoleCounterboreBuilder(FeatureBuilder):
    """Cuts a counterbore hole with cbore_diameter, cbore_depth, and hole diameter."""

    def build(self, base: Optional[cq.Workplane] = None, **params: Any) -> cq.Workplane:
        if base is None:
            raise ValueError("HoleCounterboreBuilder requires an existing base solid")

        diameter = require_positive("diameter", params.get("diameter"))
        cbore_dia = require_positive("cbore_diameter", params.get("cbore_diameter"))
        cbore_depth = require_positive("cbore_depth", params.get("cbore_depth"))
        depth = params.get("depth")  # Optional depth for blind counterbore; if None, through
        x = float(params.get("x", 0.0))
        y = float(params.get("y", 0.0))
        face = params.get("face", ">Z")

        if cbore_dia <= diameter:
            raise ValueError(f"Counterbore diameter ({cbore_dia}) must be greater than hole diameter ({diameter})")

        wp = base.faces(face).workplane().transformed(offset=cq.Vector(x, y, 0))

        if depth is not None:
            d = require_positive("depth", depth)
            return wp.cboreHole(diameter, cbore_dia, cbore_depth, depth=d)
        else:
            return wp.cboreHole(diameter, cbore_dia, cbore_depth)


class HoleCountersinkBuilder(FeatureBuilder):
    """Cuts a countersink hole with csink_diameter, csink_angle (default 90 deg), and diameter."""

    def build(self, base: Optional[cq.Workplane] = None, **params: Any) -> cq.Workplane:
        if base is None:
            raise ValueError("HoleCountersinkBuilder requires an existing base solid")

        diameter = require_positive("diameter", params.get("diameter"))
        csink_dia = require_positive("csink_diameter", params.get("csink_diameter"))
        csink_angle = float(params.get("csink_angle", 90.0))
        depth = params.get("depth")
        x = float(params.get("x", 0.0))
        y = float(params.get("y", 0.0))
        face = params.get("face", ">Z")

        if csink_dia <= diameter:
            raise ValueError(f"Countersink diameter ({csink_dia}) must be greater than hole diameter ({diameter})")

        wp = base.faces(face).workplane().transformed(offset=cq.Vector(x, y, 0))

        if depth is not None:
            d = require_positive("depth", depth)
            return wp.cskHole(diameter, csink_dia, csink_angle, depth=d)
        else:
            return wp.cskHole(diameter, csink_dia, csink_angle)
