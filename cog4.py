import cadquery as cq
import numpy as np
from typing import Literal
from pathlib import Path
import pyvista as pv
from helpers import setup_visualization, visualize_step


def create_rack_cutter_sketch(
    m: float,
    alpha: float,
    ha_star: float,
    c_star: float,
    rho_f_star: float,
    z: int,
) -> cq.Sketch:
    """
    Create a rack cutter profile with multiple teeth.

    The rack consists of multiple trapezoid teeth with rounded tips,
    arranged along the X-axis with proper pitch spacing.

    Args:
        m: module (DE: Modul)
        alpha: pressure angle [degree] (DE: Eingriffswinkel [grad])
        ha_star: addendum coefficient (DE: Kopfhöhenfaktor)
        c_star: clearance coefficient (DE: Kopfspielfaktor)
        rho_f_star: fillet radius coefficient (DE: Fussrundungsfaktor).
                    If negative, use tangentArcPoint instead.
        z: number of teeth (DE: Zähnezahl)
    Returns:
        CadQuery Workplane with rack cutter profile
    """

    d: float = m * float(z)  # pitch diameter (DE: Teilkreisdurchmesser)
    ha: float = ha_star * m  # addendum (DE: Zahnkopfhöhe)
    hf: float = (ha_star + c_star) * m  # dedendum (DE: Zahnfusshöhe)
    rho_f: float = abs(rho_f_star) * m  # fillet radius at tip (DE: Fussrundung)
    alpha_r: float = np.radians(alpha)
    p: float = np.pi * m  # pitch (DE: Teilung)

    rack_length: float = (z + 4) * p
    base_height: float = 3 * m

    toothwidth_at_base: float = p / 2 + 2 * hf * np.tan(alpha_r)

    rack_sketch: cq.Sketch = (
        cq.Sketch()
        .push([(0, -base_height / 2 - hf)])
        .rect(rack_length, base_height)
        .push([(0, (ha + hf) / 2 - hf)])
        .rarray(p, 1, z + 4, 1)
        .trapezoid(toothwidth_at_base, ha + hf, 90 - alpha, mode="a")
        .clean()
    )

    rack_sketch = (
        rack_sketch
        .reset()
        .vertices("not (<Y or >Y or <X or >X)")
        .fillet(rho_f)
        .clean()
    )

    return rack_sketch


def simulate_gear_cutting(
    z: int,
    m: float,
    c_star: float,
    alpha: float,
    num_cut_positions: int,
    extrude_depth: float,
    visualize: Literal[None, "show", "step", "img"],
) -> cq.Workplane:
    d: float = m * z
    r: float = d / 2
    p: float = np.pi * m

    d_blank: float = d + 3 * m
    gear_blank: cq.Workplane = (
        cq.Workplane("XY").circle(d_blank / 2).extrude(extrude_depth)
    )

    rack_cutter_sketch: cq.Sketch = create_rack_cutter_sketch(
        m=m,
        alpha=alpha,
        ha_star=1.0,
        c_star=c_star,
        rho_f_star=0.3,
        z=z,
    )
    rack_cutter: cq.Workplane = (
        cq.Workplane("XY").placeSketch(rack_cutter_sketch).extrude(extrude_depth)
    )

    cut_counter: int = 0
    output_dir: Path = Path("output")
    step_dir: Path = output_dir / "step"
    image_dir: Path = output_dir / "img"
    tmp_dir: Path = output_dir / "tmp"

    fixed_camera_position: pv.CameraPosition | None = setup_visualization(
        visualize, step_dir, image_dir, tmp_dir, gear_blank
    )

    result: cq.Workplane = gear_blank
    cut_counter = visualize_step(
        result, None, visualize, cut_counter, step_dir, image_dir, tmp_dir, fixed_camera_position
    )

    for i in range(num_cut_positions):
        t: float = i / (num_cut_positions)
        x_rack: float = p * z * (1 / 2 - t)
        theta: float = x_rack / r

        positioned_rack: cq.Workplane = rack_cutter.translate(
            (-x_rack, -r, 0.0)
        ).rotate((0, 0, 0), (0, 0, 1), np.degrees(theta))

        result = result.cut(positioned_rack)
        cut_counter = visualize_step(
            result, positioned_rack, visualize, cut_counter, step_dir, image_dir, tmp_dir, fixed_camera_position
        )

    return result


