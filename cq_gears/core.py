import cadquery as cq
import numpy as np
from dataclasses import dataclass
from typing import Protocol, runtime_checkable, TypeAlias, TypeVar

_GEAR_TYPE_REGISTRY: list[type] = []
_GEAR_SOLID_REGISTRY: list[type] = []

_GearClassT = TypeVar("_GearClassT", bound=type)
def _register_gear_type(klass: _GearClassT) -> _GearClassT:
    """Decorator that marks a gear data class as implemented"""
    _GEAR_TYPE_REGISTRY.append(klass)
    return klass


def implemented_gear_types() -> list[type]:
    return _GEAR_TYPE_REGISTRY

def _register_gear_solid(klass: _GearClassT) -> _GearClassT:
    """Decorator that marks a gear data class as implemented"""
    _GEAR_SOLID_REGISTRY.append(klass)
    return klass


def implemented_gear_solids() -> list[type]:
    return _GEAR_SOLID_REGISTRY


@runtime_checkable
class GearData(Protocol):
    """
    Structural Interface that every gear data record must satisfy.

    Operations that work for any gear type should type-hint against this
    Protocol. Concrete gear dataclasses (SpurGear, HelicalGear, etc.) do
    NOT inherit from it. They need to satisfy it structuraly just by
    having every listed field with a compatible type.
    """

    # ===== User inputs =====
    # normal module (DE: Normalmodul)
    @property
    def m_n(self)-> float: ...
    # number of teeth (DE: Zähnezahl)
    @property
    def z(self)-> int: ...
    # face width (DE: Zahnbreite) - the axial/z-direction thickness
    @property
    def b(self)-> float: ...
    # profile shift coefficient (DE: Profilverschiebung)
    @property
    def x(self)-> float: ...
    # normal pressure angle [degrees] (DE: Normaleingriffswinkel [grad])
    @property
    def alpha_n(self)-> float: ...
    # addendum coefficient (DE: Kopfhöhenfaktor)
    @property
    def ha_star(self)-> float: ...
    # clearance coefficient (DE: Kopfspielfaktor)
    @property
    def c_star(self)-> float: ...
    # fillet radius coefficent (DE: Fussrundingsfaktor)
    @property
    def rho_f_star(self)-> float: ...

    # ===== Derived (universal across all gear types) =====
    # normal pressure angle [radian] (DE: Normaleingriffswinkel [radian])
    @property
    def alpha_n_r(self)-> float: ...
    # transverse module (DE: Stirnmodul) - derived as m_n / cos(beta)
    @property
    def m_t(self)-> float: ...
    # transverse pressure angle [degrees] (DE: Stirneingriffswinkel [grad])
    @property
    def alpha_t(self)-> float: ...
    # transverse pressure angle [radian] (DE: Stirneingriffswinkel [radian])
    @property
    def alpha_t_r(self)-> float: ...
    # pitch (DE: Teilung)
    @property
    def p(self)-> float: ...
    # addendum (DE: Zahnkopfhöhe)
    @property
    def ha(self)-> float: ...
    # dedendum (DE: Zahnfusshöhe)
    @property
    def hf(self)-> float: ...
    # fillet radius at tip (DE: Fussrundung)
    @property
    def rho_f(self)-> float: ...
    # pitch diameter (DE: Teilkreisdurchmesser)
    @property
    def dp(self)-> float: ...
    # base diameter (DE: Grundkreisdurchmesser)
    @property
    def db(self)-> float: ...
    # tip/addendum diameter (DE: Kopfkreisdurchmesser)
    @property
    def da(self)-> float: ...
    # root diameter (DE: Fusskreisdurchmesser)
    @property
    def df(self)-> float: ...


@_register_gear_type
@dataclass(frozen=True, kw_only=True)
class SpurGearData:
    """
    External spur gear data(beta = 0)

    Holds both user inputs and the derived geometry. Constructs via
    make_spur_gear_data(...).

    Direct construction requires all fields.
    """

    # ===== Inputs =====
    m_n: float
    z: int
    b: float
    x: float
    alpha_n: float
    ha_star: float
    c_star: float
    rho_f_star: float

    # ===== Derived =====
    alpha_n_r: float
    m_t: float
    alpha_t: float
    alpha_t_r: float
    p: float
    ha: float
    hf: float
    rho_f: float
    dp: float
    db: float
    da: float
    df: float


