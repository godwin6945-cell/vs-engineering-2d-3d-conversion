"""
Phase 3 – AI Extraction Module
Dual-pass Claude extraction using tool use / structured outputs.
Each pass independently extracts dimensions from the drawing image
into a structured DrawingSpec schema.
"""

import base64
import hashlib
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from sketch2step_spec.drawing import (
    BoundingBox,
    DimensionEvidence,
    DimensionSpec,
    DrawingSpec,
    FeatureSpec,
)
from sketch2step_spec.enums import (
    DimensionSource,
    DimensionStatus,
    DimensionType,
    FeatureType,
    ViewType,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool schemas for Claude structured extraction
# ---------------------------------------------------------------------------

DIMENSION_TOOL = {
    "name": "record_dimension",
    "description": (
        "Record a single dimension read from the engineering drawing. "
        "Call this once per distinct dimension visible on the drawing."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "description": "Unique dimension ID, e.g. 'dim_01', 'dim_02'",
            },
            "name": {
                "type": "string",
                "description": "Descriptive name, e.g. 'Overall Length', 'Hole 1 Diameter'",
            },
            "value": {
                "type": "number",
                "description": "Numeric value of the dimension. Use null if unreadable.",
            },
            "unit": {
                "type": "string",
                "enum": ["mm", "in", "deg"],
                "description": "Unit of measurement",
            },
            "type": {
                "type": "string",
                "enum": ["linear", "diameter", "radius", "angle", "depth", "thread"],
                "description": "Dimension type",
            },
            "source": {
                "type": "string",
                "enum": ["printed", "inferred", "missing"],
                "description": "'printed' if clearly marked on drawing, 'inferred' if deduced, 'missing' if expected but not shown",
            },
            "confidence": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0,
                "description": "Confidence in the reading (0.0 to 1.0)",
            },
            "view": {
                "type": "string",
                "enum": ["front", "top", "side", "isometric", "detail", "section", "unknown"],
                "description": "Which view the dimension appears in",
            },
            "bbox_x_min": {"type": "number", "description": "Normalized left coordinate [0-1]"},
            "bbox_y_min": {"type": "number", "description": "Normalized top coordinate [0-1]"},
            "bbox_x_max": {"type": "number", "description": "Normalized right coordinate [0-1]"},
            "bbox_y_max": {"type": "number", "description": "Normalized bottom coordinate [0-1]"},
            "tol_plus": {"type": "number", "description": "Upper tolerance. Default 0."},
            "tol_minus": {"type": "number", "description": "Lower tolerance (positive number). Default 0."},
            "notes": {"type": "string", "description": "Any notes about this dimension"},
        },
        "required": ["id", "name", "value", "unit", "type", "source", "confidence", "view"],
    },
}

FEATURE_TOOL = {
    "name": "record_feature",
    "description": (
        "Record a CAD feature identified from the drawing. "
        "Call once per distinct feature (base shape, hole, pattern, etc.)."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "description": "Feature ID, e.g. 'feat_base_01', 'feat_hole_01'",
            },
            "type": {
                "type": "string",
                "enum": [e.value for e in FeatureType],
                "description": "CAD feature type",
            },
            "dimension_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "IDs of dimensions that drive this feature",
            },
            "parameters": {
                "type": "object",
                "description": "Resolved parameters (e.g. {length: 100, width: 50, height: 20})",
            },
            "parent_feature_id": {
                "type": "string",
                "description": "ID of parent feature if this is a sub-feature (e.g. hole on a plate)",
            },
        },
        "required": ["id", "type", "dimension_ids", "parameters"],
    },
}

METADATA_TOOL = {
    "name": "record_drawing_metadata",
    "description": (
        "Record global drawing metadata: drawing number, title, revision, "
        "material, general tolerance, and any notes or ambiguities."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "drawing_number": {"type": "string"},
            "title": {"type": "string"},
            "revision": {"type": "string"},
            "unit": {"type": "string", "enum": ["mm", "in"]},
            "material": {"type": "string"},
            "general_tolerance": {"type": "string", "description": "e.g. 'ISO 2768-m'"},
            "notes": {
                "type": "array",
                "items": {"type": "string"},
                "description": "General drawing notes",
            },
            "ambiguities": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Anything unclear, missing, or contradictory in the drawing",
            },
        },
        "required": [],
    },
}

EXTRACTION_TOOLS = [DIMENSION_TOOL, FEATURE_TOOL, METADATA_TOOL]


