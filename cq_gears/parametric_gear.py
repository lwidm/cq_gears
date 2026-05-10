import numpy as np
import cadquery as cq
from . import geometry
from . import cq_bridge

from .core import (
    GearData,
    HelicalGearData,
    InternalHelicalGearData,
    InternalSpurGearData,
    SpurGearData,
)


def compute_tooth_points(
    geardata: GearData, n_points: int
) -> dict[str, bool | np.ndarray]:
    if n_points < 3:
        raise ValueError(f"n_points must be greater than 3. Instead got {n_points}")

    has_undercut: bool = geardata.df < geardata.dp

    phi_r_addendum: float = geometry.involute_phi_d(geardata.da, geardata.db, "right")
    phi_r_addendum_intersection: float = geometry.involute_self_intersection(
        phi_r_addendum,
        geardata.m_t,
        geardata.x,
        geardata.dp,
        geardata.db,
        geardata.alpha_n_r,
    )

    phi_inv_start: float
    phi_undercut_end: float = 0.0
    if has_undercut:
        phi_inv_start = geometry.involute_phi_d(geardata.dp, geardata.db, "right")
        phi_undercut_end = geometry.undercut_phi_d(
            geardata.dp, geardata.dp, geardata.df, geardata.alpha_t_r, "right"
        )
        phi_inv_start, phi_undercut_end = geometry.undercut_involute_intersection(
            phi_inv_start,
            phi_undercut_end,
            geardata.df,
            geardata.dp,
            geardata.db,
            geardata.alpha_t_r,
            "right",
            200,
        )
    else:
        phi_inv_start = geometry.involute_phi_d(geardata.df, geardata.db, "right")

    phi_r_end: float
    involutes_intersect: bool
    if phi_r_addendum > phi_r_addendum_intersection:
        phi_r_end = phi_r_addendum_intersection
        involutes_intersect = True
    else:
        phi_r_end = phi_r_addendum
        involutes_intersect = False

    points_inv_right: np.ndarray = geometry.involute_tooth(
        geardata.m_t,
        geardata.x,
        geardata.dp,
        geardata.db,
        geardata.alpha_n_r,
        phi_inv_start,
        phi_r_end,
        n_points,
        "right",
    )
    points_inv_left: np.ndarray = geometry.involute_tooth(
        geardata.m_t,
        geardata.x,
        geardata.dp,
        geardata.db,
        geardata.alpha_n_r,
        -phi_inv_start,
        -phi_r_end,
        n_points,
        "left",
    )

    result: dict[str, bool | np.ndarray] = {
        "points_inv_right": points_inv_right,
        "points_inv_left": points_inv_left,
        "involutes_intersect": involutes_intersect,
        "has_undercut": has_undercut,
    }

    if has_undercut:
        result["points_undercut_right"] = geometry.undercut_tooth(
            geardata.m_t,
            geardata.x,
            geardata.dp,
            geardata.db,
            geardata.df,
            geardata.alpha_n_r,
            geardata.alpha_t_r,
            phi_undercut_end,
            n_points,
            "right",
        )
        result["points_undercut_left"] = geometry.undercut_tooth(
            geardata.m_t,
            geardata.x,
            geardata.dp,
            geardata.db,
            geardata.df,
            geardata.alpha_n_r,
            geardata.alpha_t_r,
            -phi_undercut_end,
            n_points,
            "left",
        )

    return result


