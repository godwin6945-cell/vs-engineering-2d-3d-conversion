"""
Unit tests for CAD cavity builders: Slots, Rectangular/Circular/Obround Pockets, and Keyways.
"""

import math
import pytest
import cadquery as cq
from sketch2step_cad.builders.cuts_and_cavities import (
    KeywayBuilder,
    PocketCircleBuilder,
    PocketObroundBuilder,
    PocketRectBuilder,
    SlotBuilder,
)


@pytest.fixture
def base_solid() -> cq.Workplane:
    # 120 x 80 x 25 mm solid block
    return cq.Workplane("XY").box(120.0, 80.0, 25.0, centered=(True, True, False))


@pytest.fixture
def shaft_solid() -> cq.Workplane:
    # Shaft 40 mm dia x 100 mm long along Z
    return cq.Workplane("XY").circle(20.0).extrude(100.0)


def test_slot_through(base_solid: cq.Workplane):
    builder = SlotBuilder()
    solid = builder.build(base=base_solid, length=50.0, width=16.0, x=0.0, y=0.0)

    shape = solid.val()
    assert shape.isValid()
    assert shape.Volume() < base_solid.val().Volume()


def test_slot_blind_with_angle(base_solid: cq.Workplane):
    builder = SlotBuilder()
    solid = builder.build(
        base=base_solid,
        length=40.0,
        width=12.0,
        depth=10.0,
        angle=45.0,
        x=10.0,
        y=5.0,
    )
    assert solid.val().isValid()
    assert solid.val().Volume() < base_solid.val().Volume()


def test_pocket_rect(base_solid: cq.Workplane):
    orig_vol = base_solid.val().Volume()
    builder = PocketRectBuilder()
    # 60 x 40 x 10 mm rectangular pocket
    solid = builder.build(base=base_solid, length=60.0, width=40.0, depth=10.0)

    shape = solid.val()
    assert shape.isValid()
    # Pocket volume = 60 * 40 * 10 = 24000 mm3
    pocket_vol = 60.0 * 40.0 * 10.0
    expected_vol = orig_vol - pocket_vol
    assert math.isclose(shape.Volume(), expected_vol, rel_tol=1e-3)


def test_pocket_circle(base_solid: cq.Workplane):
    orig_vol = base_solid.val().Volume()
    builder = PocketCircleBuilder()
    # 30 mm dia x 8 mm deep circular pocket
    solid = builder.build(base=base_solid, diameter=30.0, depth=8.0)

    shape = solid.val()
    assert shape.isValid()
    pocket_vol = math.pi * (15.0 ** 2) * 8.0
    expected_vol = orig_vol - pocket_vol
    assert math.isclose(shape.Volume(), expected_vol, rel_tol=1e-3)


def test_pocket_obround(base_solid: cq.Workplane):
    builder = PocketObroundBuilder()
    solid = builder.build(base=base_solid, length=50.0, width=20.0, depth=12.0)
    assert solid.val().isValid()
    assert solid.val().Volume() < base_solid.val().Volume()


def test_keyway_builder(shaft_solid: cq.Workplane):
    builder = KeywayBuilder()
    # Keyway 8 mm wide x 4 mm deep x 30 mm long (standard DIN 6885 for dia 40)
    solid = builder.build(base=shaft_solid, width=8.0, depth=4.0, length=30.0, offset_z=20.0)
    assert solid.val().isValid()
    assert solid.val().Volume() < shaft_solid.val().Volume()


def test_cut_builder_requires_base():
    builder = PocketRectBuilder()
    with pytest.raises(ValueError, match="requires an existing base solid"):
        builder.build(base=None, length=20.0, width=10.0, depth=5.0)
