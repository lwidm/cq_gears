import numpy as np
import cadquery as cq
from . import geometry
from . import cq_bridge

from .core import GearData


def _compute_tooth_points(
    geardata: GearData, n_points: int
) -> dict[str, bool | np.ndarray]:
    if n_points < 3:
        raise ValueError(f"n_points must be greater than 3. Instead got {n_points}")

    phi_r_addendum: float = geometry.involute_phi_d(geardata.da, geardata.db, "right")
    phi_r_addendum_intersection: float = geometry.involute_self_intersection(
        phi_r_addendum,
        geardata.m,
        geardata.x,
        geardata.d,
        geardata.db,
        geardata.alpha_n_r,
    )
    phi_inv_start: float = geometry.involute_phi_d(geardata.d, geardata.db, "right")
    phi_undercut_end: float = geometry.undercut_phi_d(
        geardata.d, geardata.d, geardata.df, geardata.alpha_t_r, "right"
    )
    phi_inv_start, phi_undercut_end = geometry.undercut_involute_intersection(
        phi_inv_start,
        phi_undercut_end,
        geardata.df,
        geardata.d,
        geardata.db,
        geardata.alpha_t_r,
        "right",
        200,
    )

    phi_r_end: float
    involutes_instersect: bool
    if phi_r_addendum > phi_r_addendum_intersection:
        phi_r_end = phi_r_addendum_intersection
        involutes_instersect = True
    else:
        phi_r_end = phi_r_addendum
        involutes_instersect = False

    points_inv_right: np.ndarray = geometry.involute_tooth(
        geardata.m,
        geardata.x,
        geardata.d,
        geardata.db,
        geardata.alpha_n_r,
        phi_inv_start,
        phi_r_end,
        n_points,
        "right",
    )
    points_inv_left: np.ndarray = geometry.involute_tooth(
        geardata.m,
        geardata.x,
        geardata.d,
        geardata.db,
        geardata.alpha_n_r,
        -phi_inv_start,
        -phi_r_end,
        n_points,
        "left",
    )
    points_undercut_right: np.ndarray = geometry.undercut_tooth(
        geardata.m,
        geardata.x,
        geardata.d,
        geardata.db,
        geardata.df,
        geardata.alpha_n_r,
        geardata.alpha_t_r,
        phi_undercut_end,
        n_points,
        "right",
    )
    points_undercut_left: np.ndarray = geometry.undercut_tooth(
        geardata.m,
        geardata.x,
        geardata.d,
        geardata.db,
        geardata.df,
        geardata.alpha_n_r,
        geardata.alpha_t_r,
        -phi_undercut_end,
        n_points,
        "left",
    )

    result: dict[str, bool | np.ndarray] = {
        "points_inv_right": points_inv_right,
        "points_inv_left": points_inv_left,
        "points_undercut_right": points_undercut_right,
        "points_undercut_left": points_undercut_left,
        "involutes_intersect": involutes_instersect,
    }

    return result


def _tooth_sketch(geardata: GearData, n_points: int) -> cq.Sketch:
    tooth_compute_dict: dict[str, bool | np.ndarray] = _compute_tooth_points(
        geardata, n_points
    )
    points_inv_right: np.ndarray = tooth_compute_dict["points_inv_right"]  # type: ignore
    points_inv_left: np.ndarray = tooth_compute_dict["points_inv_left"]  # type: ignore
    points_undercut_right: np.ndarray = tooth_compute_dict["points_undercut_right"]  # type: ignore
    points_undercut_left: np.ndarray = tooth_compute_dict["points_undercut_left"]  # type: ignore
    involutes_instersect: bool = tooth_compute_dict["involutes_intersect"]  # type: ignore

    arc_base: cq_bridge.CqArcTuple = cq_bridge.cq_arc_center_start_end(
        arc_center=np.array([0.0, 0.0]),
        arc_start=points_inv_left[:, 0],
        arc_end=points_inv_right[:, 0],
        counter_clock_wise=False,
    )

    cq_inv_right: cq_bridge.CqSplineTuple = cq_bridge.cq_spline_from_array(
        points_inv_right, skip_first=False, tangents=None, periodic=False
    )
    cq_inv_left: cq_bridge.CqSplineTuple = cq_bridge.cq_spline_from_array(
        points_inv_left[:, ::-1], skip_first=False, tangents=None, periodic=False
    )

    result: cq.Sketch
    if involutes_instersect:
        result = (
            cq.Sketch()
            .arc(*arc_base)
            .spline(*cq_inv_right)
            .spline(*cq_inv_left)
            .close()
        )
    else:
        arc_tip: cq_bridge.CqArcTuple = cq_bridge.cq_arc_center_start_end(
            arc_center=np.array([0.0, 0.0]),
            arc_start=points_inv_right[:, -1],
            arc_end=points_inv_left[:, -1],
            counter_clock_wise=True,
        )
        result = (
            cq.Sketch()
            .arc(*arc_base)
            .spline(*cq_inv_right)
            .arc(*arc_tip)
            .spline(*cq_inv_left)
            .close()
        )

    return result


def _circles(geardata: GearData) -> cq.Sketch:
    result: cq.Sketch = (
        cq.Sketch()
        .circle(geardata.d / 2.0)
        .circle(geardata.db / 2.0)
        .circle(geardata.da / 2.0)
        .circle(geardata.df / 2.0)
    )
    return result