def _tooth_sketch(geardata: GearData, n_points: int) -> cq.Sketch:
    tooth_compute_dict: dict[str, bool | np.ndarray] = compute_tooth_points(
        geardata, n_points
    )
    points_inv_right: np.ndarray = tooth_compute_dict["points_inv_right"]  # type: ignore
    points_inv_left: np.ndarray = tooth_compute_dict["points_inv_left"]  # type: ignore
    involutes_intersect: bool = tooth_compute_dict["involutes_intersect"]  # type: ignore
    has_undercut: bool = tooth_compute_dict["has_undercut"]  # type: ignore

    if involutes_intersect:
        points_inv_left[:, -1] = points_inv_right[:, -1]

    points_undercut_right: np.ndarray | None = None
    points_undercut_left: np.ndarray | None = None
    if has_undercut:
        points_undercut_right = tooth_compute_dict["points_undercut_right"]  # type: ignore
        points_undercut_left = tooth_compute_dict["points_undercut_left"]  # type: ignore
        assert points_undercut_right is not None
        assert points_undercut_left is not None
        arc_base_start: np.ndarray = points_undercut_left[:, 0]
        arc_base_end: np.ndarray = points_undercut_right[:, 0]
    else:
        arc_base_start = points_inv_left[:, 0]
        arc_base_end = points_inv_right[:, 0]

    arc_base: cq_bridge.CqArcTuple = cq_bridge.cq_arc_center_start_end(
        arc_center=np.array([0.0, 0.0]),
        arc_start=arc_base_start,
        arc_end=arc_base_end,
        counter_clock_wise=False,
    )

    cq_inv_right: cq_bridge.CqSplineTuple = cq_bridge.cq_spline_from_array(
        points_inv_right, skip_first=False, tangents=None, periodic=False
    )
    cq_inv_left: cq_bridge.CqSplineTuple = cq_bridge.cq_spline_from_array(
        points_inv_left[:, ::-1], skip_first=False, tangents=None, periodic=False
    )

    sketch: cq.Sketch = cq.Sketch().arc(*arc_base)

    cq_undercut_right: cq_bridge.CqSplineTuple | None = None
    cq_undercut_left: cq_bridge.CqSplineTuple | None = None
    if points_undercut_right is not None and points_undercut_left is not None:
        cq_undercut_right = cq_bridge.cq_spline_from_array(
            points_undercut_right, skip_first=False, tangents=None, periodic=False
        )
        cq_undercut_left = cq_bridge.cq_spline_from_array(
            points_undercut_left[:, ::-1],
            skip_first=False,
            tangents=None,
            periodic=False,
        )
        assert cq_undercut_right is not None
        sketch = sketch.spline(*cq_undercut_right)  # type: ignore

    sketch = sketch.spline(*cq_inv_right)  # type: ignore

    if not involutes_intersect:
        arc_tip: cq_bridge.CqArcTuple = cq_bridge.cq_arc_center_start_end(
            arc_center=np.array([0.0, 0.0]),
            arc_start=points_inv_right[:, -1],
            arc_end=points_inv_left[:, -1],
            counter_clock_wise=True,
        )
        sketch = sketch.arc(*arc_tip)

    sketch = sketch.spline(*cq_inv_left)  # type: ignore

    if cq_undercut_left is not None:
        sketch = sketch.spline(*cq_undercut_left)  # type: ignore

    return sketch.assemble()


def parametric_gear_workplane(geardata: GearData, n_points: int) -> cq.Workplane:

    tooth_sketch: cq.Sketch = _tooth_sketch(geardata, n_points)

    origin: cq.Workplane = cq.Workplane()
    cylinder: cq.Workplane = origin.cylinder(geardata.b, geardata.df / 2.0, (0, 0, 1))
    teeth: cq.Workplane
    match geardata:
        case SpurGearData():
            teeth = (
                origin.polarArray(radius=0, startAngle=0, angle=360, count=geardata.z)
                .placeSketch(tooth_sketch)
                .extrude(geardata.b / 2, both=True)
            )
        case HelicalGearData():
            twist_deg = np.degrees(
                2 * geardata.b * np.tan(geardata.beta_r) / geardata.dp
            )
            teeth = (
                origin.workplane(offset=-geardata.b / 2)
                .polarArray(
                    radius=0, startAngle=-twist_deg / 2, angle=360, count=geardata.z
                )
                .placeSketch(tooth_sketch)
                .twistExtrude(geardata.b, twist_deg)
            )
        case _:
            raise NotImplementedError(
                f'Currently only the following gear types are implemented: ["HelicalGear", "SpurGear"]. Got geardata of type: {type(geardata)}'
            )
    result: cq.Workplane = cylinder.union(teeth).clean()
    return result
