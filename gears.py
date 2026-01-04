import cadquery as cq
from cadquery.cq import Workplane
from cadquery.occ_impl.shapes import extrude
import numpy as np
from typing import Literal
from pathlib import Path
import pyvista as pv
from dataclasses import dataclass

from helpers import setup_visualization, visualize_step


@dataclass
class GearData:
    # module (DE: Modul)
    m: float
    # number of teeth (DE: Zähnezahl)
    z: int
    # face width (DE: Zahnbreite) - the axial/z-direction thickness
    b: float

    # pressure angle [degrees] (DE: Eingriffswinkel [grad])
    alpha: float
    # pressure angle [radian] (DE: Eingriffswinkel [radian])
    alpha_r: float
    # helix angle at pitch circle [degrees] (DE: Schrägungswinkel am Teilkreis [raidan])
    beta: float
    # helix angle at pitch circle [radian] (DE: Schrägungswinkel am Teilkreis [radian])
    beta_r: float
    # helix angle at base circle [degrees] (DE: Schrägungswinkel am Grundkreis [degrees])
    beta_b: float
    # helix angle at base circle [radian] (DE: Schrägungswinkel am Grundkreis [radian])
    beta_b_r: float

    # addendum coefficient (DE: Kopfhöhenfaktor)
    ha_star: float
    # clearance coefficient (DE: Kopfspielfaktor)
    c_star: float
    # fillet radius coefficent (DE: Fussrundingsfaktor)
    rho_f_star: float
    # pitch diameter (DE: Teilkreisdurchmesser)

    # addendum (DE: Zahnkopfhöhe)
    ha: float
    # dedendum (DE: Zahnfusshöhe)
    hf: float
    # fillet radius at tip (DE: Fussrundung)
    rho_f: float

    # pitch diameter (DE: Teilkreisdurchmesser)
    d: float
    # base diameter (DE: Grundkreisdurchmesser)
    db: float
    # tip/addendum diameter (DE: Kopfkreisdurchmesser)
    da: float
    # root diameter (DE: Fusskreisdurchmesser)
    df: float

    # pitch (DE: Teilung)
    p: float


@dataclass
class Gear:
    data: GearData
    rack: cq.Workplane | None
    workplane: cq.Workplane | None


@dataclass
class GearList:
    gears: list[Gear]
    groups: list[set[int]]


def compute_gear_data(
    m: float,
    z: int,
    b: float,
    alpha: float,
    beta: float,
    ha_star: float,
    c_star: float,
    rho_f_star: float,
) -> GearData:
    alpha_r: float = np.radians(alpha)
    beta_r: float = np.radians(beta)

    p: float = np.pi * m

    # Helix angle at base circle
    # For spur gears (beta=0), beta_b=0
    # For helical gears: tan(beta_b) = tan(beta) * cos(alpha)
    beta_b_r: float = np.arctan(np.tan(beta_r) * np.cos(alpha_r))
    beta_b: float = np.degrees(beta_b_r)

    ha: float = ha_star * m
    hf: float = (ha_star + c_star) * m
    rho_f: float = abs(rho_f_star) * m

    d: float = m * float(z)
    db: float = d * np.cos(alpha_r)
    df: float = d - 2 * hf
    da: float = d + 2 * ha

    return GearData(
        m=m,
        z=z,
        b=b,
        alpha=alpha,
        alpha_r=alpha_r,
        beta=beta,
        beta_r=beta_r,
        beta_b=beta_b,
        beta_b_r=beta_b_r,
        ha_star=ha_star,
        c_star=c_star,
        rho_f_star=rho_f_star,
        ha=ha,
        hf=hf,
        rho_f=rho_f,
        d=d,
        db=db,
        df=df,
        da=da,
        p=p,
    )


def _are_compatible(
    gear_data_a: GearData, gear_data_b: GearData, tolerance: float = 1e-6
) -> bool:
    return (
        abs(gear_data_a.m - gear_data_b.m) < tolerance
        and abs(gear_data_a.alpha - gear_data_b.alpha) < tolerance
        and abs(abs(gear_data_a.beta) - abs(gear_data_b.beta)) < tolerance
        and abs(gear_data_a.ha_star - gear_data_b.ha_star) < tolerance
        and abs(gear_data_a.c_star - gear_data_b.c_star) < tolerance
    )


def _find_compatible_groups(
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

            if _are_compatible(gear_data, gear_data_list[j], tolerance):
                group.add(j)
                used.add(j)

        groups.append(group)

    return groups


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


def _simulate_gear_cutting(
    gear: Gear,
    num_cut_positions: int,
    visualize: Literal[None, "show", "step", "img"],
) -> cq.Workplane:

    if gear.rack is None:
        raise ValueError(
            "Could not simulate gear cutting. No rack found in gear (None value)"
        )
    rack: cq.Workplane = gear.rack

    m: float = gear.data.m
    z: float = gear.data.z
    b: float = gear.data.b
    d: float = gear.data.d
    p: float = gear.data.p

    r: float = d / 2
    d_blank: float = d + 3 * m

    gear_blank: cq.Workplane = cq.Workplane("XY").circle(d_blank / 2).extrude(b)

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

        positioned_rack: cq.Workplane = rack.translate((-x_rack, -r, 0.0)).rotate(
            (0, 0, 0), (0, 0, 1), np.degrees(theta)
        )

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
        gear_list.gears[i].workplane = _simulate_gear_cutting(
            gear, num_cut_positions, visualize
        )
