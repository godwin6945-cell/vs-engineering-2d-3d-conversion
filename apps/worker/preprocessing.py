"""
Phase 3 – Preprocessor Module
Handles DXF parsing, PDF vector extraction, image deskew/denoise,
multi-view detection, and cropping for the extraction pipeline.
"""

import io
import math
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

class InputFormat(str, Enum):
    DXF = "dxf"
    PDF = "pdf"
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"


@dataclass
class DXFEntity:
    """Parsed DXF geometry entity."""
    entity_type: str  # LINE, CIRCLE, ARC, DIMENSION, TEXT, MTEXT, LWPOLYLINE
    layer: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DXFDimension:
    """Structured DXF dimension entity."""
    dim_type: str  # LINEAR, ALIGNED, RADIAL, DIAMETRIC, ANGULAR
    value: Optional[float] = None
    text_override: Optional[str] = None
    insertion_point: Optional[Tuple[float, float]] = None
    defpoints: List[Tuple[float, float]] = field(default_factory=list)


@dataclass
class DXFParseResult:
    """Complete DXF parse output."""
    entities: List[DXFEntity] = field(default_factory=list)
    dimensions: List[DXFDimension] = field(default_factory=list)
    text_entities: List[Dict[str, Any]] = field(default_factory=list)
    bounding_box: Optional[Tuple[float, float, float, float]] = None  # xmin, ymin, xmax, ymax
    unit: str = "mm"


@dataclass
class ViewRegion:
    """Detected view region in an engineering drawing."""
    view_type: str  # front, top, side, isometric, detail, section, unknown
    bbox: Tuple[int, int, int, int]  # x, y, w, h in pixels
    image: Optional[np.ndarray] = None  # cropped image


@dataclass
class PreprocessResult:
    """Output of preprocessing for a single drawing file."""
    format: InputFormat
    images: List[np.ndarray] = field(default_factory=list)  # processed images (one per page/view)
    views: List[ViewRegion] = field(default_factory=list)
    dxf_data: Optional[DXFParseResult] = None
    pdf_text: Optional[str] = None
    original_size: Optional[Tuple[int, int]] = None  # (width, height)
    pages: int = 1
    warnings: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# DXF Parser
# ---------------------------------------------------------------------------

