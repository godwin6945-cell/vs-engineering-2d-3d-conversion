"""
Parametric builders for hole patterns: linear, circular (PCD), and 2D grid.
"""

import math
from typing import Any, List, Optional, Tuple
import cadquery as cq
from .base import FeatureBuilder, require_positive


class HolePatternLinearBuilder(FeatureBuilder):
    """
    Parametric linear hole pattern.
    count: number of holes (>= 1), pitch: spacing between centers,
    diameter: hole diameter, depth: hole depth (None = through),
    angle: direction angle in degrees (default 0 = along X axis).
    """

    def build(self, base: Optional[cq.Workplane] = None, **params: Any) -> cq.Workplane:
        if base is None:
            raise ValueError("HolePatternLinearBuilder requires an existing base solid")

        count = int(params.get("count", 1))
        if count < 1:
            raise ValueError(f"Hole pattern count must be >= 1, got {count}")

        pitch = require_positive("pitch", params.get("pitch", 1.0)) if count > 1 else 0.0
        diameter = require_positive("diameter", params.get("diameter"))
        depth = params.get("depth")
        start_x = float(params.get("start_x", 0.0))
        start_y = float(params.get("start_y", 0.0))
        angle_rad = math.radians(float(params.get("angle", 0.0)))
        face = params.get("face", ">Z")

        # Generate center coordinates
        pts: List[Tuple[float, float]] = []
        for i in range(count):
            dist = i * pitch
            px = start_x + dist * math.cos(angle_rad)
            py = start_y + dist * math.sin(angle_rad)
            pts.append((px, py))

        wp = base.faces(face).workplane().pushPoints(pts)
        if depth is not None:
            return wp.hole(diameter, require_positive("depth", depth))
        return wp.hole(diameter)


class HolePatternCircularBuilder(FeatureBuilder):
    """
    Parametric circular Pitch Circle Diameter (PCD) hole pattern.
    pcd: pitch circle diameter, count: number of equi-spaced holes,
    diameter: hole diameter, depth: hole depth (None = through),
    start_angle: angle of first hole in degrees (default 0).
    """

    def build(self, base: Optional[cq.Workplane] = None, **params: Any) -> cq.Workplane:
        if base is None:
            raise ValueError("HolePatternCircularBuilder requires an existing base solid")

        pcd = require_positive("pcd", params.get("pcd"))
        count = int(params.get("count", 4))
        if count < 1:
            raise ValueError(f"Circular hole pattern count must be >= 1, got {count}")

        diameter = require_positive("diameter", params.get("diameter"))
        depth = params.get("depth")
        center_x = float(params.get("center_x", 0.0))
        center_y = float(params.get("center_y", 0.0))
        start_angle = math.radians(float(params.get("start_angle", 0.0)))
        face = params.get("face", ">Z")
        radius = pcd / 2.0

        pts: List[Tuple[float, float]] = []
        angle_step = 2.0 * math.pi / count
        for i in range(count):
            ang = start_angle + i * angle_step
            px = center_x + radius * math.cos(ang)
            py = center_y + radius * math.sin(ang)
            pts.append((px, py))

        wp = base.faces(face).workplane().pushPoints(pts)
        if depth is not None:
            return wp.hole(diameter, require_positive("depth", depth))
        return wp.hole(diameter)


class HolePatternGridBuilder(FeatureBuilder):
    """
    Parametric 2D grid hole pattern.
    x_count, y_count: number of rows and columns,
    x_spacing, y_spacing: pitch between holes,
    diameter: hole diameter, depth: hole depth (None = through).
    """

    def build(self, base: Optional[cq.Workplane] = None, **params: Any) -> cq.Workplane:
        if base is None:
            raise ValueError("HolePatternGridBuilder requires an existing base solid")

        x_count = int(params.get("x_count", 2))
        y_count = int(params.get("y_count", 2))
        if x_count < 1 or y_count < 1:
            raise ValueError("Grid pattern counts must be >= 1")

        x_spacing = require_positive("x_spacing", params.get("x_spacing", 1.0)) if x_count > 1 else 0.0
        y_spacing = require_positive("y_spacing", params.get("y_spacing", 1.0)) if y_count > 1 else 0.0
        diameter = require_positive("diameter", params.get("diameter"))
        depth = params.get("depth")
        face = params.get("face", ">Z")
        centered = params.get("centered", True)

        # Center grid around origin if centered
        x_offset = -((x_count - 1) * x_spacing) / 2.0 if centered else 0.0
        y_offset = -((y_count - 1) * y_spacing) / 2.0 if centered else 0.0

        pts: List[Tuple[float, float]] = []
        for ix in range(x_count):
            for iy in range(y_count):
                pts.append((x_offset + ix * x_spacing, y_offset + iy * y_spacing))

        wp = base.faces(face).workplane().pushPoints(pts)
        if depth is not None:
            return wp.hole(diameter, require_positive("depth", depth))
        return wp.hole(diameter)
