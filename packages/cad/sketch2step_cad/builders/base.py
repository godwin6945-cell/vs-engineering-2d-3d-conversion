"""
Base classes and validation helpers for CadQuery parametric feature builders.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import cadquery as cq


class FeatureBuilder(ABC):
    """Abstract base class for all deterministic CAD feature builders."""

    @abstractmethod
    def build(self, base: Optional[cq.Workplane] = None, **params: Any) -> cq.Workplane:
        """Construct or modify the CadQuery geometry using verified numeric parameters."""
        pass


def require_positive(name: str, value: float) -> float:
    """Validate that a numeric dimension is strictly positive (> 0)."""
    if value is None or value <= 0:
        raise ValueError(f"Feature parameter '{name}' must be strictly greater than 0, got {value}")
    return float(value)


def require_non_negative(name: str, value: float) -> float:
    """Validate that a numeric parameter is non-negative (>= 0)."""
    if value is None or value < 0:
        raise ValueError(f"Feature parameter '{name}' must be non-negative, got {value}")
    return float(value)