def parse_dxf(file_path: str) -> DXFParseResult:
    """
    Parse DXF file using ezdxf.
    Extracts lines, circles, arcs, dimensions, and text entities.
    """
    import ezdxf

    result = DXFParseResult()

    try:
        doc = ezdxf.readfile(file_path)
    except Exception as e:
        logger.error(f"Failed to parse DXF: {e}")
        result.entities.append(DXFEntity(entity_type="ERROR", attributes={"message": str(e)}))
        return result

    msp = doc.modelspace()

    # Detect units from header
    unit_map = {
        0: "unitless", 1: "in", 2: "ft", 3: "mi", 4: "mm",
        5: "cm", 6: "m", 7: "km", 8: "microinch", 9: "mil",
    }
    try:
        insunits = doc.header.get("$INSUNITS", 0)
        result.unit = unit_map.get(insunits, "mm")
    except Exception:
        result.unit = "mm"

    x_vals, y_vals = [], []

    for entity in msp:
        dxf_type = entity.dxftype()

        if dxf_type == "LINE":
            start = (entity.dxf.start.x, entity.dxf.start.y)
            end = (entity.dxf.end.x, entity.dxf.end.y)
            result.entities.append(DXFEntity(
                entity_type="LINE",
                layer=entity.dxf.layer,
                attributes={"start": start, "end": end}
            ))
            x_vals.extend([start[0], end[0]])
            y_vals.extend([start[1], end[1]])

        elif dxf_type == "CIRCLE":
            center = (entity.dxf.center.x, entity.dxf.center.y)
            result.entities.append(DXFEntity(
                entity_type="CIRCLE",
                layer=entity.dxf.layer,
                attributes={"center": center, "radius": entity.dxf.radius}
            ))
            x_vals.extend([center[0] - entity.dxf.radius, center[0] + entity.dxf.radius])
            y_vals.extend([center[1] - entity.dxf.radius, center[1] + entity.dxf.radius])

        elif dxf_type == "ARC":
            center = (entity.dxf.center.x, entity.dxf.center.y)
            result.entities.append(DXFEntity(
                entity_type="ARC",
                layer=entity.dxf.layer,
                attributes={
                    "center": center,
                    "radius": entity.dxf.radius,
                    "start_angle": entity.dxf.start_angle,
                    "end_angle": entity.dxf.end_angle,
                }
            ))
            x_vals.extend([center[0] - entity.dxf.radius, center[0] + entity.dxf.radius])
            y_vals.extend([center[1] - entity.dxf.radius, center[1] + entity.dxf.radius])

        elif dxf_type == "LWPOLYLINE":
            points = list(entity.get_points(format="xyb"))
            result.entities.append(DXFEntity(
                entity_type="LWPOLYLINE",
                layer=entity.dxf.layer,
                attributes={
                    "points": [(p[0], p[1]) for p in points],
                    "is_closed": entity.closed,
                }
            ))
            for p in points:
                x_vals.append(p[0])
                y_vals.append(p[1])

        elif dxf_type in ("DIMENSION", "ALIGNED_DIMENSION", "LINEAR_DIMENSION",
                          "RADIAL_DIMENSION", "DIAMETRIC_DIMENSION", "ANGULAR_DIMENSION"):
            dim = _parse_dimension_entity(entity, dxf_type)
            result.dimensions.append(dim)

        elif dxf_type in ("TEXT", "MTEXT"):
            text_data = _parse_text_entity(entity, dxf_type)
            result.text_entities.append(text_data)

    if x_vals and y_vals:
        result.bounding_box = (min(x_vals), min(y_vals), max(x_vals), max(y_vals))

    logger.info(
        f"DXF parsed: {len(result.entities)} entities, "
        f"{len(result.dimensions)} dimensions, "
        f"{len(result.text_entities)} text blocks"
    )
    return result


def _parse_dimension_entity(entity, dxf_type: str) -> DXFDimension:
    """Extract structured data from a DXF dimension entity."""
    dim = DXFDimension(dim_type=dxf_type.replace("_DIMENSION", "").upper())

    try:
        # Actual measurement value
        if hasattr(entity.dxf, "actual_measurement"):
            dim.value = round(entity.dxf.actual_measurement, 4)
    except Exception:
        pass

    try:
        if hasattr(entity.dxf, "text") and entity.dxf.text:
            text = entity.dxf.text
            if text != "<>":  # <> means use actual measurement
                dim.text_override = text
    except Exception:
        pass

    try:
        if hasattr(entity.dxf, "insert"):
            dim.insertion_point = (entity.dxf.insert.x, entity.dxf.insert.y)
    except Exception:
        pass

    try:
        if hasattr(entity.dxf, "defpoint"):
            dim.defpoints.append((entity.dxf.defpoint.x, entity.dxf.defpoint.y))
        if hasattr(entity.dxf, "defpoint2"):
            dim.defpoints.append((entity.dxf.defpoint2.x, entity.dxf.defpoint2.y))
        if hasattr(entity.dxf, "defpoint3"):
            dim.defpoints.append((entity.dxf.defpoint3.x, entity.dxf.defpoint3.y))
    except Exception:
        pass

    return dim


def _parse_text_entity(entity, dxf_type: str) -> Dict[str, Any]:
    """Extract text content and position from TEXT or MTEXT entity."""
    data: Dict[str, Any] = {"type": dxf_type, "layer": entity.dxf.layer}

    try:
        if dxf_type == "MTEXT":
            data["text"] = entity.text  # plain text content
        else:
            data["text"] = entity.dxf.text
    except Exception:
        data["text"] = ""

    try:
        if hasattr(entity.dxf, "insert"):
            data["position"] = (entity.dxf.insert.x, entity.dxf.insert.y)
        elif hasattr(entity.dxf, "align_point"):
            data["position"] = (entity.dxf.align_point.x, entity.dxf.align_point.y)
    except Exception:
        pass

    try:
        data["height"] = entity.dxf.height
    except Exception:
        pass

    return data


