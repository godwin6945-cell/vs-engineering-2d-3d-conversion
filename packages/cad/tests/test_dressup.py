"""
Unit tests for CAD dress-up features: Bosses, Fillets, Chamfers, and Threads.
"""

import math
import pytest
import cadquery as cq
from sketch2step_cad.builders.dressup import (
    BossBuilder,
    ChamferBuilder,
    FilletBuilder,
    ThreadCosmeticBuilder,
    ThreadModelledBuilder,
)


@pytest.fixture
def base_block() -> cq.Workplane:
    # 80 x 60 x 30 mm block
    return cq.Workplane("XY").box(80.0, 60.0, 30.0, centered=(True, True, False))


def test_boss_circular(base_block: cq.Workplane):
    orig_vol = base_block.val().Volume()
    builder = BossBuilder()
    # Circular boss 24 mm dia x 15 mm high
    solid = builder.build(base=base_block, diameter=24.0, height=15.0)

    shape = solid.val()
    assert shape.isValid()
    boss_vol = math.pi * (12.0 ** 2) * 15.0
    expected_vol = orig_vol + boss_vol
    assert math.isclose(shape.Volume(), expected_vol, rel_tol=1e-3)


def test_boss_rectangular(base_block: cq.Workplane):
    orig_vol = base_block.val().Volume()
    builder = BossBuilder()
    solid = builder.build(base=base_block, length=30.0, width=20.0, height=10.0)

    shape = solid.val()
    assert shape.isValid()
    expected_vol = orig_vol + (30.0 * 20.0 * 10.0)
    assert math.isclose(shape.Volume(), expected_vol, rel_tol=1e-3)


def test_fillet_builder(base_block: cq.Workplane):
    builder = FilletBuilder()
    solid = builder.build(base=base_block, radius=4.0, edge_selector="|Z")

    shape = solid.val()
    assert shape.isValid()
    # Filleting vertical edges reduces volume slightly
    assert shape.Volume() < base_block.val().Volume()


def test_chamfer_builder(base_block: cq.Workplane):
    builder = ChamferBuilder()
    solid = builder.build(base=base_block, length=2.0, edge_selector=">Z")

    shape = solid.val()
    assert shape.isValid()
    assert shape.Volume() < base_block.val().Volume()


def test_thread_cosmetic_iso_sizes(base_block: cq.Workplane):
    builder = ThreadCosmeticBuilder()
    # M8 metric tap drill is 6.8 mm dia (depth 20 mm)
    solid = builder.build(base=base_block, thread_callout="M8", depth=20.0)

    shape = solid.val()
    assert shape.isValid()
    tap_drill_vol = math.pi * (3.4 ** 2) * 20.0
    expected_vol = base_block.val().Volume() - tap_drill_vol
    assert math.isclose(shape.Volume(), expected_vol, rel_tol=1e-3)


def test_thread_cosmetic_unsupported_size(base_block: cq.Workplane):
    builder = ThreadCosmeticBuilder()
    with pytest.raises(ValueError, match="Unsupported ISO metric thread"):
        builder.build(base=base_block, thread_callout="M999")