def make_spur_gear_data(
    *,
    m_n: float,
    z: int,
    b: float,
    x: float = 0.0,
    alpha_n: float = 20,
    ha_star: float = 1.0,
    c_star: float = 0.25,
    rho_f_star: float = 0.3,
) -> SpurGearData:
    """Constructs a SpurGearData from user inputs, computing all derived fields"""

    alpha_n_r: float = np.radians(alpha_n)
    # Spur: transverse equals normal
    m_t: float = m_n
    alpha_t: float = alpha_n
    alpha_t_r: float = alpha_n_r

    p: float = np.pi * m_t
    ha: float = (ha_star + x) * m_n
    hf: float = (ha_star + c_star - x) * m_n
    rho_f: float = abs(rho_f_star) * m_n
    dp: float = m_t * float(z)
    db: float = dp * np.cos(alpha_t_r)
    da: float = dp + 2 * ha
    df: float = dp - 2 * hf

    return SpurGearData(
        m_n=m_n,
        z=z,
        b=b,
        x=x,
        alpha_n=alpha_n,
        ha_star=ha_star,
        c_star=c_star,
        rho_f_star=rho_f_star,
        alpha_n_r=alpha_n_r,
        m_t=m_t,
        alpha_t=alpha_t,
        alpha_t_r=alpha_t_r,
        p=p,
        ha=ha,
        hf=hf,
        rho_f=rho_f,
        dp=dp,
        db=db,
        da=da,
        df=df,
    )


@_register_gear_type
@dataclass(frozen=True, kw_only=True)
class HelicalGearData:
    """
    External helical gear data (beta > 0)

    Same universal fields as SpurGearData, plus the helical-specific
    inputs and derived fields (beta, beta_r, beta_b, beta_b_r)
    """

    # ===== Inputs =====
    m_n: float
    z: int
    b: float
    x: float
    alpha_n: float
    ha_star: float
    c_star: float
    rho_f_star: float
    # ===== Inputs - Helix specific =====
    # helix angle at pitch circle [degrees] (DE: Schrägungswinkel am Teilkreis [raidan])
    beta: float

    # ===== Derived =====
    alpha_n_r: float
    m_t: float
    alpha_t: float
    alpha_t_r: float
    p: float
    ha: float
    hf: float
    rho_f: float
    dp: float
    db: float
    da: float
    df: float
    # ===== Derived - Helix specific =====
    # helix angle at pitch circle [radian] (DE: Schrägungswinkel am Teilkreis [radian])
    beta_r: float
    # helix angle at base circle [degrees] (DE: Schrägungswinkel am Grundkreis [degrees])
    beta_b: float
    # helix angle at base circle [radian] (DE: Schrägungswinkel am Grundkreis [radian])
    beta_b_r: float


def make_helical_gear_data(
    *,
    m_n: float,
    z: int,
    b: float,
    beta: float,
    x: float = 0.0,
    alpha_n: float = 20.0,
    ha_star: float = 1.0,
    c_star: float = 0.25,
    rho_f_star: float = 0.3,
) -> HelicalGearData:
    """Construct a HelicalGearData from user inputs, computing all derived fields."""

    alpha_n_r: float = np.radians(alpha_n)
    beta_r: float = np.radians(beta)

    # Helical conversion (transverse derived from normal)
    alpha_t_r: float = np.arctan(np.tan(alpha_n_r) / np.cos(beta_r))
    alpha_t: float = np.degrees(alpha_t_r)
    m_t: float = m_n / np.cos(beta_r)

    # Base helix angle
    beta_b_r: float = np.arctan(np.tan(beta_r) * np.cos(alpha_t_r))
    beta_b: float = np.degrees(beta_b_r)

    # Universal derived
    p: float = np.pi * m_t
    ha: float = (ha_star + x) * m_n
    hf: float = (ha_star + c_star - x) * m_n
    rho_f: float = abs(rho_f_star) * m_n
    dp: float = m_t * z
    db: float = dp * np.cos(alpha_t_r)
    da: float = dp + 2 * ha
    df: float = dp - 2 * hf

    return HelicalGearData(
        m_n=m_n,
        z=z,
        b=b,
        beta=beta,
        x=x,
        alpha_n=alpha_n,
        ha_star=ha_star,
        c_star=c_star,
        rho_f_star=rho_f_star,
        alpha_n_r=alpha_n_r,
        m_t=m_t,
        alpha_t=alpha_t,
        alpha_t_r=alpha_t_r,
        p=p,
        ha=ha,
        hf=hf,
        rho_f=rho_f,
        dp=dp,
        db=db,
        da=da,
        df=df,
        beta_r=beta_r,
        beta_b=beta_b,
        beta_b_r=beta_b_r,
    )


