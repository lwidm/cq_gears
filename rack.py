import cadquery as cq
import numpy as np
from typing import Literal

from .core import GearData


def _create_single_rack_cutter(
    m: float,
    z: int,
    b: float,
    alpha_t: float,
    alpha_t_r: float,
    beta_r: float,
    ha: float,
    hf: float,
    rho_f: float,
    p: float,
) -> cq.Workplane:

    base_height: float = 3 * m
    rack_length: float

    rack_length: float = (z + 4) * p

    n_rack_teeth: int = int(rack_length / p)

    toothwidth_at_base: float = p / 2 + 2 * hf * np.tan(alpha_t_r)

    rack_sketch: cq.Sketch = (
        cq.Sketch()
        .push([(0, -base_height / 2 - hf)])
        .rect(rack_length, base_height)
        .push([(0, (ha + hf) / 2 - hf)])
        .rarray(p, 1, n_rack_teeth, 1)
        .trapezoid(toothwidth_at_base, ha + hf, 90 - alpha_t, mode="a")
        .clean()
    )
    rack_sketch = (
        rack_sketch.reset().vertices("not (<Y or >Y or <X or >X)").fillet(rho_f).clean()
    )

    rack: cq.Workplane = cq.Workplane("XY").placeSketch(rack_sketch)
    start_x: float = -b / 2 * np.tan(beta_r) if beta_r != 0 else 0.0
    start_y: float = -b / 2
    end_x: float = -start_x
    end_y: float = -start_y
    sweep_path: cq.Workplane = (
        cq.Workplane("XZ").moveTo(start_x, start_y).lineTo(end_x, end_y)
    )
    rack = rack.sweep(sweep_path)

    return rack


def _create_rack_cutter_for_group(
    gear_data_list: list[GearData],
    group: set[int],
) -> cq.Workplane:
    gear_data_in_group: list[GearData] = [gear_data_list[i] for i in group]

    first: GearData = gear_data_in_group[0]
    z_max: int = max(gd.z for gd in gear_data_in_group)
    b_max: float = max(gd.b for gd in gear_data_in_group)

    return _create_single_rack_cutter(
        first.m,
        z_max,
        b_max,
        first.alpha_t,
        first.alpha_t_r,
        first.beta_r,
        first.ha,
        first.hf,
        first.rho_f,
        first.p,
    )
