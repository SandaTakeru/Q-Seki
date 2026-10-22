"""Core calculation and report generation for KSH survey area tables."""

from .geometry import (
    AreaMode,
    compute_polygon_area,
    normalize_ring,
    polygon_twice_area,
    ring_signed_area,
)
from .report import ParcelReport, PartReport, ReportBundle, VertexRow, build_html_report
from .rounding import round_decimal

__all__ = [
    "AreaMode",
    "compute_polygon_area",
    "normalize_ring",
    "polygon_twice_area",
    "ring_signed_area",
    "ParcelReport",
    "PartReport",
    "ReportBundle",
    "VertexRow",
    "build_html_report",
    "round_decimal",
]
