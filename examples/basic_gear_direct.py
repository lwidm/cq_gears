import cadquery as cq
from cadquery.vis import show
from pathlib import Path

import cq_gears
from cq_gears.core import GearData
from cq_gears import gear_direct

m: float = 2.0
b: float = 10.0
alpha_t: float = 20.0
beta: float = 0.0
delta: float = 90.0
ha_star: float = 1.0
c_star: float = 0.167
rho_f_star: float = 0.3

gear_data_1: GearData = cq_gears.compute_gear_data(
    m=m,
    z=20,
    b=b,
    x=0.0,
    alpha_t=alpha_t,
    beta=beta,
    delta=delta,
    ha_star=ha_star,
    c_star=c_star,
    rho_f_star=rho_f_star,
)

gear_data_2: GearData = cq_gears.compute_gear_data(
    m=m,
    z=20,
    b=b,
    x=0.5,
    alpha_t=alpha_t,
    beta=beta,
    delta=delta,
    ha_star=ha_star,
    c_star=c_star,
    rho_f_star=rho_f_star,
)


gear_sketch: cq.Sketch = gear_direct._tooth_sketch(gear_data_1, 200)

show(gear_sketch)