@_register_gear_type
@dataclass(frozen=True, kw_only=True)
class InternalSpurGearData:
    """
    Internal (ring) spur gear data (beta = 0).

    Same fields as SpurGearData, but the geometry is inverted:
    d_a < d_p < d_f (the tooth points inward toward the gear axis).
    """

    # ===== Inputs =====
    m_n: float
    z: int
    b: float
    x: float
    alpha_n: float
    ha_star: float
    c_star: float
    rho_f_star: float

    # ===== Derived =====
    alpha_n_r: float
    m_t: float
    alpha_t: float
    alpha_t_r: float
    p: float
    ha: float
    hf: float
    rho_f: float
    dp: float
    db: float
    da: float
    df: float


def make_internal_spur_gear_data(
    *,
    m_n: float,
    z: int,
    b: float,
    x: float = 0.0,
    alpha_n: float = 20.0,
    ha_star: float = 1.0,
    c_star: float = 0.25,
    rho_f_star: float = 0.3,
) -> InternalSpurGearData:
    """Construct an InternalSpurGearData from user inputs, computing all derived fields."""
    # BUG : unverified math (just intuition for now)

    alpha_n_r: float = np.radians(alpha_n)
    # Internal spur: transverse equals normal (no helix)
    m_t: float = m_n
    alpha_t: float = alpha_n
    alpha_t_r: float = alpha_n_r

    p: float = np.pi * m_t
    ha: float = (ha_star + x) * m_n
    hf: float = (ha_star + c_star - x) * m_n
    rho_f: float = abs(rho_f_star) * m_n
    dp: float = m_t * z
    db: float = dp * np.cos(alpha_t_r)

    # *** Internal-gear sign flip on tip and root diameters ***
    da: float = dp - 2 * ha
    df: float = dp + 2 * hf

    return InternalSpurGearData(
        m_n=m_n,
        z=z,
        b=b,
        x=x,
        alpha_n=alpha_n,
        ha_star=ha_star,
        c_star=c_star,
        rho_f_star=rho_f_star,
        alpha_n_r=alpha_n_r,
        m_t=m_t,
        alpha_t=alpha_t,
        alpha_t_r=alpha_t_r,
        p=p,
        ha=ha,
        hf=hf,
        rho_f=rho_f,
        dp=dp,
        db=db,
        da=da,
        df=df,
    )


@_register_gear_type
@dataclass(frozen=True, kw_only=True)
class InternalHelicalGearData:
    """
    Internal (ring) helical gear data (beta > 0).

    Combines the helix-angle inputs and derivations from HelicalGearData
    with the inverted geometry from InternalSpurGearData:
    d_a < d_p < d_f (the tooth points inward toward the gear axis).
    """

    # ===== Inputs =====
    m_n: float
    z: int
    b: float
    x: float
    alpha_n: float
    ha_star: float
    c_star: float
    rho_f_star: float
    # ===== Inputs - Helix specific =====
    # helix angle at pitch circle [degrees] (DE: Schrägungswinkel am Teilkreis [grad])
    beta: float

    # ===== Derived =====
    alpha_n_r: float
    m_t: float
    alpha_t: float
    alpha_t_r: float
    p: float
    ha: float
    hf: float
    rho_f: float
    dp: float
    db: float
    da: float
    df: float
    # ===== Derived - Helix specific =====
    # helix angle at pitch circle [radian] (DE: Schrägungswinkel am Teilkreis [radian])
    beta_r: float
    # helix angle at base circle [degrees] (DE: Schrägungswinkel am Grundkreis [grad])
    beta_b: float
    # helix angle at base circle [radian] (DE: Schrägungswinkel am Grundkreis [radian])
    beta_b_r: float


