"""
Unit tests for the Visual Diff & Headless Orthographic Rendering Engine.
"""

import numpy as np
import pytest
import cadquery as cq
from sketch2step_cad.visual_diff import (
    compare_orthographic_to_drawing,
    np_image_to_data_uri,
    render_orthographic_views,
)


@pytest.fixture
def sample_box_solid():
    return (
        cq.Workplane("XY")
        .box(100.0, 60.0, 20.0)
        .faces(">Z")
        .hole(15.0)
    )


def test_render_orthographic_views(sample_box_solid):
    views = render_orthographic_views(sample_box_solid, image_size=(400, 300))
    assert "front" in views
    assert "top" in views
    assert "side" in views

    for name, img in views.items():
        assert isinstance(img, np.ndarray)
        assert img.shape == (300, 400, 3)
        # Check that canvas is not purely blank
        assert np.any(img < 255)


def test_np_image_to_data_uri():
    img = np.ones((50, 50, 3), dtype=np.uint8) * 128
    uri = np_image_to_data_uri(img)
    assert uri.startswith("data:image/png;base64,")
    assert len(uri) > 50


def test_compare_orthographic_to_drawing(sample_box_solid):
    views = render_orthographic_views(sample_box_solid, image_size=(400, 300))
    res = compare_orthographic_to_drawing(views)

    assert res.match_percentage >= 90.0
    assert len(res.identified_discrepancies) > 0
    assert "front" in res.rendered_ortho_urls
    assert res.rendered_ortho_urls["front"].startswith("data:image/png;base64,")
