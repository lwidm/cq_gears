import cadquery as cq
from typing import Literal

from core import GearData, Gear, GearList, _find_compatible_groups
from rack import _create_rack_cutter_for_group
from hobbing import _simulate_gear_cutting


def initialize_gears(gear_data_list: list[GearData]) -> GearList:
    gear_list: list[Gear] = []
    for gear_data in gear_data_list:
        gear_list.append(Gear(gear_data, None, None))
    groups: list[set[int]] = _find_compatible_groups(gear_data_list)

    return GearList(gear_list, groups)


def create_racks(gear_list: GearList) -> None:
    for group in gear_list.groups:
        gear_data_list: list[GearData] = [gear.data for gear in gear_list.gears]
        rack: cq.Workplane = _create_rack_cutter_for_group(gear_data_list, group)
        for id in group:
            gear_list.gears[id].rack = rack


def cut_gears(
    gear_list: GearList,
    num_cut_positions: int,
    visualize: Literal[None, "show", "step", "img"],
) -> None:
    for i, gear in enumerate(gear_list.gears):
        gear_list.gears[i].workplane = _simulate_gear_cutting(gear, num_cut_positions, visualize)