def make_internal_helical_gear_data(
    *,
    m_n: float,
    z: int,
    b: float,
    beta: float,
    x: float = 0.0,
    alpha_n: float = 20.0,
    ha_star: float = 1.0,
    c_star: float = 0.25,
    rho_f_star: float = 0.3,
) -> InternalHelicalGearData:
    """Construct an InternalHelicalGearData from user inputs, computing all derived fields."""
    # BUG : unverified math (just intuition for now)

    alpha_n_r: float = np.radians(alpha_n)
    beta_r: float = np.radians(beta)

    # Helical conversion (transverse derived from normal)
    alpha_t_r: float = np.arctan(np.tan(alpha_n_r) / np.cos(beta_r))
    alpha_t: float = np.degrees(alpha_t_r)
    m_t: float = m_n / np.cos(beta_r)

    # Base helix angle
    beta_b_r: float = np.arctan(np.tan(beta_r) * np.cos(alpha_t_r))
    beta_b: float = np.degrees(beta_b_r)

    # Universal derived
    p: float = np.pi * m_t
    ha: float = (ha_star + x) * m_n
    hf: float = (ha_star + c_star - x) * m_n
    rho_f: float = abs(rho_f_star) * m_n
    dp: float = m_t * z
    db: float = dp * np.cos(alpha_t_r)

    # *** Internal-gear sign flip on tip and root diameters ***
    da: float = dp - 2 * ha
    df: float = dp + 2 * hf

    return InternalHelicalGearData(
        m_n=m_n,
        z=z,
        b=b,
        beta=beta,
        x=x,
        alpha_n=alpha_n,
        ha_star=ha_star,
        c_star=c_star,
        rho_f_star=rho_f_star,
        alpha_n_r=alpha_n_r,
        m_t=m_t,
        alpha_t=alpha_t,
        alpha_t_r=alpha_t_r,
        p=p,
        ha=ha,
        hf=hf,
        rho_f=rho_f,
        dp=dp,
        db=db,
        da=da,
        df=df,
        beta_r=beta_r,
        beta_b=beta_b,
        beta_b_r=beta_b_r,
    )


@dataclass(frozen=True, kw_only=True)
class BevelGearData:
    """
    Bevel (conical) gear data (DE: Kegelräder). Not yet implemented.
    """

    # ===== Inputs =====
    m_n: float
    z: int
    b: float
    x: float
    alpha_n: float
    ha_star: float
    c_star: float
    rho_f_star: float
    # ===== Inputs - Bevel gear specific =====
    # pitch cone angle [degrees] (DE: Teilkegelwinkel)
    delta: float

    # ===== Derived =====
    alpha_n_r: float
    m_t: float
    alpha_t: float
    alpha_t_r: float
    p: float
    ha: float
    hf: float
    rho_f: float
    dp: float
    db: float
    da: float
    df: float
    # ===== Derived - Bevel gear specific =====
    # pitch cone angle [radian] (DE: Teilkegelwinkel)
    delta_r: float


def make_bevel_gear_data(
    *,
    m_n: float,
    z: int,
    b: float,
    delta: float,
    x: float = 0.0,
    alpha_n: float = 20.0,
    ha_star: float = 1.0,
    c_star: float = 0.25,
    rho_f_star: float = 0.3,
) -> BevelGearData:
    """Construct a BevelGearData. Not yet implemented."""
    raise NotImplementedError("Bevel gears are not yet implemented.")


@dataclass(frozen=True, kw_only=True)
class WormGearData:
    """
    Worm gear data (DE: Schneckenräder). Not yet implemented.

    TODO
    """

    pass


def make_worm_gear_data(
    *,
    m_n: float,
    z: int,
    b: float,
    x: float = 0.0,
    alpha_n: float = 20.0,
    ha_star: float = 1.0,
    c_star: float = 0.25,
    rho_f_star: float = 0.3,
) -> WormGearData:
    """Construct a WormGearData. Not yet implemented."""
    raise NotImplementedError("Worm gears are not yet implemented.")


