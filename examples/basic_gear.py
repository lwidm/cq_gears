import cadquery as cq
from cadquery.vis import show
from pathlib import Path

import cq_gears

m: float = 2.0
b: float = 10.0
alpha_t: float = 20.0
beta: float = 0.0
delta: float = 60.0
ha_star: float = 1.0
c_star: float = 0.167
rho_f_star: float = 0.3

gear_data_1 = cq_gears.compute_gear_data(
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

gear_data_2 = cq_gears.compute_gear_data(
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

# gear_list = cq_gears.initialize_gears([gear_data_1, gear_data_2])
gear_list = cq_gears.initialize_gears([gear_data_1])

cq_gears.create_racks(gear_list)

# cq_gears.cut_gears(gear_list, num_cut_positions=20, visualize=None)

# cq_gears.create_video(
#     input_dir=Path("output/img/0"),
#     output_path=Path("output/1.mp4"),
#     delete_frames=True,
#     video_length=10.0
# )

# gear1: cq.Workplane = gear_list.gears[0].workplane
# gear2: cq.Workplane = gear_list.gears[1].workplane

rack1: cq.Workplane = gear_list.gears[0].rack
# rack2: cq.Workplane = gear_list.gears[1].rack

# show_object(rack1)
# show_object(rack2)
show(rack1)
# show_object(gear2)
# show_object(gear1.cut(gear2))
# show_object(rack2.cut(rack1))

