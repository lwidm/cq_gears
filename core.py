import cadquery as cq
import numpy as np
from dataclasses import dataclass


@dataclass
class GearData:
    m: float
    z: int
    b: float

    alpha: float
    alpha_r: float
    beta: float
    beta_r: float
    beta_b: float
    beta_b_r: float

    ha_star: float
    c_star: float
    rho_f_star: float

    ha: float
    hf: float
    rho_f: float

    d: float
    db: float
    da: float
    df: float

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
