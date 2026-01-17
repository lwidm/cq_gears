import cadquery as cq
from matplotlib import pyplot as plt
from pathlib import Path

from cq_gears import plotting
from cq_gears import core
from cq_gears.core import GearData

output_dir: Path = Path("output")

geardata: GearData = core.compute_gear_data(
        m=1.0,
        z=20,
        b=1.0,
        x=0.0,
        alpha_t=20.0,
        beta=0.0,
        delta=90.0,
        ha_star=1.0,
        c_star=0.167,
        rho_f_star=0.3,
    )

fig, ax = plt.subplots(figsize=(5, 5))
plotting.tooth_plot(ax=ax, geardata=geardata, flank="right")
plotting.tooth_plot(ax=ax, geardata=geardata, flank="left")
fig.savefig(output_dir / f"tooth.png", dpi=300)
plt.show()
plt.close(fig)

