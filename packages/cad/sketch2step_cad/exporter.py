"""
STEP AP214 and STL export with roundtrip verification.
"""

import os
import tempfile
from typing import Tuple
import cadquery as cq


class StepExporter:
    """Exports CadQuery geometry to STEP AP214 and verifies import roundtrip."""

    @staticmethod
    def export_step(solid: cq.Workplane, file_path: str) -> str:
        """Exports solid model to standardized STEP AP214 format."""
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        # CadQuery default export for .step / .stp uses AP214
        cq.exporters.export(solid, file_path)
        return file_path

    @staticmethod
    def export_stl(solid: cq.Workplane, file_path: str, tolerance: float = 0.01) -> str:
        """Exports tessellated STL format for browser 3D viewers."""
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        cq.exporters.export(solid, file_path, tolerance=tolerance)
        return file_path

    @classmethod
    def verify_step_roundtrip(cls, solid: cq.Workplane) -> Tuple[bool, float]:
        """
        Exports geometry to temporary STEP file and re-imports it.
        Validates that the re-imported solid is valid and preserves volume.
        Returns: (passed: bool, volume_deviation_percent: float)
        """
        orig_volume = solid.val().Volume()
        if orig_volume <= 0:
            return False, 100.0

        with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            cls.export_step(solid, tmp_path)
            # Re-import solid
            reimported = cq.importers.importStep(tmp_path)
            re_volume = reimported.val().Volume()
            re_valid = reimported.val().isValid()

            vol_diff = abs(re_volume - orig_volume)
            deviation_pct = (vol_diff / orig_volume) * 100.0

            # Roundtrip passes if solid is valid and volume deviation < 0.05%
            passed = re_valid and (deviation_pct < 0.05)
            return passed, round(deviation_pct, 4)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
