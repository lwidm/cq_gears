import cadquery as cq
from matplotlib import pyplot as plt
from pathlib import Path

import cq_gears

output_dir: Path = Path("output")

fig, ax = plt.subplots(figsize=(5, 5))
cq_gears.plotting.hypotrochoid_plot(ax=ax, phi_0=30.0, phi_hypo=-50, flank="right", show_arrows=True, show_line=True)
fig.savefig(output_dir / f"hypotroichoid.png", dpi=300)
plt.show()
plt.close(fig)

cq_gears.plotting.create_hypotrochoid_video(output_dir=output_dir, video_length=10)

