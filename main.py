import cadquery as cq
from pathlib import Path

m: float = 2.0  # Module, Modul
z: int = 4  # Number of teeth, Zähnezahl
x: float = 0.0  # Profile shift, Profilverschiebung
alpha: float = 20.0  # [degree] Pressure angle, Eingriffswinkel
thickness: float = 10
c_star: float = 0.167

import cog4 as gears
from helpers import create_video

result = gears.simulate_gear_cutting(
    z=z,
    m=m,
    c_star=c_star,
    alpha=alpha,
    num_cut_positions=100,
    extrude_depth=thickness,
    visualize=None,
)

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


show_object(result)
# show(result)
