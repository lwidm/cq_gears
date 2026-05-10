import cadquery as cq
from cadquery.vis import show
from pathlib import Path

import cq_gears

m_n: float = 2.0
b: float = 10.0
alpha_n: float = 20.0
beta: float = 20.0
ha_star: float = 1.0
c_star: float = 0.167
rho_f_star: float = 0.3

gear_data_1: cq_gears.HelicalGearData = cq_gears.make_helical_gear_data(
    m_n=m_n,
    z=20,
    b=b,
    x=0.0,
    alpha_n=alpha_n,
    beta=beta,
    ha_star=ha_star,
    c_star=c_star,
    rho_f_star=rho_f_star,
)

gear_data_2: cq_gears.HelicalGearData = cq_gears.make_helical_gear_data(
    m_n=m_n,
    z=20,
    b=b,
    x=0.5,
    alpha_n=alpha_n,
    beta=beta,
    ha_star=ha_star,
    c_star=c_star,
    rho_f_star=rho_f_star,
)

gear_list: list[cq_gears.HobbedGear] = cq_gears.build_hobbed_gear_list(
    [gear_data_1, gear_data_2], n_cut_positions=20, visualize="img"
)

cq_gears.create_video(
    input_dir=Path("output/img/0"),
    output_path=Path("output/1.mp4"),
    delete_frames=True,
    video_length=10.0,
)

gear1: cq.Workplane = gear_list[0].workplane
gear2: cq.Workplane = gear_list[1].workplane

rack1: cq.Workplane = gear_list[0].cutter
rack2: cq.Workplane = gear_list[1].cutter

# show_object(rack1)
# show_object(rack2)
show(gear1)
show(gear2)
# show_object(gear2)
# show_object(gear1.cut(gear2))
# show_object(rack2.cut(rack1))
