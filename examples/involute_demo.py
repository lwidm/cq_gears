import cadquery as cq
from matplotlib import pyplot as plt
from pathlib import Path

import cq_gears

output_dir: Path = Path("output")

fig, ax = plt.subplots(figsize=(5, 5))
cq_gears.plotting.involute_plot(ax=ax, phi_0=30.0, phi=-50, show_arrows=True, show_angle=True, type="line")
fig.savefig(output_dir / f"involute.png", dpi=300)
plt.show()
plt.close(fig)
cq_gears.plotting.create_involute_video(output_dir=output_dir, video_length=10)

