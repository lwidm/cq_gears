import cadquery as cq
import numpy as np

from .core import GearData


def _create_single_rack_sketch(
    m: float,
    z: int,
    ha: float,
    hf: float,
    alpha_t: float,
    alpha_t_r: float,
    rho_f: float,
    p: float,
) -> cq.Sketch:
    base_height: float = 3 * m
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
        .reset()
        .vertices("not (<Y or >Y or <X or >X)")
        .fillet(rho_f)
        .clean()
    )

    return rack_sketch


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
    delta_r: float,
) -> cq.Workplane:

    rack_sketch = _create_single_rack_sketch(
        m=m, z=z, ha=ha, hf=hf, alpha_t=alpha_t, alpha_t_r=alpha_t_r, rho_f=rho_f, p=p
    )

    rack: cq.Workplane

    if np.isclose(delta_r, np.pi / 2):
        base: cq.Workplane = cq.Workplane("XY").placeSketch(rack_sketch)

        if np.isclose(beta_r, 0.0):
            rack = base.extrude(b / 2, both=True)
        else:
            start_x: float = -b / 2 * np.tan(beta_r)
            start_y: float = -b / 2
            end_x: float = -start_x
            end_y: float = -start_y

            sweep_path: cq.Workplane = (
                cq.Workplane("XZ").moveTo(start_x, start_y).lineTo(end_x, end_y)
            )

            rack = base.sweep(sweep_path)

    else:
        raise NotImplementedError("No beval gear rack cutter implemented")

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
        first.delta_r,
    )
