"""
Unit tests for CAD pattern builders: Linear, Circular (PCD), and 2D Grid hole patterns.
"""

import math
import pytest
import cadquery as cq
from sketch2step_cad.builders.patterns import (
    HolePatternCircularBuilder,
    HolePatternGridBuilder,
    HolePatternLinearBuilder,
)


@pytest.fixture
def base_disc() -> cq.Workplane:
    # Circular disc 150 mm dia x 15 mm thick
    return cq.Workplane("XY").circle(75.0).extrude(15.0)


@pytest.fixture
def base_plate() -> cq.Workplane:
    # Rectangular plate 200 x 200 x 20 mm
    return cq.Workplane("XY").box(200.0, 200.0, 20.0, centered=(True, True, False))


def test_hole_pattern_linear(base_plate: cq.Workplane):
    orig_vol = base_plate.val().Volume()
    builder = HolePatternLinearBuilder()
    # 4 holes of dia 10mm spaced 30mm apart
    solid = builder.build(
        base=base_plate,
        count=4,
        pitch=30.0,
        diameter=10.0,
        start_x=-45.0,
        start_y=0.0,
    )

    shape = solid.val()
    assert shape.isValid()
    # 4 holes * (pi * 5^2 * 20) = 4 * 500 * pi = 2000 * pi
    total_hole_vol = 4.0 * math.pi * (5.0 ** 2) * 20.0
    expected_vol = orig_vol - total_hole_vol
    assert math.isclose(shape.Volume(), expected_vol, rel_tol=1e-3)


def test_hole_pattern_linear_invalid_count(base_plate: cq.Workplane):
    builder = HolePatternLinearBuilder()
    with pytest.raises(ValueError, match="count must be >= 1"):
        builder.build(base=base_plate, count=0, pitch=20.0, diameter=8.0)


def test_hole_pattern_circular_pcd_four_holes(base_disc: cq.Workplane):
    orig_vol = base_disc.val().Volume()
    builder = HolePatternCircularBuilder()
    # 4 holes of dia 12mm on PCD 100mm
    solid = builder.build(
        base=base_disc,
        pcd=100.0,
        count=4,
        diameter=12.0,
    )

    shape = solid.val()
    assert shape.isValid()
    # 4 holes * (pi * 6^2 * 15) = 4 * 540 * pi = 2160 * pi
    hole_vol = 4.0 * math.pi * (6.0 ** 2) * 15.0
    expected_vol = orig_vol - hole_vol
    assert math.isclose(shape.Volume(), expected_vol, rel_tol=1e-3)


def test_hole_pattern_circular_pcd_six_holes(base_disc: cq.Workplane):
    orig_vol = base_disc.val().Volume()
    builder = HolePatternCircularBuilder()
    solid = builder.build(
        base=base_disc,
        pcd=110.0,
        count=6,
        diameter=8.0,
    )
    shape = solid.val()
    assert shape.isValid()
    hole_vol = 6.0 * math.pi * (4.0 ** 2) * 15.0
    expected_vol = orig_vol - hole_vol
    assert math.isclose(shape.Volume(), expected_vol, rel_tol=1e-3)


def test_hole_pattern_grid_2x3(base_plate: cq.Workplane):
    orig_vol = base_plate.val().Volume()
    builder = HolePatternGridBuilder()
    # 2 x 3 = 6 holes of dia 10mm
    solid = builder.build(
        base=base_plate,
        x_count=2,
        y_count=3,
        x_spacing=80.0,
        y_spacing=50.0,
        diameter=10.0,
    )

    shape = solid.val()
    assert shape.isValid()
    total_holes_vol = 6.0 * math.pi * (5.0 ** 2) * 20.0
    expected_vol = orig_vol - total_holes_vol
    assert math.isclose(shape.Volume(), expected_vol, rel_tol=1e-3)


def test_hole_pattern_grid_invalid_count(base_plate: cq.Workplane):
    builder = HolePatternGridBuilder()
    with pytest.raises(ValueError, match="counts must be >= 1"):
        builder.build(base=base_plate, x_count=0, y_count=2, diameter=10.0)
