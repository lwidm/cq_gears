import cadquery as cq
from typing import Literal

from .core import GearData, Gear, GearList, find_compatible_groups
from .rack import create_rack_cutter_for_group
from .hobbing import simulate_gear_cutting
from .parametric_gear import parametric_gear_workplane


def initialize_gears(gear_data_list: list[GearData]) -> GearList:
    gear_list: list[Gear] = []
    for gear_data in gear_data_list:
        gear_list.append(Gear(gear_data, cq.Workplane(), cq.Workplane()))
    groups: list[set[int]] = find_compatible_groups(gear_data_list)

    return GearList(gear_list, groups)


def create_racks(gear_list: GearList) -> None:
    for group in gear_list.groups:
        gear_data_list: list[GearData] = [gear.data for gear in gear_list.gears]
        rack: cq.Workplane = create_rack_cutter_for_group(gear_data_list, group)
        for id in group:
            gear_list.gears[id].rack = rack


def cut_gears(
    gear_list: GearList,
    num_cut_positions: int,
    visualize: Literal[None, "show", "step", "img"],
) -> None:
    for i, gear in enumerate(gear_list.gears):
        gear_list.gears[i].workplane = simulate_gear_cutting(
            gear, num_cut_positions, visualize, i
        )

def build_parametric_gear(
        geardata: GearData,
        n_spline_points: int,
) -> Gear:
    if n_spline_points < 3:
        raise ValueError(f"n_spline_points must be greater than 3. Instead got {n_spline_points}")

    gear_workplane: cq.Workplane = parametric_gear_workplane(geardata, n_spline_points)
    gear: Gear = Gear(geardata, None, gear_workplane)

    return gear
