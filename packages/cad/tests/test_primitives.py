"""
Unit tests for CAD primitive feature builders: Plate, Block, Cylinder, Stepped Shaft.
"""

import math
import pytest
from sketch2step_cad.builders.primitives import (
    BlockBuilder,
    CylinderBuilder,
    PlateBuilder,
    SteppedShaftBuilder,
)


def test_plate_builder_volume_and_bounds():
    builder = PlateBuilder()
    solid = builder.build(length=100.0, width=50.0, thickness=10.0)

    shape = solid.val()
    assert shape.isValid()
    # Expected Volume = 100 * 50 * 10 = 50,000 mm3
    assert math.isclose(shape.Volume(), 50000.0, rel_tol=1e-3)

    bb = shape.BoundingBox()
    assert math.isclose(bb.xlen, 100.0, rel_tol=1e-3)
    assert math.isclose(bb.ylen, 50.0, rel_tol=1e-3)
    assert math.isclose(bb.zlen, 10.0, rel_tol=1e-3)


def test_plate_builder_invalid_negative_dimensions():
    builder = PlateBuilder()
    with pytest.raises(ValueError, match="strictly greater than 0"):
        builder.build(length=-10.0, width=50.0, thickness=10.0)

    with pytest.raises(ValueError, match="strictly greater than 0"):
        builder.build(length=100.0, width=0.0, thickness=10.0)


def test_block_builder_dimensions():
    builder = BlockBuilder()
    solid = builder.build(length=40.0, width=30.0, height=20.0)

    shape = solid.val()
    assert shape.isValid()
    assert math.isclose(shape.Volume(), 24000.0, rel_tol=1e-3)

    bb = shape.BoundingBox()
    assert math.isclose(bb.xlen, 40.0, rel_tol=1e-3)
    assert math.isclose(bb.ylen, 30.0, rel_tol=1e-3)
    assert math.isclose(bb.zlen, 20.0, rel_tol=1e-3)


def test_cylinder_builder_by_diameter():
    builder = CylinderBuilder()
    solid = builder.build(diameter=20.0, height=50.0)

    shape = solid.val()
    assert shape.isValid()
    # Expected volume = pi * r^2 * h = pi * 10^2 * 50 = 5000 * pi ~= 15707.96 mm3
    expected_vol = math.pi * (10.0 ** 2) * 50.0
    assert math.isclose(shape.Volume(), expected_vol, rel_tol=1e-3)

    bb = shape.BoundingBox()
    assert math.isclose(bb.xlen, 20.0, rel_tol=1e-3)
    assert math.isclose(bb.ylen, 20.0, rel_tol=1e-3)
    assert math.isclose(bb.zlen, 50.0, rel_tol=1e-3)


def test_cylinder_builder_by_radius():
    builder = CylinderBuilder()
    solid = builder.build(radius=15.0, height=30.0)

    shape = solid.val()
    assert shape.isValid()
    expected_vol = math.pi * (15.0 ** 2) * 30.0
    assert math.isclose(shape.Volume(), expected_vol, rel_tol=1e-3)


def test_cylinder_builder_missing_radius_and_diameter():
    builder = CylinderBuilder()
    with pytest.raises(ValueError, match="requires either 'diameter' or 'radius'"):
        builder.build(height=25.0)


def test_stepped_shaft_builder_two_steps():
    builder = SteppedShaftBuilder()
    steps = [
        {"diameter": 30.0, "length": 40.0},
        {"diameter": 20.0, "length": 60.0},
    ]
    solid = builder.build(steps=steps)

    shape = solid.val()
    assert shape.isValid()
    # Expected Volume = pi * 15^2 * 40 + pi * 10^2 * 60 = 9000*pi + 6000*pi = 15000*pi
    expected_vol = math.pi * (15.0 ** 2) * 40.0 + math.pi * (10.0 ** 2) * 60.0
    assert math.isclose(shape.Volume(), expected_vol, rel_tol=1e-3)

    bb = shape.BoundingBox()
    assert math.isclose(bb.xlen, 30.0, rel_tol=1e-3)
    assert math.isclose(bb.zlen, 100.0, rel_tol=1e-3)


def test_stepped_shaft_builder_empty_steps():
    builder = SteppedShaftBuilder()
    with pytest.raises(ValueError, match="non-empty list of 'steps'"):
        builder.build(steps=[])