# ---------------------------------------------------------------------------
# PDF Extractor
# ---------------------------------------------------------------------------

def extract_pdf(file_path: str, dpi: int = 300) -> PreprocessResult:
    """
    Extract text + render each page at target DPI for vision model input.
    Uses pymupdf (not fitz) per deprecation guidance.
    """
    import pymupdf

    result = PreprocessResult(format=InputFormat.PDF)

    try:
        doc = pymupdf.open(file_path)
    except Exception as e:
        logger.error(f"Failed to open PDF: {e}")
        result.warnings.append(f"PDF open failed: {e}")
        return result

    result.pages = len(doc)
    all_text = []

    for page_num in range(len(doc)):
        page = doc[page_num]

        # Extract vector text
        text = page.get_text("text")
        all_text.append(text)

        # Render at target DPI
        zoom = dpi / 72.0
        mat = pymupdf.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)

        # Convert to numpy array
        img_data = pix.tobytes("png")
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is not None:
            result.images.append(img)
            if result.original_size is None:
                result.original_size = (img.shape[1], img.shape[0])

    doc.close()
    result.pdf_text = "\n---PAGE BREAK---\n".join(all_text)

    logger.info(f"PDF extracted: {result.pages} pages, {len(result.pdf_text)} chars of text")
    return result


# ---------------------------------------------------------------------------
# Image Preprocessor
# ---------------------------------------------------------------------------

def preprocess_image(
    image: np.ndarray,
    deskew: bool = True,
    denoise: bool = True,
    enhance_text: bool = True,
) -> np.ndarray:
    """
    Clean up a scanned/photographed engineering drawing image.
    Steps: deskew → denoise → contrast enhance.
    """
    result = image.copy()

    # Convert to grayscale for processing
    if len(result.shape) == 3:
        gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    else:
        gray = result.copy()

    # 1. Deskew using Hough lines
    if deskew:
        gray, angle = _deskew_image(gray)
        if len(result.shape) == 3 and abs(angle) > 0.1:
            h, w = result.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            result = cv2.warpAffine(result, M, (w, h),
                                     flags=cv2.INTER_CUBIC,
                                     borderMode=cv2.BORDER_REPLICATE)

    # 2. Denoise
    if denoise:
        if len(result.shape) == 3:
            result = cv2.fastNlMeansDenoisingColored(result, h=6, hForColoredComponents=6,
                                                       templateWindowSize=7, searchWindowSize=21)
        else:
            gray = cv2.fastNlMeansDenoising(gray, h=6, templateWindowSize=7, searchWindowSize=21)

    # 3. Enhance text regions for OCR
    if enhance_text:
        if len(result.shape) == 3:
            lab = cv2.cvtColor(result, cv2.COLOR_BGR2LAB)
            l_channel = lab[:, :, 0]
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            lab[:, :, 0] = clahe.apply(l_channel)
            result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    return result


def _deskew_image(gray: np.ndarray) -> Tuple[np.ndarray, float]:
    """
    Detect skew angle via Hough transform and correct it.
    Returns the corrected image and the detected angle.
    """
    # Edge detection
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Hough lines
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100,
                             minLineLength=100, maxLineGap=10)

    if lines is None or len(lines) == 0:
        return gray, 0.0

    # Compute angles of detected lines
    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        # Only consider near-horizontal and near-vertical lines
        if abs(angle) < 15 or abs(angle - 90) < 15 or abs(angle + 90) < 15:
            if abs(angle) < 15:
                angles.append(angle)

    if not angles:
        return gray, 0.0

    # Median angle for robustness
    median_angle = float(np.median(angles))

    if abs(median_angle) < 0.1:
        return gray, 0.0

    # Rotate to correct skew
    h, w = gray.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
    corrected = cv2.warpAffine(gray, M, (w, h),
                                flags=cv2.INTER_CUBIC,
                                borderMode=cv2.BORDER_REPLICATE)

    return corrected, median_angle


