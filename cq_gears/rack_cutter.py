import cadquery as cq
import numpy as np

from .core import (
    GearData,
    SpurGearData,
    HelicalGearData,
)


def _create_rack_cutter_sketch(
    geardata: GearData,
    z: int | None = None,
) -> cq.Sketch:
    m_t: float = geardata.m_t
    z_eff: int = geardata.z if z is None else z
    p: float = geardata.p
    hf: float = geardata.hf
    ha: float = geardata.ha
    alpha_t: float = geardata.alpha_t
    alpha_t_r: float = geardata.alpha_t_r

    base_height: float = 3 * m_t
    rack_length: float = (z_eff + 4) * p
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
        .clean()
    )

    return rack_sketch


def create_rack_cutter(
    geardata: GearData,
    z: int | None = None,
    b: float | None = None,
) -> cq.Workplane:
    b_eff: float = geardata.b if b is None else b

    rack_sketch = _create_rack_cutter_sketch(geardata, z)

    rack: cq.Workplane
    base: cq.Workplane = cq.Workplane("XY").placeSketch(rack_sketch)

    match geardata:
        case SpurGearData():
            rack = base.extrude(b_eff / 2, both=True)
        case HelicalGearData():
            start_x: float = -b_eff / 2 * np.tan(geardata.beta_r)
            start_y: float = -b_eff / 2
            end_x: float = -start_x
            end_y: float = -start_y

            sweep_path: cq.Workplane = (
                cq.Workplane("XZ").moveTo(start_x, start_y).lineTo(end_x, end_y)
            )

            rack = base.sweep(sweep_path)
        case _:
            raise NotImplementedError(
                f'Currently only the following gear types are implemented: ["HelicalGear", "SpurGear"]. Got geardata of type: {type(geardata)}'
            )

    return rack


def create_rack_cutter_for_group(
    gear_data_list: list[GearData],
    group: set[int],
) -> cq.Workplane:
    gear_data_in_group: list[GearData] = [gear_data_list[i] for i in group]

    first: GearData = gear_data_in_group[0]
    z_max: int = max(gd.z for gd in gear_data_in_group)
    b_max: float = max(gd.b for gd in gear_data_in_group)

    return create_rack_cutter(
        geardata=first,
        z=z_max,
        b=b_max,
    )


def _cutters_are_compatible(
    gear_data_a: GearData, gear_data_b: GearData, tolerance: float = 1e-6
) -> bool:
    universal_ok: bool = (
        abs(gear_data_a.m_n - gear_data_b.m_n) < tolerance
        and abs(gear_data_a.alpha_n - gear_data_b.alpha_n) < tolerance
        and abs(gear_data_a.ha_star - gear_data_b.ha_star) < tolerance
        and abs(gear_data_a.c_star - gear_data_b.c_star) < tolerance
        and abs(gear_data_a.x - gear_data_b.x) < tolerance
    )
    if not universal_ok:
        return False

    if type(gear_data_a) is not type(gear_data_b):
        return False

    match (gear_data_a, gear_data_b):
        case SpurGearData(), SpurGearData():
            return True
        case HelicalGearData(), HelicalGearData():
            return abs(abs(gear_data_a.beta) - abs(gear_data_b.beta)) < tolerance
        case _:
            raise NotImplementedError(
                f'Currently only the following gear types are implemented for rack cutting: ["HelicalGear", "SpurGear"]. Got geardata of types: {type(gear_data_a)} and  {type(gear_data_b)}'
            )


def find_compatible_cutter_groups(
    gear_data_list: list[GearData], tolerance: float = 1e-6
) -> list[set[int]]:
    groups: list[set[int]] = []
    used: set[int] = set()

    for i, gear_data in enumerate(gear_data_list):
        if i in used:
            continue

        group: set[int] = {i}
        used.add(i)

        for j in range(i + 1, len(gear_data_list)):
            if j in used:
                continue

            if _cutters_are_compatible(gear_data, gear_data_list[j], tolerance):
                group.add(j)
                used.add(j)

        groups.append(group)

    return groups