# ---------------------------------------------------------------------------
# Prompt Templates
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_PASS_A = """You are a senior mechanical engineer performing precise dimension extraction from an engineering drawing.

TASK:
Carefully examine the engineering drawing image and extract EVERY dimension, feature, and piece of metadata visible.

RULES:
1. Call `record_dimension` once for EACH distinct dimension shown on the drawing.
2. Call `record_feature` for each identifiable CAD feature (base shape, holes, fillets, chamfers, threads, patterns, slots, pockets).
3. Call `record_drawing_metadata` once for the title block info and notes.
4. Read dimension values EXACTLY as printed. Do NOT round or estimate.
5. If a dimension is partially obscured or unclear, set source='inferred' and confidence < 0.7.
6. If a dimension is expected but missing from the drawing, set source='missing', value=null, confidence=0.
7. Pay attention to:
   - Tolerances (±values, limit dimensions)
   - Thread callouts (M8×1.25, etc.)
   - Surface finish symbols
   - Geometric tolerances (GD&T)
   - Section views and detail views
   - Hole patterns (PCD, linear, grid)
8. Use ISO metric standards (mm) unless the drawing clearly uses inches.
9. Provide bounding box coordinates (normalized 0-1) where each dimension label appears on the image.
10. NEVER guess a value. If you can't read it clearly, flag it.

Start by examining the drawing systematically: title block → overall dimensions → features → details."""

SYSTEM_PROMPT_PASS_B = """You are a quality assurance inspector verifying dimension readings from an engineering drawing.

TASK:
Independently extract ALL dimensions, features, and metadata from the engineering drawing. This is a verification pass — be extra meticulous.

APPROACH:
1. Start from the BOTTOM-RIGHT (title block) and work LEFT and UP.
2. Count dimensions visible in each view before extracting them.
3. Cross-reference between views: a diameter in the front view should correspond to a circle in the top view.
4. Verify feature counts: count holes, fillets, chamfers before recording.

RULES:
1. Call `record_dimension` for EVERY dimension on the drawing — do not skip any.
2. Call `record_feature` for each CAD feature you identify.
3. Call `record_drawing_metadata` for title block and notes.
4. Read values EXACTLY as printed. If ambiguous between two values (e.g., is it 25 or 2.5?), set confidence < 0.5 and note the ambiguity.
5. Check for:
   - Missing dimensions that would be needed to fully define the part
   - Inconsistent dimensions (e.g., overall doesn't match sum of segments)
   - Standard thread sizes per ISO metric
   - Correct tolerance interpretation
6. Source classification:
   - 'printed': clearly shown with dimension line and value
   - 'inferred': deduced from other dimensions or geometry
   - 'missing': needed but not shown
7. Provide normalized bounding box coordinates for dimension locations.
8. Flag ANY ambiguity or uncertainty in notes or the ambiguities list."""


# ---------------------------------------------------------------------------
# Extraction Engine
# ---------------------------------------------------------------------------

