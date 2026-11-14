"""
Phase 3 – OCR Cross-Check Module
Independent second reader using RapidOCR to verify dimension values
extracted by Claude. Provides the third leg of the triple-verification.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data Types
# ---------------------------------------------------------------------------

@dataclass
class OCRReading:
    """A single OCR text detection with its location and parsed numeric value."""
    text: str
    confidence: float  # 0.0 to 1.0
    bbox: Tuple[int, int, int, int]  # x, y, w, h in pixels
    numeric_value: Optional[float] = None
    is_dimension: bool = False


@dataclass
class OCRResult:
    """Complete OCR scan result for a drawing image."""
    readings: List[OCRReading] = field(default_factory=list)
    dimension_readings: List[OCRReading] = field(default_factory=list)
    raw_text_blocks: List[Dict[str, Any]] = field(default_factory=list)
    engine: str = "rapidocr"
    processing_time_ms: float = 0.0


# ---------------------------------------------------------------------------
# Dimension Text Patterns
# ---------------------------------------------------------------------------

# Patterns that look like engineering dimensions
DIMENSION_PATTERNS = [
    # Basic numeric: 12.5, 100, 0.75
    re.compile(r"^(\d+\.?\d*)$"),
    # Diameter: Ø12.5, ⌀12.5, %%c12.5
    re.compile(r"^[Øø⌀]?\s*(\d+\.?\d*)$"),
    # Radius: R12.5
    re.compile(r"^[Rr]\s*(\d+\.?\d*)$"),
    # Thread: M8, M8x1.25, M8×1.25
    re.compile(r"^[Mm](\d+\.?\d*)(?:\s*[x×]\s*(\d+\.?\d*))?$"),
    # Tolerance: 12.5 ±0.1, 12.5+0.1/-0.05
    re.compile(r"^(\d+\.?\d*)\s*[±]\s*(\d+\.?\d*)$"),
    re.compile(r"^(\d+\.?\d*)\s*\+\s*(\d+\.?\d*)\s*/?\s*-\s*(\d+\.?\d*)$"),
    # Angle: 45°, 90°
    re.compile(r"^(\d+\.?\d*)\s*°$"),
    # Countersink/counterbore: ⌴12.5, ∨12.5
    re.compile(r"^[⌴∨]\s*(\d+\.?\d*)$"),
]


def parse_dimension_value(text: str) -> Optional[float]:
    """
    Try to parse a numeric dimension value from OCR text.
    Returns None if the text doesn't look like a dimension.
    """
    text = text.strip()

    # Remove common OCR noise
    text = text.replace(",", ".")  # European decimal
    text = text.replace("O", "0")  # Common OCR confusion
    text = text.replace("l", "1")  # Common OCR confusion in dimension context
    text = text.replace(" ", "")

    for pattern in DIMENSION_PATTERNS:
        match = pattern.match(text)
        if match:
            try:
                return float(match.group(1))
            except (ValueError, IndexError):
                continue

    # Last resort: try direct float parse
    try:
        val = float(text)
        if 0.01 <= abs(val) <= 10000:  # reasonable dimension range
            return val
    except ValueError:
        pass

    return None


# ---------------------------------------------------------------------------
# OCR Engine
# ---------------------------------------------------------------------------

class OCREngine:
    """
    RapidOCR-based engine for reading dimension text from engineering drawings.
    Provides independent verification separate from Claude extraction.
    """

    def __init__(self):
        self._engine = None

    def _get_engine(self):
        """Lazy-initialize the RapidOCR engine."""
        if self._engine is None:
            from rapidocr_onnxruntime import RapidOCR
            self._engine = RapidOCR()
        return self._engine

    def scan_full_image(self, image: np.ndarray) -> OCRResult:
        """
        Run OCR on the entire drawing image.
        Returns all text detections with dimension parsing.
        """
        import time
        start = time.time()

        engine = self._get_engine()
        result = OCRResult()

        # Run OCR
        try:
            ocr_result, elapsed = engine(image)
        except Exception as e:
            logger.error(f"OCR engine error: {e}")
            result.processing_time_ms = (time.time() - start) * 1000
            return result

        if ocr_result is None:
            result.processing_time_ms = (time.time() - start) * 1000
            return result

        # Process results
        for detection in ocr_result:
            # RapidOCR returns: [bbox_points, text, confidence]
            bbox_points, text, confidence = detection

            # Convert polygon bbox to (x, y, w, h)
            pts = np.array(bbox_points, dtype=np.int32)
            x = int(pts[:, 0].min())
            y = int(pts[:, 1].min())
            w = int(pts[:, 0].max()) - x
            h = int(pts[:, 1].max()) - y

            reading = OCRReading(
                text=text.strip(),
                confidence=float(confidence),
                bbox=(x, y, w, h),
            )

            # Try to parse as dimension
            numeric = parse_dimension_value(text)
            if numeric is not None:
                reading.numeric_value = numeric
                reading.is_dimension = True
                result.dimension_readings.append(reading)

            result.readings.append(reading)
            result.raw_text_blocks.append({
                "text": text,
                "confidence": confidence,
                "bbox": (x, y, w, h),
                "bbox_points": bbox_points,
            })

        result.processing_time_ms = (time.time() - start) * 1000

        logger.info(
            f"OCR scan complete: {len(result.readings)} text blocks, "
            f"{len(result.dimension_readings)} dimension candidates "
            f"({result.processing_time_ms:.0f}ms)"
        )

        return result

    def scan_region(
        self,
        image: np.ndarray,
        x: int, y: int, w: int, h: int,
        padding: int = 10,
    ) -> List[OCRReading]:
        """
        Scan a specific region of the image for dimension text.
        Used to verify a specific dimension location reported by Claude.
        """
        img_h, img_w = image.shape[:2]

        # Apply padding and clamp
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(img_w, x + w + padding)
        y2 = min(img_h, y + h + padding)

        crop = image[y1:y2, x1:x2]

        if crop.size == 0:
            return []

        # Upscale small regions for better OCR
        crop_h = crop.shape[0]
        if crop_h < 32:
            scale = 64 / crop_h
            crop = cv2.resize(crop, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

        result = self.scan_full_image(crop)
        return result.dimension_readings

    def read_dimension_at_bbox(
        self,
        image: np.ndarray,
        bbox_norm: Tuple[float, float, float, float],
    ) -> Optional[float]:
        """
        Read a dimension value at a normalized bounding box position.
        bbox_norm: (x_min, y_min, x_max, y_max) in [0, 1] range.
        Returns the numeric value or None.
        """
        h, w = image.shape[:2]
        x_min, y_min, x_max, y_max = bbox_norm

        px_x = int(x_min * w)
        px_y = int(y_min * h)
        px_w = int((x_max - x_min) * w)
        px_h = int((y_max - y_min) * h)

        readings = self.scan_region(image, px_x, px_y, px_w, px_h, padding=20)

        if not readings:
            return None

        # Return the highest-confidence dimension reading
        best = max(readings, key=lambda r: r.confidence)
        return best.numeric_value


def match_ocr_to_dimensions(
    ocr_result: OCRResult,
    claude_dimensions: List[Dict[str, Any]],
    image_width: int,
    image_height: int,
    match_radius_px: int = 80,
) -> Dict[str, Optional[float]]:
    """
    Match OCR dimension readings to Claude-extracted dimensions by spatial proximity.

    Returns a dict mapping dimension_id → OCR numeric value (or None if no match).
    """
    matches: Dict[str, Optional[float]] = {}

    for dim in claude_dimensions:
        dim_id = dim.get("id", "")
        bbox = dim.get("bbox")

        if bbox is None:
            matches[dim_id] = None
            continue

        # Convert normalized bbox to pixel center
        dim_cx = ((bbox.get("x_min", 0) + bbox.get("x_max", 0)) / 2) * image_width
        dim_cy = ((bbox.get("y_min", 0) + bbox.get("y_max", 0)) / 2) * image_height

        best_match: Optional[float] = None
        best_dist = float("inf")

        for reading in ocr_result.dimension_readings:
            rx, ry, rw, rh = reading.bbox
            rcx = rx + rw / 2
            rcy = ry + rh / 2

            dist = ((dim_cx - rcx) ** 2 + (dim_cy - rcy) ** 2) ** 0.5

            if dist < match_radius_px and dist < best_dist:
                best_dist = dist
                best_match = reading.numeric_value

        matches[dim_id] = best_match

    return matches
