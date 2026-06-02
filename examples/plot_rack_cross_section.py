import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

import cq_gears
from cq_gears import plotting as cqg_plt

m_n: float = 2.0
b: float = 10.0
alpha_n: float = 20.0
delta: float = 90.0
ha_star: float = 1.0
c_star: float = 0.167
rho_f_star: float = 0.3

gear_data_1: cq_gears.RackGearData = cq_gears.make_rack_gear_data(
    m_n=m_n,
    z=5,
    b=b,
    x=0.0,
    alpha_n=alpha_n,
    ha_star=ha_star,
    c_star=c_star,
    rho_f_star=rho_f_star,
    rail_width=m_n/2
)

gear_data_2: cq_gears.RackGearData = cq_gears.make_rack_gear_data(
    m_n=m_n,
    z=5,
    b=b,
    x=0.4,
    alpha_n=alpha_n,
    ha_star=ha_star,
    c_star=c_star,
    rho_f_star=rho_f_star,
    rail_width=m_n/2
)


def main() -> None:
    fig: Figure
    ax: Axes
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect("equal")
    ax = cqg_plt.plot_rack_profile(
        ax,
        gear_data_1,
        "points",
        linewidth=1.0,
        linestyle="-.",
        color="black",
        tooth_offset=0.0,
    )
    ax = cqg_plt.plot_rack_profile(
        ax,
        gear_data_2,
        "Arc",
        tooth_offset=0.5,
        linewidth=1.0,
        linestyle="-.",
        color="red",
    )
    plt.show()


if __name__ == "__main__":
    main()
