"""
CadQuery Deterministic Feature Compiler & Geometric Validators.
"""

from .builders.registry import BUILDER_REGISTRY, get_builder
from .compiler import FeatureCompiler, CompilationError
from .validator import GeometryValidator
from .exporter import StepExporter
from .report import InspectionReportCompiler
from .sandbox import validate_cad_ast, execute_sandboxed_cad_script, SecurityViolation
from .visual_diff import render_orthographic_views, compare_orthographic_to_drawing

__version__ = "0.1.0"

__all__ = [
    "BUILDER_REGISTRY",
    "get_builder",
    "FeatureCompiler",
    "CompilationError",
    "GeometryValidator",
    "StepExporter",
    "InspectionReportCompiler",
    "validate_cad_ast",
    "execute_sandboxed_cad_script",
    "SecurityViolation",
    "render_orthographic_views",
    "compare_orthographic_to_drawing",
]
