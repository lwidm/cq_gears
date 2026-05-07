import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from pathlib import Path

import cq_gears

m_n: float = 2.0
b: float = 10.0
alpha_n: float = 20.0
delta: float = 90.0
ha_star: float = 1.0
c_star: float = 0.167
rho_f_star: float = 0.3
x: float = 0.0

geardata_ring: cq_gears.GearData = cq_gears.compute_gear_data(
    m_n=m_n,
    z=20,
    b=b,
    x=x,
    alpha_n=alpha_n,
    beta=0.0,
    delta=delta,
    ha_star=ha_star,
    c_star=c_star,
    rho_f_star=rho_f_star,
)

geardata_pinion: cq_gears.GearData = cq_gears.compute_gear_data(
    m_n=m_n,
    z=10,
    b=b,
    x=x,
    alpha_n=alpha_n,
    beta=5.0,
    delta=delta,
    ha_star=ha_star,
    c_star=c_star,
    rho_f_star=rho_f_star,
)


def main() -> None:
    output_dir: Path = Path("output")
    show_gears: bool = True

    fig: Figure
    ax: Axes
    fig, ax = plt.subplots(figsize=(5, 5))
    cq_gears.plotting.plot_rolling_circle(
        ax,
        geardata_ring.d,
        geardata_pinion.d,
        20.0 / 180 * 2 * np.pi,
        show_gears=show_gears,
        geardata_ring=geardata_ring,
        geardata_pinion=geardata_pinion,
    )
    fig.savefig(output_dir / f"rolling_circle.png", dpi=300)
    plt.show()
    plt.close(fig)
    cq_gears.plotting.create_rolling_circle_video(
        output_dir=output_dir,
        video_length=10,
        show_gears=show_gears,
        geardata_ring=geardata_ring,
        geardata_pinion=geardata_pinion,
    )


if __name__ == "__main__":
    main()
