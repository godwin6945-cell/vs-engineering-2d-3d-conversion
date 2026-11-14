"""
Unit tests for the Preprocessor module.
Verifies DXF parsing, image enhancement (deskew/denoise), and view detection.
"""

import os
import tempfile
import cv2
import ezdxf
import numpy as np
import pytest
from apps.worker.preprocessing import (
    _classify_view_position,
    _render_dxf_to_image,
    detect_views,
    parse_dxf,
    preprocess_drawing,
    preprocess_image,
    upscale_region,
)


@pytest.fixture
def sample_dxf_file():
    """Create a temporary DXF file with lines, circles, and text entities."""
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 4  # 4 = mm
    msp = doc.modelspace()

    # Add plate rectangle
    msp.add_line((0, 0), (100, 0))
    msp.add_line((100, 0), (100, 60))
    msp.add_line((100, 60), (0, 60))
    msp.add_line((0, 60), (0, 0))

    # Add a hole circle
    msp.add_circle((50, 30), radius=10)

    # Add a text label
    msp.add_text("100.0", dxfattribs={"insert": (50, -10), "height": 3.5})

    with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as f:
        temp_path = f.name

    doc.saveas(temp_path)
    yield temp_path

    if os.path.exists(temp_path):
        os.remove(temp_path)


def test_parse_dxf_entities(sample_dxf_file):
    res = parse_dxf(sample_dxf_file)
    assert res.unit == "mm"
    assert len(res.entities) >= 5  # 4 lines + 1 circle
    assert any(e.entity_type == "CIRCLE" for e in res.entities)
    assert any(e.entity_type == "LINE" for e in res.entities)
    assert len(res.text_entities) >= 1
    assert res.text_entities[0]["text"] == "100.0"
    assert res.bounding_box is not None
    xmin, ymin, xmax, ymax = res.bounding_box
    assert xmin <= 0 and xmax >= 100


def test_render_dxf_to_image(sample_dxf_file):
    dxf_data = parse_dxf(sample_dxf_file)
    img = _render_dxf_to_image(dxf_data, width=800, height=600)
    assert img is not None
    assert img.shape == (600, 800, 3)
    # Check that drawing is rendered (not pure white)
    assert np.any(img < 255)


def test_preprocess_image_clean():
    # Create white canvas with a black line
    img = np.ones((400, 600, 3), dtype=np.uint8) * 255
    cv2.line(img, (50, 200), (550, 200), (0, 0, 0), 2)

    processed = preprocess_image(img, deskew=True, denoise=False)
    assert processed.shape == img.shape


def test_upscale_region():
    small = np.ones((20, 40, 3), dtype=np.uint8) * 255
    upscaled = upscale_region(small, target_min_height=64)
    assert upscaled.shape[0] >= 64
    assert upscaled.shape[1] > 40


def test_detect_views_synthetic():
    # Create an image with two distinct drawing view boxes
    canvas = np.ones((1000, 1000, 3), dtype=np.uint8) * 255
    # Front view (center top)
    cv2.rectangle(canvas, (350, 100), (650, 400), (0, 0, 0), 3)
    # Top view (center bottom)
    cv2.rectangle(canvas, (350, 550), (650, 850), (0, 0, 0), 3)

    views = detect_views(canvas, min_area_ratio=0.02)
    assert len(views) >= 2
    types = [v.view_type for v in views]
    assert "front" in types or "top" in types


def test_classify_view_position():
    assert _classify_view_position(x=500, y=100, w=200, h=200, img_w=1200, img_h=1000) == "front"
    assert _classify_view_position(x=500, y=700, w=200, h=200, img_w=1200, img_h=1000) == "top"
    assert _classify_view_position(x=50, y=200, w=150, h=150, img_w=1200, img_h=1000) == "side"
