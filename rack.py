import cadquery as cq
import numpy as np

from core import GearData


def _create_single_rack_cutter(
    m: float,
    z: int,
    b: float,
    alpha: float,
    alpha_r: float,
    ha: float,
    hf: float,
    rho_f: float,
    p: float,
) -> cq.Workplane:

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
    rack: cq.Workplane = (
        cq.Workplane("XY").placeSketch(rack_sketch).extrude(b, both=True)
    )

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
        first.alpha,
        first.alpha_r,
        first.ha,
        first.hf,
        first.rho_f,
        first.p,
    )
