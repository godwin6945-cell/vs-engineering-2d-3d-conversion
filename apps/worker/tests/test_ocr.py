"""
Unit tests for the OCR module.
Verifies dimension regex parsing and spatial bounding box matching.
"""

import pytest
from apps.worker.ocr import (
    OCRReading,
    OCRResult,
    match_ocr_to_dimensions,
    parse_dimension_value,
)


def test_parse_dimension_value_basic_numbers():
    assert parse_dimension_value("100") == 100.0
    assert parse_dimension_value("12.5") == 12.5
    assert parse_dimension_value("0.75") == 0.75
    assert parse_dimension_value("12,5") == 12.5  # European comma decimal


def test_parse_dimension_value_diameter_symbols():
    assert parse_dimension_value("Ø25") == 25.0
    assert parse_dimension_value("ø16.5") == 16.5
    assert parse_dimension_value("⌀30") == 30.0


def test_parse_dimension_value_radius():
    assert parse_dimension_value("R5") == 5.0
    assert parse_dimension_value("R12.5") == 12.5
    assert parse_dimension_value("r2.0") == 2.0


def test_parse_dimension_value_threads():
    assert parse_dimension_value("M8") == 8.0
    assert parse_dimension_value("M10x1.5") == 10.0
    assert parse_dimension_value("M16×2.0") == 16.0


def test_parse_dimension_value_tolerance():
    assert parse_dimension_value("50±0.1") == 50.0
    assert parse_dimension_value("100+0.05/-0.02") == 100.0


def test_parse_dimension_value_non_dimension():
    assert parse_dimension_value("TITLE BLOCK") is None
    assert parse_dimension_value("DRAWN BY:") is None
    assert parse_dimension_value("STEEL") is None


def test_match_ocr_to_dimensions_spatial():
    """Verify spatial proximity matching connects OCR reading to correct dimension."""
    ocr_res = OCRResult(
        dimension_readings=[
            OCRReading(
                text="100.0",
                confidence=0.98,
                bbox=(190, 95, 30, 15),  # center ~ (205, 102)
                numeric_value=100.0,
                is_dimension=True,
            ),
            OCRReading(
                text="50.0",
                confidence=0.95,
                bbox=(490, 290, 25, 15),  # center ~ (502, 297)
                numeric_value=50.0,
                is_dimension=True,
            ),
        ]
    )

    # 1000 x 1000 image
    claude_dims = [
        {
            "id": "d_len",
            "bbox": {"x_min": 0.18, "y_min": 0.08, "x_max": 0.23, "y_max": 0.12},  # center (205, 100)
        },
        {
            "id": "d_wid",
            "bbox": {"x_min": 0.48, "y_min": 0.28, "x_max": 0.53, "y_max": 0.32},  # center (505, 300)
        },
        {
            "id": "d_far",
            "bbox": {"x_min": 0.8, "y_min": 0.8, "x_max": 0.9, "y_max": 0.9},  # far away
        },
    ]

    matches = match_ocr_to_dimensions(
        ocr_res, claude_dims, image_width=1000, image_height=1000, match_radius_px=50
    )

    assert matches["d_len"] == 100.0
    assert matches["d_wid"] == 50.0
    assert matches["d_far"] is None
