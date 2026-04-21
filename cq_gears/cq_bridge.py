import numpy as np
from typing import NamedTuple


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
    if arc_center.shape != (2,):
        raise ValueError(
            f"arc_center not a point! Expected point shape (2,), got {arc_center.shape}"
        )
    if arc_start.shape != (2,):
        raise ValueError(
            f"arc_start not a point! Expected point shape (2,), got {arc_start.shape}"
        )
    if arc_end.shape != (2,):
        raise ValueError(
            f"arc_end not a point! Expected point shape (2,), got {arc_end.shape}"
        )

    cx: float = arc_center[0]
    cy: float = arc_center[1]
    r: float = np.sqrt((arc_start[0] - cx) ** 2 + (arc_start[1] - cy) ** 2)
    a0: float = np.degrees(np.arctan2(arc_start[1] - cy, arc_start[0] - cx))
    a1: float = np.degrees(np.arctan2(arc_end[1] - cy, arc_end[0] - cx))
    da: float = (a1 - a0) % 360 if counter_clock_wise else -((a0 - a1) % 360)
    return CqArcTuple(center=(cx, cy), radius=r, start_angle_deg=a0, sweep_angle_deg=da)


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
