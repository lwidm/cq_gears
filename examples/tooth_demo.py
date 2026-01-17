import cadquery as cq
from matplotlib import pyplot as plt
from pathlib import Path

import cq_gears

output_dir: Path = Path("output")

fig, ax = plt.subplots(figsize=(5, 5))
cq_gears.plotting.tooth_plot(ax=ax, flank="right")
fig.savefig(output_dir / f"tooth.png", dpi=300)
plt.show()
plt.close(fig)

