import cadquery as cq
import numpy as np
from dataclasses import dataclass


@dataclass
class GearData:
    # module (DE: Modul)
    m: float
    # number of teeth (DE: Zähnezahl)
    z: int
    # face width (DE: Zahnbreite) - the axial/z-direction thickness
    b: float
    # profile shift coefficient (DE: Profilverschiebung)
    x: float

    # transverse pressure angle [degrees] (DE: Stirneingriffswinkel [grad])
    alpha_t: float
    # transverse pressure angle [radian] (DE: Stirneingriffswinkel [radian])
    alpha_t_r: float
    # normal pressure angle [degrees] (DE: Normaleingriffswinkel [grad])
    alpha_n: float
    # normal pressure angle [radian] (DE: Normaleingriffswinkel [radian])
    alpha_n_r: float
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
    x: float,
    alpha_t: float,
    beta: float,
    ha_star: float,
    c_star: float,
    rho_f_star: float,
) -> GearData:
    alpha_t_r: float = np.radians(alpha_t)
    beta_r: float = np.radians(beta)

    alpha_n_r: float = np.arctan(np.tan(alpha_t_r) * np.sin(beta_r))
    alpha_n: float = np.degrees(alpha_n_r)

    p: float = np.pi * m

    beta_b_r: float = np.arctan(np.cos(alpha_t_r) / np.tan(beta_r)) if beta != 0 else 0.0
    beta_b: float = np.degrees(beta_b_r)

    ha: float = (ha_star + x) * m
    hf: float = (ha_star + c_star - x) * m
    rho_f: float = abs(rho_f_star) * m

    d: float = m * float(z)
    db: float = d * np.cos(alpha_t_r)
    df: float = d - 2 * hf
    da: float = d + 2 * ha

    return GearData(
        m=m,
        z=z,
        b=b,
        x=x,
        alpha_t=alpha_t,
        alpha_t_r=alpha_t_r,
        alpha_n=alpha_n,
        alpha_n_r=alpha_n_r,
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
        and abs(gear_data_a.alpha_t - gear_data_b.alpha_t) < tolerance
        and abs(gear_data_a.alpha_n - gear_data_b.alpha_n) < tolerance
        and abs(abs(gear_data_a.beta) - abs(gear_data_b.beta)) < tolerance
        and abs(gear_data_a.ha_star - gear_data_b.ha_star) < tolerance
        and abs(gear_data_a.c_star - gear_data_b.c_star) < tolerance
        and abs(gear_data_a.x - gear_data_b.x) < tolerance
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