def upscale_region(image: np.ndarray, target_min_height: int = 64) -> np.ndarray:
    """
    Upscale a small text region so OCR can read it.
    Uses cubic interpolation for quality.
    """
    h, w = image.shape[:2]
    if h >= target_min_height:
        return image

    scale = target_min_height / h
    new_w = int(w * scale)
    new_h = int(h * scale)
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_CUBIC)


# ---------------------------------------------------------------------------
# View Detection
# ---------------------------------------------------------------------------

def detect_views(image: np.ndarray, min_area_ratio: float = 0.02) -> List[ViewRegion]:
    """
    Detect distinct view regions in an engineering drawing.
    Uses contour analysis to find rectangular regions separated by whitespace.
    """
    h, w = image.shape[:2]
    min_area = int(h * w * min_area_ratio)

    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Threshold to find drawn content
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    # Morphological close to merge nearby elements
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 30))
    closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    # Find contours
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    views = []
    for contour in contours:
        x, y, cw, ch = cv2.boundingRect(contour)
        area = cw * ch

        if area < min_area:
            continue

        # Classify view based on position (first-angle projection, ISO standard)
        view_type = _classify_view_position(x, y, cw, ch, w, h)

        crop = image[y:y+ch, x:x+cw].copy()
        views.append(ViewRegion(
            view_type=view_type,
            bbox=(x, y, cw, ch),
            image=crop,
        ))

    # Sort: largest views first
    views.sort(key=lambda v: v.bbox[2] * v.bbox[3], reverse=True)

    if not views:
        # If no views detected, treat the whole image as one view
        views.append(ViewRegion(
            view_type="front",
            bbox=(0, 0, w, h),
            image=image.copy(),
        ))

    logger.info(f"Detected {len(views)} views: {[v.view_type for v in views]}")
    return views


def _classify_view_position(
    x: int, y: int, w: int, h: int,
    img_w: int, img_h: int
) -> str:
    """
    Classify view type based on position in ISO first-angle projection layout.

    First-angle layout:
        [Side]  [Front]
                [Top]
    """
    cx = x + w / 2
    cy = y + h / 2

    # Normalize to [0,1]
    nx = cx / img_w
    ny = cy / img_h

    # Simple heuristic for common layouts
    if nx > 0.3 and nx < 0.7:
        if ny < 0.5:
            return "front"
        else:
            return "top"
    elif nx < 0.3:
        return "side"
    elif nx > 0.7:
        if ny < 0.5:
            return "side"
        else:
            return "isometric"

    return "unknown"


# ---------------------------------------------------------------------------
# Main Preprocessing Entry Point
# ---------------------------------------------------------------------------

def preprocess_drawing(
    file_path: str,
    file_format: Optional[str] = None,
    dpi: int = 300,
) -> PreprocessResult:
    """
    Main entry point: dispatch to format-specific handler, then
    preprocess images and detect views.
    """
    path = Path(file_path)

    if file_format is None:
        file_format = path.suffix.lstrip(".").lower()

    fmt = InputFormat(file_format.lower())

    if fmt == InputFormat.DXF:
        result = _preprocess_dxf(file_path)
    elif fmt == InputFormat.PDF:
        result = extract_pdf(file_path, dpi=dpi)
    else:
        result = _preprocess_raster(file_path)

    # Preprocess each image
    processed_images = []
    for img in result.images:
        processed = preprocess_image(img)
        processed_images.append(processed)
    result.images = processed_images

    # Detect views on the first (or largest) image
    if result.images:
        result.views = detect_views(result.images[0])

    return result


def _preprocess_dxf(file_path: str) -> PreprocessResult:
    """DXF-specific preprocessing: parse entities and generate a rasterized view."""
    result = PreprocessResult(format=InputFormat.DXF)
    result.dxf_data = parse_dxf(file_path)

    # For the vision model, we need a rasterized image.
    # Generate a simple rendering of the DXF geometry.
    img = _render_dxf_to_image(result.dxf_data)
    if img is not None:
        result.images.append(img)
        result.original_size = (img.shape[1], img.shape[0])

    return result


