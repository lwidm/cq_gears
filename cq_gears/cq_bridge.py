import numpy as np
from typing import NamedTuple
import cadquery as cq

from . import geometry


class CqArcTuple(NamedTuple):
    center: tuple[float, float]
    radius: float
    start_angle_deg: float
    sweep_angle_deg: float


def cq_arc_center_start_end(
    arc_center: np.ndarray,
    arc_start: np.ndarray,
    arc_end: np.ndarray,
    counter_clock_wise: bool,
) -> CqArcTuple:
    center, radius, start_angle, sweep = geometry.arc_from_endpoints(
        arc_center, arc_start, arc_end, counter_clock_wise
    )
    return CqArcTuple(
        center=center,
        radius=radius,
        start_angle_deg=start_angle,
        sweep_angle_deg=sweep,
    )


class CqSplineTuple(NamedTuple):
    points: list[tuple[float, float]]
    tangents: list[tuple[float, float]] | None = None
    periodic: bool = False
    tag: str | None = None


def cq_spline_from_array(
    points: np.ndarray, skip_first: bool, tangents: np.ndarray | None, periodic: bool
) -> CqSplineTuple:
    if points.ndim != 2 or points.shape[0] != 2:
        raise ValueError(f"points: expect shape (2, N), got {points.shape}")
    if points.shape[1] < 2:
        raise ValueError(f"points: needs at least 2 columns, got {points.shape[1]}")

    start_col: int = 1 if skip_first else 0
    pts_list: list[tuple[float, float]] = [
        (float(points[0, c]), float(points[1, c]))
        for c in range(start_col, points.shape[1])
    ]

    tan_list: list[tuple[float, float]] | None = None
    if tangents is not None:
        if tangents.shape != (2, 2):
            raise ValueError(f"tangents: expected shape (2,2), got {tangents.shape}")
        tan_list = [
            (float(tangents[0, 0]), float(tangents[1, 0])),
            (float(tangents[0, 1]), float(tangents[1, 1])),
        ]

    return CqSplineTuple(
        points=pts_list, tangents=tan_list, periodic=periodic, tag=None
    )
