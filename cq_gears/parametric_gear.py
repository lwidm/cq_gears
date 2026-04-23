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

    if involutes_instersect:
        points_inv_left[:, -1] = points_inv_right[:, -1]

    arc_base: cq_bridge.CqArcTuple = cq_bridge.cq_arc_center_start_end(
        arc_center=np.array([0.0, 0.0]),
        arc_start=points_undercut_left[:, 0],
        arc_end=points_undercut_right[:, 0],
        counter_clock_wise=False,
    )

    cq_inv_right: cq_bridge.CqSplineTuple = cq_bridge.cq_spline_from_array(
        points_inv_right, skip_first=False, tangents=None, periodic=False
    )
    cq_inv_left: cq_bridge.CqSplineTuple = cq_bridge.cq_spline_from_array(
        points_inv_left[:, ::-1], skip_first=False, tangents=None, periodic=False
    )
    cq_undercut_right: cq_bridge.CqSplineTuple = cq_bridge.cq_spline_from_array(
        points_undercut_right, skip_first=False, tangents=None, periodic=False
    )
    cq_undercut_left: cq_bridge.CqSplineTuple = cq_bridge.cq_spline_from_array(
        points_undercut_left[:, ::-1], skip_first=False, tangents=None, periodic=False
    )

    result: cq.Sketch
    if involutes_instersect:
        result = (
            cq.Sketch()
            .arc(*arc_base)
            .spline(*cq_undercut_right)
            .spline(*cq_inv_right)
            .spline(*cq_inv_left)
            .spline(*cq_undercut_left)
            .assemble()
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
            .spline(*cq_undercut_right)
            .spline(*cq_inv_right)
            .arc(*arc_tip)
            .spline(*cq_inv_left)
            .spline(*cq_undercut_left)
            .assemble()
        )

    return result


def parametric_gear_workplane(geardata: GearData, n_points: int) -> cq.Workplane:
    if not np.isclose(geardata.delta_r, np.pi / 2):
        raise NotImplementedError("No bevel gear implemented in parametric_gear_workplane")

    tooth_sketch: cq.Sketch = _tooth_sketch(geardata, n_points)

    origin: cq.Workplane = cq.Workplane()
    cylinder: cq.Workplane = origin.cylinder(geardata.b, geardata.df / 2.0, (0, 0, 1))
    teeth: cq.Workplane
    if np.isclose(geardata.beta_r, 0.0):
        teeth = (
            origin.polarArray(radius=0, startAngle=0, angle=360, count=geardata.z)
            .placeSketch(tooth_sketch)
            .extrude(geardata.b / 2, both=True)
        )
    else:
        twist_deg = np.degrees(2 * geardata.b * np.tan(geardata.beta_r) / geardata.d)
        teeth = (
            origin.workplane(offset=-geardata.b / 2)
            .polarArray(
                radius=0, startAngle=-twist_deg / 2, angle=360, count=geardata.z
            )
            .placeSketch(tooth_sketch)
            .twistExtrude(geardata.b, twist_deg)
        )
    result: cq.Workplane = cylinder.union(teeth).clean()
    return result
