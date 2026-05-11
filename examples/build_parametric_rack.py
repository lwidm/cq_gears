from cadquery.vis import show

import cq_gears

m_n: float = 2.0
b: float = 10.0
alpha_n: float = 20.0
delta: float = 90.0
ha_star: float = 1.0
c_star: float = 0.167
rho_f_star: float = 0.3
rail_width: float = 2.0

rack_data_1: cq_gears.RackGearData = cq_gears.make_rack_gear_data(
    m_n=m_n,
    z=20,
    b=b,
    x=0.0,
    alpha_n=alpha_n,
    ha_star=ha_star,
    c_star=c_star,
    rho_f_star=rho_f_star,
    rail_width=rail_width,
)

# gear_data_2: cq_gears.HelicalGearData = cq_gears.make_helical_gear_data(
#     m_n=m_n,
#     z=20,
#     b=b,
#     x=1.2,
#     alpha_n=alpha_n,
#     beta=5.0,
#     ha_star=ha_star,
#     c_star=c_star,
#     rho_f_star=rho_f_star,
# )


gear1: cq_gears.ParametricGear = cq_gears.build_parametric_gear(rack_data_1, 200)
# gear2: cq_gears.ParametricGear = cq_gears.build_parametric_gear(gear_data_2, 200)

show(gear1.workplane)
# show(gear2.workplane)
