import numpy as np
import cadquery as cq
from . import geometry
from . import cq_bridge

from .core import (
    GearData,
    SpurGearData,
    HelicalGearData,
    RackGearData,
    HelicalRackGearData,
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


def _involute_tooth_sketch(geardata: GearData, n_points: int) -> cq.Sketch:
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


def _rack_tooth_sketch(geardata: GearData) -> cq.Sketch:
    ha: float = geardata.ha
    hf: float = geardata.hf
    tip_w: float = geardata.p / 2 - 2 * np.tan(geardata.alpha_t_r) * ha
    base_w: float = geardata.p / 2 + 2 * np.tan(geardata.alpha_t_r) * hf

    return cq.Sketch().polygon(
        [
            (-ha, tip_w / 2),
            (-ha, -tip_w / 2),
            (hf, -base_w / 2),
            (hf, base_w / 2),
        ]
    )


def _full_rack_section_sketch(
    geardata: RackGearData | HelicalRackGearData,
    *,
    extra_teeth_per_side: int = 0,
) -> cq.Sketch:
    """
    Full 2D cross-section of a parametric rack.

    Origin convention: (0, 0) is the center of the first tooth, on the
    pitch line (x = 0). Teeth tips at x = -ha; rail back at
    x = +(hf + rail_width). Tooth array along +Y at pitch p, first
    tooth at y = 0.

    With extra_teeth_per_side > 0, extra teeth are added in BOTH +-Y
    directions and the rail is extended to match. This is used when the
    sketch will be swept along a tilted path and cropped afterward.
    """
    p: float = geardata.p
    ha: float = geardata.ha
    hf: float = geardata.hf
    alpha_t: float = geardata.alpha_t
    alpha_t_r: float = geardata.alpha_t_r
    rho_f: float = geardata.rho_f
    rail_width: float = geardata.rail_width

    base_w: float = p / 2 + 2 * np.tan(alpha_t_r) * hf
    n_teeth: int = geardata.z + 2 * extra_teeth_per_side

    array_center_y: float = (geardata.z - 1) * p / 2
    rail_y_length: float = (n_teeth - 1) * p + base_w

    rail_x_center: float = hf + rail_width / 2
    tooth_x_center: float = (hf - ha) / 2

    sketch: cq.Sketch = (
        cq.Sketch()
        # Rail — centered on the tooth-array midpoint
        .push([(rail_x_center, array_center_y)])
        .rect(rail_width, rail_y_length)
        # Teeth — rarray centers on the push point, so push to
        # array_center_y rather than the first tooth's y
        .push([(tooth_x_center, array_center_y)])
        .rarray(1, p, 1, n_teeth)
        .trapezoid(base_w, ha + hf, 90 - alpha_t, angle=90, mode="a")
        .clean()
        .reset()
        # Round the interior corners (tooth-rail seam)
        .vertices("not (<X or >X or <Y or >Y)")
        .fillet(rho_f)
        .clean()
    )
    return sketch


def parametric_gear_workplane(
    geardata: GearData, n_points: int | None = None
) -> cq.Workplane:

    origin: cq.Workplane = cq.Workplane("XY")

    cylinder: cq.Workplane
    tooth_sketch: cq.Sketch
    teeth: cq.Workplane
    result: cq.Workplane
    match geardata:
        case SpurGearData():
            if n_points is None:
                raise ValueError(
                    'SpurGearData needs a non None value for "n_points" since it constructs splines using parametric equations'
                )
            cylinder = origin.cylinder(geardata.b, geardata.df / 2.0, (0, 0, 1))
            tooth_sketch = _involute_tooth_sketch(geardata, n_points)
            teeth = (
                origin.polarArray(radius=0, startAngle=0, angle=360, count=geardata.z)
                .placeSketch(tooth_sketch)
                .extrude(geardata.b / 2, both=True)
            )
            result = cylinder.union(teeth).clean()
        case HelicalGearData():
            if n_points is None:
                raise ValueError(
                    'SpurGearData needs a non None value for "n_points" since it constructs splines using parametric equations'
                )
            twist_deg = np.degrees(
                2 * geardata.b * np.tan(geardata.beta_r) / geardata.dp
            )
            cylinder = origin.cylinder(geardata.b, geardata.df / 2.0, (0, 0, 1))
            tooth_sketch = _involute_tooth_sketch(geardata, n_points)
            teeth = (
                origin.workplane(offset=-geardata.b / 2)
                .polarArray(
                    radius=0, startAngle=-twist_deg / 2, angle=360, count=geardata.z
                )
                .placeSketch(tooth_sketch)
                .twistExtrude(geardata.b, twist_deg)
            )
            result = cylinder.union(teeth).clean()
        case RackGearData():
            base_w: float = (
                geardata.p / 2 + 2 * np.tan(geardata.alpha_t_r) * geardata.hf
            )
            rail: cq.Workplane = origin.workplane(
                origin=(geardata.hf, -base_w / 2), offset=-geardata.b / 2
            ).box(
                geardata.rail_width,
                geardata.p * float(geardata.z - 1) + base_w,
                geardata.b,
                centered=False,
            )
            tooth_sketch = _rack_tooth_sketch(geardata)
            teeth = (
                origin.rarray(0, geardata.p, 1, geardata.z, center=False)
                .placeSketch(tooth_sketch)
                .extrude(geardata.b / 2, both=True)
            )
            result = (
                rail.union(teeth)
                .clean()
                .edges("not (<Y or >Y or <X or >X or #Z)")
                .fillet(geardata.rho_f)
            )
        case HelicalRackGearData():
            half_b: float = geardata.b / 2
            extra: int = max(
                1, int(np.ceil(half_b * np.tan(geardata.beta_r) / geardata.p))
            )
            section: cq.Sketch = _full_rack_section_sketch(
                geardata, extra_teeth_per_side=extra
            )

            y_offset: float = half_b * np.tan(geardata.beta_r)
            sweep_path: cq.Workplane = (
                cq.Workplane("YZ").moveTo(-y_offset, -half_b).lineTo(+y_offset, +half_b)
            )

            overshooting: cq.Workplane = origin.placeSketch(section).sweep(sweep_path)

            base_w: float = (
                geardata.p / 2 + 2 * np.tan(geardata.alpha_t_r) * geardata.hf
            )
            y_min: float = -base_w / 2
            y_max: float = geardata.p * float(geardata.z - 1) + base_w / 2

            crop_box: cq.Workplane = (
                cq.Workplane("XY")
                .center(0, (y_min + y_max) / 2)
                .box(
                    10 * (geardata.rail_width + geardata.ha),  # X — generous
                    y_max - y_min,  # Y — exact desired length
                    10 * geardata.b,  # Z — generous
                )
            )

            result = overshooting.intersect(crop_box).clean()
        case _:
            raise NotImplementedError(
                f'Currently only the following gear types are implemented: ["HelicalGear", "SpurGear", "RackGearData"]. Got geardata of type: {type(geardata)}'
            )
    return result
