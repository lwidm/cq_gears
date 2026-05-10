import cadquery as cq
from typing import Literal


from .core import (
    GearData,
    HobbedGear,
    ParametricGear,
)
from .rack_cutter import (
    create_rack_cutter_for_group,
    create_rack_cutter,
    find_compatible_cutter_groups,
)
from .hobbing import simulate_gear_cutting
from .parametric_gear import parametric_gear_workplane


def build_hobbed_gear(
    geardata: GearData,
    n_cut_positions: int,
    visualize: Literal[None, "show", "step", "img"],
    gear_index: int,
) -> HobbedGear:
    cutter: cq.Workplane = create_rack_cutter(geardata)
    workplane: cq.Workplane = simulate_gear_cutting(
        geardata, cutter, n_cut_positions, visualize, gear_index
    )
    return HobbedGear(data=geardata, workplane=workplane, cutter=cutter)


def build_hobbed_gear_list(
    geardata_list: list[GearData],
    n_cut_positions: int,
    visualize: Literal[None, "show", "step", "img"],
) -> list[HobbedGear]:
    groups: list[set[int]] = find_compatible_cutter_groups(geardata_list)
    cutter_by_index: dict[int, cq.Workplane] = {}
    for group in groups:
        cutter: cq.Workplane = create_rack_cutter_for_group(geardata_list, set(group))
        for idx in group:
            cutter_by_index[idx] = cutter
    workplane_list: list[cq.Workplane] = []
    for idx, geardata in enumerate(geardata_list):
        workplane_list.append(
            simulate_gear_cutting(
                geardata, cutter_by_index[idx], n_cut_positions, visualize, idx
            )
        )
    return [
        HobbedGear(
            data=geardata_list[idx],
            workplane=workplane_list[idx],
            cutter=cutter_by_index[idx],
        )
        for idx in range(len(geardata_list))
    ]


def build_parametric_gear(
    geardata: GearData,
    n_spline_points: int,
) -> ParametricGear:
    if n_spline_points < 3:
        raise ValueError(
            f"n_spline_points must be greater than 3. Instead got {n_spline_points}"
        )

    gear_workplane: cq.Workplane = parametric_gear_workplane(geardata, n_spline_points)
    gear: ParametricGear = ParametricGear(data=geardata, workplane=gear_workplane)

    return gear
