"""
Unit tests for CAD hole builders: Through, Blind, Counterbore, Countersink.
"""

import math
import pytest
import cadquery as cq
from sketch2step_cad.builders.holes import (
    HoleBlindBuilder,
    HoleCounterboreBuilder,
    HoleCountersinkBuilder,
    HoleThroughBuilder,
)


@pytest.fixture
def base_block() -> cq.Workplane:
    # 100 x 100 x 20 mm block (centered in XY, Z from 0 to 20)
    return cq.Workplane("XY").box(100.0, 100.0, 20.0, centered=(True, True, False))


def test_hole_through(base_block: cq.Workplane):
    orig_vol = base_block.val().Volume()
    builder = HoleThroughBuilder()
    solid = builder.build(base=base_block, diameter=20.0, x=0.0, y=0.0)

    shape = solid.val()
    assert shape.isValid()
    # Hole volume = pi * 10^2 * 20 = 2000 * pi
    hole_vol = math.pi * (10.0 ** 2) * 20.0
    expected_vol = orig_vol - hole_vol
    assert math.isclose(shape.Volume(), expected_vol, rel_tol=1e-3)


def test_hole_through_offset_coords(base_block: cq.Workplane):
    builder = HoleThroughBuilder()
    solid = builder.build(base=base_block, diameter=10.0, x=25.0, y=25.0)
    assert solid.val().isValid()


def test_hole_blind(base_block: cq.Workplane):
    orig_vol = base_block.val().Volume()
    builder = HoleBlindBuilder()
    solid = builder.build(base=base_block, diameter=16.0, depth=10.0, x=0.0, y=0.0)

    shape = solid.val()
    assert shape.isValid()
    # Hole volume = pi * 8^2 * 10 = 640 * pi
    hole_vol = math.pi * (8.0 ** 2) * 10.0
    expected_vol = orig_vol - hole_vol
    assert math.isclose(shape.Volume(), expected_vol, rel_tol=1e-3)


def test_hole_counterbore_through(base_block: cq.Workplane):
    orig_vol = base_block.val().Volume()
    builder = HoleCounterboreBuilder()
    # Hole 10mm through (20mm deep), cbore 18mm x 6mm deep
    solid = builder.build(
        base=base_block,
        diameter=10.0,
        cbore_diameter=18.0,
        cbore_depth=6.0,
        x=0.0,
        y=0.0,
    )

    shape = solid.val()
    assert shape.isValid()
    # Upper cbore volume: pi * 9^2 * 6 = 486 * pi
    # Lower hole volume: pi * 5^2 * (20 - 6) = 350 * pi
    hole_vol = math.pi * (9.0 ** 2) * 6.0 + math.pi * (5.0 ** 2) * 14.0
    expected_vol = orig_vol - hole_vol
    assert math.isclose(shape.Volume(), expected_vol, rel_tol=1e-3)


def test_hole_counterbore_invalid_diameter(base_block: cq.Workplane):
    builder = HoleCounterboreBuilder()
    with pytest.raises(ValueError, match="must be greater than hole diameter"):
        builder.build(base=base_block, diameter=20.0, cbore_diameter=15.0, cbore_depth=5.0)


def test_hole_countersink(base_block: cq.Workplane):
    builder = HoleCountersinkBuilder()
    solid = builder.build(
        base=base_block,
        diameter=10.0,
        csink_diameter=16.0,
        csink_angle=90.0,
        x=0.0,
        y=0.0,
    )
    assert solid.val().isValid()
    assert solid.val().Volume() < base_block.val().Volume()


def test_hole_countersink_invalid_diameter(base_block: cq.Workplane):
    builder = HoleCountersinkBuilder()
    with pytest.raises(ValueError, match="must be greater than hole diameter"):
        builder.build(base=base_block, diameter=15.0, csink_diameter=12.0)


def test_hole_builder_requires_base_solid():
    builder = HoleThroughBuilder()
    with pytest.raises(ValueError, match="requires an existing base solid"):
        builder.build(base=None, diameter=10.0)
