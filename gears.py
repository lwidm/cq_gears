import cadquery as cq
import numpy as np
from typing import Literal
from pathlib import Path
import pyvista as pv
from dataclasses import dataclass

from helpers import setup_visualization, visualize_step


@dataclass
class GearData:
    m: float  # module (DE: Modul)
    z: int  # number of teeth (DE: Zähnezahl)
    alpha: float  # pressure angle [degrees] (DE: Eingriffswinkel [grad])
    alpha_r: float  # pressure angle [radian] (DE: Eingriffswinkel [radian])
    beta: float  # helix angle at pitch circle [degrees] (DE: Schrägungswinkel am Teilkreis [raidan])
    beta_r: float  # helix angle at pitch circle [radian] (DE: Schrägungswinkel am Teilkreis [radian])
    beta_b: float  # helix angle at base circle [degrees] (DE: Schrägungswinkel am Grundkreis [degrees])
    beta_b_r: float  # helix angle at base circle [radian] (DE: Schrägungswinkel am Grundkreis [radian])
    ha_star: float  # addendum coefficient (DE: Kopfhöhenfaktor)
    c_star: float  # clearance coefficient (DE: Kopfspielfaktor)
    rho_f_star: float  # fillet radius coefficent (DE: Fussrundingsfaktor)
    d: float  # pitch diameter (DE: Teilkreisdurchmesser)
    db: float  # base diameter (DE: Grundkreisdurchmesser)
    df: float  # TODO diameter (DE: Kopfkreisdurchmesser)
    p: float  # pitch (DE: Teilung)


@dataclass
class Gear:
    data: GearData
    rack: cq.Workplane
    gear: cq.Workplane


def compute_gear_data(
    m: float,
    z: float,
    alpha: float,
    beta: float,
    ha_star: float,
    c_star: float,
    rho_f_star: float,
) -> GearData:
    alpha_r: float = np.radians(alpha)
    beta_r: float = np.radians(beta)

    d: float = m * float(z)
    p: float = np.pi * m

    db: float = d * np.cos(alpha_r)

    # Helix angle at base circle
    # For spur gears (beta=0), beta_b=0
    # For helical gears: tan(beta_b) = tan(beta) * cos(alpha)
    beta_b_r: float = np.arctan(np.tan(beta_r) * np.cos(alpha_r))
    beta_b: float = np.degrees(beta_b_r)

    hf: float = (ha_star + c_star) * m  # dedendum height
    df: float = d - 2 * hf

    return GearData(
        m=m,
        z=int(z),
        alpha=alpha,
        alpha_r=alpha_r,
        beta=beta,
        beta_r=beta_r,
        beta_b=beta_b,
        beta_b_r=beta_b_r,
        ha_star=ha_star,
        c_star=c_star,
        rho_f_star=rho_f_star,
        d=d,
        db=db,
        df=df,
        p=p,
    )


def create_rack_cutter_sketch(
    m: float,
    alpha: float,
    ha_star: float,
    c_star: float,
    rho_f_star: float,
    z: int,
) -> cq.Sketch:
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
        rack_sketch.reset().vertices("not (<Y or >Y or <X or >X)").fillet(rho_f).clean()
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
        result,
        None,
        visualize,
        cut_counter,
        step_dir,
        image_dir,
        tmp_dir,
        fixed_camera_position,
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
            result,
            positioned_rack,
            visualize,
            cut_counter,
            step_dir,
            image_dir,
            tmp_dir,
            fixed_camera_position,
        )

    return result
