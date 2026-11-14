"""
Parametric builders for structural components: flanges, L-brackets, and U-brackets.
"""

from typing import Any, Optional
import cadquery as cq
from .base import FeatureBuilder, require_positive


class FlangeBuilder(FeatureBuilder):
    """
    Parametric circular flange with central bore and optional neck hub.
    outer_diameter, thickness, bore_diameter (optional), hub_diameter (optional), hub_height (optional).
    """

    def build(self, base: Optional[cq.Workplane] = None, **params: Any) -> cq.Workplane:
        outer_dia = require_positive("outer_diameter", params.get("outer_diameter"))
        thickness = require_positive("thickness", params.get("thickness"))
        bore_dia = params.get("bore_diameter")
        hub_dia = params.get("hub_diameter")
        hub_height = params.get("hub_height")

        wp = base if base is not None else cq.Workplane("XY")

        # Flange disc base
        flange = wp.circle(outer_dia / 2.0).extrude(thickness)

        # Add hub if specified
        if hub_dia and hub_height:
            h_dia = require_positive("hub_diameter", hub_dia)
            h_height = require_positive("hub_height", hub_height)
            hub = (
                cq.Workplane("XY")
                .workplane(offset=thickness)
                .circle(h_dia / 2.0)
                .extrude(h_height)
            )
            flange = flange.union(hub)

        # Cut central bore if specified
        if bore_dia:
            b_dia = require_positive("bore_diameter", bore_dia)
            total_height = thickness + (require_positive("hub_height", hub_height) if hub_height else 0.0)
            flange = (
                flange.faces(">Z")
                .workplane()
                .circle(b_dia / 2.0)
                .cutThruAll()
            )

        return flange


class BracketLBuilder(FeatureBuilder):
    """
    Parametric L-shaped angle bracket.
    leg1: horizontal leg length, leg2: vertical leg height, width: depth extrusion, thickness: wall thickness.
    """

    def build(self, base: Optional[cq.Workplane] = None, **params: Any) -> cq.Workplane:
        leg1 = require_positive("leg1", params.get("leg1"))
        leg2 = require_positive("leg2", params.get("leg2"))
        width = require_positive("width", params.get("width"))
        thickness = require_positive("thickness", params.get("thickness"))

        if thickness >= leg1 or thickness >= leg2:
            raise ValueError(f"Thickness ({thickness}) must be less than leg1 ({leg1}) and leg2 ({leg2})")

        # Sketch profile on XZ plane and extrude along Y (width)
        # Coordinates: (0,0) -> (leg1, 0) -> (leg1, thickness) -> (thickness, thickness) -> (thickness, leg2) -> (0, leg2) -> close
        profile_pts = [
            (0.0, 0.0),
            (leg1, 0.0),
            (leg1, thickness),
            (thickness, thickness),
            (thickness, leg2),
            (0.0, leg2),
        ]

        wp = base if base is not None else cq.Workplane("XZ")
        return wp.polyline(profile_pts).close().extrude(width)


class BracketUBuilder(FeatureBuilder):
    """
    Parametric U-channel bracket.
    base_width: outer bottom width, leg_height: outer vertical walls height,
    length: extrusion length, thickness: wall thickness.
    """

    def build(self, base: Optional[cq.Workplane] = None, **params: Any) -> cq.Workplane:
        base_width = require_positive("base_width", params.get("base_width"))
        leg_height = require_positive("leg_height", params.get("leg_height"))
        length = require_positive("length", params.get("length"))
        thickness = require_positive("thickness", params.get("thickness"))

        if 2 * thickness >= base_width or thickness >= leg_height:
            raise ValueError(
                f"Thickness ({thickness}) exceeds physical boundaries for U-bracket (base: {base_width}, height: {leg_height})"
            )

        # U-profile points on XZ plane
        profile_pts = [
            (0.0, 0.0),
            (base_width, 0.0),
            (base_width, leg_height),
            (base_width - thickness, leg_height),
            (base_width - thickness, thickness),
            (thickness, thickness),
            (thickness, leg_height),
            (0.0, leg_height),
        ]

        wp = base if base is not None else cq.Workplane("XZ")
        return wp.polyline(profile_pts).close().extrude(length)
