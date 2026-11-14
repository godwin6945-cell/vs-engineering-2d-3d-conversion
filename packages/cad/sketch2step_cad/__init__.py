"""
CadQuery Deterministic Feature Compiler & Geometric Validators.
"""

from .builders.registry import BUILDER_REGISTRY, get_builder
from .compiler import FeatureCompiler, CompilationError
from .validator import GeometryValidator
from .exporter import StepExporter
from .report import InspectionReportCompiler

__version__ = "0.1.0"

__all__ = [
    "BUILDER_REGISTRY",
    "get_builder",
    "FeatureCompiler",
    "CompilationError",
    "GeometryValidator",
    "StepExporter",
    "InspectionReportCompiler",
]