class ExtractionEngine:
    """
    Runs Claude extraction passes with tool use.
    No free-text JSON parsing — all structured data comes through tool calls.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 8192,
    ):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    def extract_pass(
        self,
        image_bytes: bytes,
        image_media_type: str = "image/png",
        system_prompt: str = SYSTEM_PROMPT_PASS_A,
        dxf_context: Optional[str] = None,
        pdf_text: Optional[str] = None,
    ) -> DrawingSpec:
        """
        Run a single extraction pass using Claude tool use.
        Returns a DrawingSpec populated from the tool calls.
        """
        # Build message content
        content: List[Dict[str, Any]] = []

        # Image
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": image_media_type,
                "data": image_b64,
            },
        })

        # Additional context
        user_text = "Extract all dimensions, features, and metadata from this engineering drawing."

        if dxf_context:
            user_text += f"\n\nAdditional DXF vector data extracted from the file:\n{dxf_context[:4000]}"

        if pdf_text:
            user_text += f"\n\nText extracted from the PDF:\n{pdf_text[:4000]}"

        content.append({"type": "text", "text": user_text})

        # Use cache control for system prompt (prompt caching)
        system_blocks = [
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ]

        # Collect all tool calls via iteration
        dimensions: List[DimensionSpec] = []
        features: List[FeatureSpec] = []
        metadata: Dict[str, Any] = {}

        messages = [{"role": "user", "content": content}]

        # Loop until Claude stops calling tools
        max_iterations = 10
        for iteration in range(max_iterations):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    system=system_blocks,
                    tools=EXTRACTION_TOOLS,
                    messages=messages,
                )
            except Exception as e:
                logger.error(f"Claude API error: {e}")
                break

            # Process tool use blocks
            tool_results = []
            has_tool_use = False

            for block in response.content:
                if block.type == "tool_use":
                    has_tool_use = True
                    tool_name = block.name
                    tool_input = block.input

                    if tool_name == "record_dimension":
                        dim = _tool_input_to_dimension(tool_input)
                        dimensions.append(dim)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": f"Recorded dimension {dim.id}: {dim.name} = {dim.value} {dim.unit}",
                        })

                    elif tool_name == "record_feature":
                        feat = _tool_input_to_feature(tool_input)
                        features.append(feat)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": f"Recorded feature {feat.id}: {feat.type}",
                        })

                    elif tool_name == "record_drawing_metadata":
                        metadata = tool_input
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": "Recorded drawing metadata.",
                        })
                    else:
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": f"Unknown tool: {tool_name}",
                            "is_error": True,
                        })

            if not has_tool_use or response.stop_reason == "end_turn":
                break

            # Continue conversation with tool results
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

        # Build DrawingSpec
        spec = DrawingSpec(
            drawing_number=metadata.get("drawing_number"),
            title=metadata.get("title"),
            revision=metadata.get("revision"),
            unit=metadata.get("unit", "mm"),
            material=metadata.get("material"),
            general_tolerance=metadata.get("general_tolerance", "ISO 2768-m"),
            dimensions=dimensions,
            features=features,
            notes=metadata.get("notes", []),
            ambiguities=metadata.get("ambiguities", []),
        )

        logger.info(
            f"Extraction pass complete: {len(dimensions)} dimensions, "
            f"{len(features)} features, {len(spec.ambiguities)} ambiguities"
        )

        return spec

    def run_dual_extraction(
        self,
        image_bytes: bytes,
        image_media_type: str = "image/png",
        dxf_context: Optional[str] = None,
        pdf_text: Optional[str] = None,
        model_pass_b: Optional[str] = None,
    ) -> Tuple[DrawingSpec, DrawingSpec]:
        """
        Run both Pass A and Pass B independently.
        Optionally uses a different model for Pass B.
        """
        logger.info("Starting dual extraction — Pass A")
        pass_a = self.extract_pass(
            image_bytes=image_bytes,
            image_media_type=image_media_type,
            system_prompt=SYSTEM_PROMPT_PASS_A,
            dxf_context=dxf_context,
            pdf_text=pdf_text,
        )

        # Optionally switch model for Pass B
        original_model = self.model
        if model_pass_b:
            self.model = model_pass_b

        logger.info("Starting dual extraction — Pass B")
        pass_b = self.extract_pass(
            image_bytes=image_bytes,
            image_media_type=image_media_type,
            system_prompt=SYSTEM_PROMPT_PASS_B,
            dxf_context=dxf_context,
            pdf_text=pdf_text,
        )

        self.model = original_model

        return pass_a, pass_b


# ---------------------------------------------------------------------------
# Tool Input → Pydantic Converters
# ---------------------------------------------------------------------------

def _tool_input_to_dimension(data: Dict[str, Any]) -> DimensionSpec:
    """Convert Claude tool call input to DimensionSpec."""
    bbox = None
    if all(k in data for k in ("bbox_x_min", "bbox_y_min", "bbox_x_max", "bbox_y_max")):
        try:
            bbox = BoundingBox(
                x_min=max(0.0, min(1.0, data["bbox_x_min"])),
                y_min=max(0.0, min(1.0, data["bbox_y_min"])),
                x_max=max(0.0, min(1.0, data["bbox_x_max"])),
                y_max=max(0.0, min(1.0, data["bbox_y_max"])),
            )
        except Exception:
            bbox = None

    return DimensionSpec(
        id=data["id"],
        name=data["name"],
        value=data.get("value"),
        unit=data.get("unit", "mm"),
        tol_plus=data.get("tol_plus", 0.0),
        tol_minus=data.get("tol_minus", 0.0),
        type=DimensionType(data.get("type", "linear")),
        source=DimensionSource(data.get("source", "printed")),
        confidence=data.get("confidence", 1.0),
        bbox=bbox,
        view=ViewType(data.get("view", "front")),
        status=DimensionStatus.NEEDS_HUMAN,  # Always starts as needs_human
        evidence=None,  # Filled in during reconciliation
        notes=data.get("notes"),
    )


def _tool_input_to_feature(data: Dict[str, Any]) -> FeatureSpec:
    """Convert Claude tool call input to FeatureSpec."""
    return FeatureSpec(
        id=data["id"],
        type=FeatureType(data["type"]),
        dimension_ids=data.get("dimension_ids", []),
        parameters=data.get("parameters", {}),
        parent_feature_id=data.get("parent_feature_id"),
    )
