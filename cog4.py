import cadquery as cq
import numpy as np

m: float = 2.0  # Module, Modul
z: int = 4  # Number of teeth, Zähnezahl
x: float = 0.0  # Profile shift, Profilverschiebung
alpha: float = 20.0  # [degree] Pressure angle, Eingriffswinkel
thickness: float = 10
c_star: float = 0.167


def create_rack_cutter_sketch(
    m: float,
    alpha: float,
    ha_star: float,
    c_star: float,
    rho_f_star: float,
    z: int,
) -> cq.Sketch:
    """
    Create a rack cutter profile with multiple teeth.

    The rack consists of multiple trapezoid teeth with rounded tips,
    arranged along the X-axis with proper pitch spacing.

    Args:
        m: module (DE: Modul)
        alpha: pressure angle [degree] (DE: Eingriffswinkel [grad])
        ha_star: addendum coefficient (DE: Kopfhöhenfaktor)
        c_star: clearance coefficient (DE: Kopfspielfaktor)
        rho_f_star: fillet radius coefficient (DE: Fussrundungsfaktor).
                    If negative, use tangentArcPoint instead.
        z: number of teeth (DE: Zähnezahl)
    Returns:
        CadQuery Workplane with rack cutter profile
    """

    d: float = m * float(z)  # pitch diameter (DE: Teilkreisdurchmesser)
    ha: float = ha_star * m  # addendum (DE: Zahnkopfhöhe)
    hf: float = (ha_star + c_star) * m  # dedendum (DE: Zahnfusshöhe)
    rho_f: float = abs(rho_f_star) * m  # fillet radius at tip (DE: Fussrundung)
    alpha_r: float = np.radians(alpha)
    p: float = np.pi * m  # pitch (DE: Teilung)

    rack_length: float = (z + 4) * p
    base_height: float = 3 * m

    toothwidth_at_base: float = p / 2 + 2 * hf * np.tan(alpha_r)

    base: cq.Sketch = (
        cq.Sketch()
        .push([(0, -base_height / 2 - hf)])
        .rect(rack_length, base_height)
        .push([(0, (ha + hf) / 2 - hf)])
        .rarray(p, 1, z + 4, 1)
        .trapezoid(toothwidth_at_base, ha + hf, 90 - alpha, mode="a")
        .clean()
    )

    return base


rack_sketch: cq.Sketch = create_rack_cutter_sketch(
    m=m,
    alpha=alpha,
    ha_star=1.0,
    c_star=c_star,
    rho_f_star=0.3,
    z=z,
)

show_object(rack_sketch)