@dataclass(frozen=True, kw_only=True)
class CrossedHelicalGearData:
    """
    Crossed helical / screw / hyperboloid gear data
    (DE: Schraubenverzahnung / Hyperboloidräder). Not yet implemented.

    TODO
    """

    pass


def make_crossed_helical_gear_data(
    *,
    m_n: float,
    z: int,
    b: float,
    beta: float,
    x: float = 0.0,
    alpha_n: float = 20.0,
    ha_star: float = 1.0,
    c_star: float = 0.25,
    rho_f_star: float = 0.3,
) -> CrossedHelicalGearData:
    """Construct a CrossedHelicalGearData. Not yet implemented."""
    raise NotImplementedError("Crossed helical gears are not yet implemented.")


@dataclass(frozen=True, kw_only=True)
class HypoidGearData:
    """
    Hypoid gear data (DE: Schraubenkegelräder / Hypoidräder).
    Not yet implemented.

    TODO
    """

    pass


def make_hypoid_gear_data(
    *,
    m_n: float,
    z: int,
    b: float,
    delta: float,
    x: float = 0.0,
    alpha_n: float = 20.0,
    ha_star: float = 1.0,
    c_star: float = 0.25,
    rho_f_star: float = 0.3,
) -> HypoidGearData:
    """Construct a HypoidGearData. Not yet implemented."""
    raise NotImplementedError("Hypoid gears are not yet implemented.")


# A union of every concrete gear data type. Use this as the parameter
# type for dispatch helpers and any function that pattern-matches on
# the concrete gear type
GearDataConcrete: TypeAlias = (
    SpurGearData | HelicalGearData | InternalSpurGearData | InternalHelicalGearData
)


def is_helical(gear: GearDataConcrete) -> bool:
    match gear:
        case HelicalGearData() | InternalHelicalGearData():
            return True
        case _:
            return False


def is_internal(gear: GearDataConcrete) -> bool:
    match gear:
        case InternalSpurGearData() | InternalHelicalGearData():
            return True
        case _:
            return False


@dataclass
class _LegacyGear:
    data: GearData
    rack: cq.Workplane | None
    workplane: cq.Workplane


@dataclass
class GearList:
    gears: list[_LegacyGear]
    groups: list[set[int]]

@runtime_checkable
class Gear(Protocol):
    """
    Structural interface that every constructed gear must satisfy.

    A "gear" here is a 3D solid (cq.Workplane) plus the data it was
    built from. Operations that just need to read the workplane or
    data should type-hint against this Protocol.
    """

    @property
    def data(self)-> GearData: ...
    @property
    def workplane(self)-> cq.Workplane: ...

@_register_gear_solid
@dataclass(frozen=True, kw_only=True)
class ParametricGear():
    """
    A gear built from closed-form parametric equations: points
    along the involute and undercut curves, stiched into a sketch
    and extruded (or twist-extruded for helical)
    """
    data: GearData
    workplane: cq.Workplane

@_register_gear_solid
@dataclass(frozen=True, kw_only=True)
class HobbedGear():
    """
    A gear built by simulating a rack (or shaper) cutter rolling
    on a cylindrical blank. Slower then parametric and approximated
    by short streight cuts, but mirrors how real gears are produced
    """
    data: GearData
    workplane: cq.Workplane
    cutter: cq.Workplane

GearConcrete: TypeAlias = ParametricGear | HobbedGear

def _are_compatible(
    gear_data_a: GearData, gear_data_b: GearData, tolerance: float = 1e-6
) -> bool:
    return (
        abs(gear_data_a.m_n - gear_data_b.m_n) < tolerance
        and abs(gear_data_a.alpha_n - gear_data_b.alpha_n) < tolerance
        and abs(abs(gear_data_a.beta) - abs(gear_data_b.beta)) < tolerance
        and abs(gear_data_a.delta - gear_data_b.delta) < tolerance
        and abs(gear_data_a.ha_star - gear_data_b.ha_star) < tolerance
        and abs(gear_data_a.c_star - gear_data_b.c_star) < tolerance
        and abs(gear_data_a.x - gear_data_b.x) < tolerance
    )


def find_compatible_groups(
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
