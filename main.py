import cadquery as cq
from pathlib import Path

m: float = 2.0
z: int = 4
x: float = 0.0
alpha: float = 20.0
b: float = 10.0
ha_star: float = 1.0
c_star: float = 0.167
rho_f_star: float = 0.1

from gears import GearData, Gear, GearList, compute_gear_data, initialize_gears, create_racks, cut_gears
from helpers import create_video

gear_data: GearData = compute_gear_data(
    m=m,
    z=z,
    b=b,
    alpha=alpha,
    beta=0.0,
    ha_star=ha_star,
    c_star=c_star,
    rho_f_star=rho_f_star,
)

gear_list: GearList = initialize_gears([gear_data])

create_racks(gear_list)

cut_gears(gear_list, num_cut_positions=100, visualize=None)

# create_video(
#     input_dir=Path("output/img"),
#     output_path=Path("output/gear_cutting.mp4"),
#     delete_frames=True,
#     video_length=10.0
# )

# result = create_rack_cutter_sketch(
#         m=m,
#         alpha=alpha,
#         ha_star=1.0,
#         c_star=c_star,
#         rho_f_star=0.3,
#         z=z,
#     )


show_object(gear_list.gears[0].workplane)
# show(result)