def _preprocess_raster(file_path: str) -> PreprocessResult:
    """PNG/JPG preprocessing."""
    result = PreprocessResult(format=InputFormat.PNG)

    img = cv2.imread(file_path)
    if img is None:
        result.warnings.append(f"Failed to read image: {file_path}")
        return result

    result.images.append(img)
    result.original_size = (img.shape[1], img.shape[0])
    return result


def _render_dxf_to_image(
    dxf_data: DXFParseResult,
    width: int = 2000,
    height: int = 1500,
    margin: int = 50,
) -> Optional[np.ndarray]:
    """
    Render parsed DXF entities onto a white image.
    This provides a visual representation for the Claude vision model.
    """
    if not dxf_data.entities and not dxf_data.dimensions:
        return None

    bb = dxf_data.bounding_box
    if bb is None:
        return None

    xmin, ymin, xmax, ymax = bb
    dx = xmax - xmin
    dy = ymax - ymin

    if dx <= 0 or dy <= 0:
        return None

    # Scale to fit canvas
    draw_w = width - 2 * margin
    draw_h = height - 2 * margin
    scale = min(draw_w / dx, draw_h / dy)

    img = np.ones((height, width, 3), dtype=np.uint8) * 255

    def to_px(x: float, y: float) -> Tuple[int, int]:
        px = int((x - xmin) * scale) + margin
        # Flip Y (DXF Y-up, image Y-down)
        py = height - (int((y - ymin) * scale) + margin)
        return (px, py)

    for entity in dxf_data.entities:
        if entity.entity_type == "LINE":
            start = to_px(*entity.attributes["start"])
            end = to_px(*entity.attributes["end"])
            cv2.line(img, start, end, (0, 0, 0), 1, cv2.LINE_AA)

        elif entity.entity_type == "CIRCLE":
            center = to_px(*entity.attributes["center"])
            radius = int(entity.attributes["radius"] * scale)
            if radius > 0:
                cv2.circle(img, center, radius, (0, 0, 0), 1, cv2.LINE_AA)

        elif entity.entity_type == "ARC":
            center = to_px(*entity.attributes["center"])
            radius = int(entity.attributes["radius"] * scale)
            if radius > 0:
                start_angle = entity.attributes["start_angle"]
                end_angle = entity.attributes["end_angle"]
                cv2.ellipse(img, center, (radius, radius), 0,
                           -end_angle, -start_angle, (0, 0, 0), 1, cv2.LINE_AA)

        elif entity.entity_type == "LWPOLYLINE":
            points = entity.attributes.get("points", [])
            if len(points) >= 2:
                pts = [to_px(p[0], p[1]) for p in points]
                for i in range(len(pts) - 1):
                    cv2.line(img, pts[i], pts[i+1], (0, 0, 0), 1, cv2.LINE_AA)
                if entity.attributes.get("is_closed"):
                    cv2.line(img, pts[-1], pts[0], (0, 0, 0), 1, cv2.LINE_AA)

    # Draw dimension text
    for text_ent in dxf_data.text_entities:
        pos = text_ent.get("position")
        text = text_ent.get("text", "")
        if pos and text:
            px_pos = to_px(pos[0], pos[1])
            cv2.putText(img, text, px_pos, cv2.FONT_HERSHEY_SIMPLEX,
                       0.4, (0, 0, 200), 1, cv2.LINE_AA)

    return img


def image_to_png_bytes(image: np.ndarray) -> bytes:
    """Convert a numpy image to PNG bytes for sending to Claude."""
    success, buffer = cv2.imencode(".png", image)
    if not success:
        raise ValueError("Failed to encode image to PNG")
    return buffer.tobytes()


def load_image_file(file_path: str) -> np.ndarray:
    """Load any image file into a numpy array."""
    img = cv2.imread(file_path)
    if img is None:
        raise ValueError(f"Cannot load image: {file_path}")
    return img
