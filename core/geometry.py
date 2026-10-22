from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import List, Literal, Sequence, Tuple

from .rounding import area_round, decimalize

AreaMode = Literal["floor", "half_up", "none"]


@dataclass(frozen=True)
class Vertex:
    x: Decimal
    y: Decimal


def _as_xy(point: Tuple[Decimal, Decimal] | Vertex) -> Tuple[Decimal, Decimal]:
    """座標入力を (x, y) のタプルへ正規化する。"""
    if isinstance(point, Vertex):
        return (point.x, point.y)
    if len(point) != 2:
        raise ValueError(f"Point must have 2 coordinates, got {point!r}")
    return (decimalize(point[0]), decimalize(point[1]))


def _shoelace_sum(vertices: Sequence[Tuple[Decimal, Decimal] | Vertex]) -> Decimal:
    """符号付きの面積計算を行い、反時計回り判定に用いる。"""
    if len(vertices) < 3:
        return Decimal("0")
    total = Decimal("0")
    for index, current in enumerate(vertices):
        prev = vertices[(index - 1) % len(vertices)]
        current_xy = _as_xy(current)
        prev_xy = _as_xy(prev)
        x1, y1 = current_xy
        x0, y0 = prev_xy
        total += x0 * y1 - x1 * y0
    return total


def ring_signed_area(vertices: Sequence[Tuple[Decimal, Decimal] | Vertex]) -> Decimal:
    """外積による符号付き面積を返す。反時計回りは正。"""
    return _shoelace_sum(vertices)


def normalize_ring(vertices: Sequence[Tuple[Decimal, Decimal] | Vertex], start: str = "north") -> List[Tuple[Decimal, Decimal]]:
    """頂点順を反時計回りかつ起点方式に合わせて正規化する。"""
    if len(vertices) < 3:
        raise ValueError("A polygon ring must have at least 3 vertices.")
    points = [_as_xy(p) for p in vertices]

    if start == "north":
        index = max(range(len(points)), key=lambda i: (points[i][1], points[i][0]))
    elif start == "first":
        index = 0
    else:
        raise ValueError(f"Unsupported start option: {start!r}")

    rotated = points[index:] + points[:index]
    signed = ring_signed_area(rotated)
    if signed < 0:
        rotated = list(reversed(rotated))
    elif signed == 0:
        raise ValueError("Degenerate polygon detected")
    return rotated


def polygon_twice_area(vertices: Sequence[Tuple[Decimal, Decimal] | Vertex]) -> Decimal:
    """任意投影座標系で使用できる 2 倍面積を返す。"""
    points = [_as_xy(p) for p in vertices]
    if len(points) < 3:
        return Decimal("0")

    total = Decimal("0")
    for index, current in enumerate(points):
        prev = points[(index - 1) % len(points)]
        next_point = points[(index + 1) % len(points)]
        # QGIS の座標は (Y, X) = (東, 北) であり、求積表の式は Yn × (Xn+1 - Xn-1)
        delta_x = next_point[1] - prev[1]
        total += current[0] * delta_x
    return abs(total)


def compute_polygon_area(vertices: Sequence[Tuple[Decimal, Decimal] | Vertex], area_digits: int = 2, area_mode: AreaMode = "floor") -> Decimal:
    """面積を計算し、端数処理を適用して返す。"""
    area = polygon_twice_area(vertices) / Decimal("2")
    return area_round(area, digits=area_digits, mode=area_mode)


def polygon_area(vertices: Sequence[Tuple[Decimal, Decimal] | Vertex], area_digits: int = 2, area_mode: AreaMode = "floor") -> Decimal:
    """後方互換のエイリアス。"""
    return compute_polygon_area(vertices, area_digits=area_digits, area_mode=area_mode)


def normalized_vertices_for_area(vertices: Sequence[Tuple[Decimal, Decimal] | Vertex], start: str = "north") -> List[Tuple[Decimal, Decimal]]:
    """面積計算用に正規化した頂点列を返す。"""
    return normalize_ring(vertices, start=start)
