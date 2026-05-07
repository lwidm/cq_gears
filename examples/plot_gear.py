import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

import cq_gears

m_n: float = 2.0
b: float = 10.0
alpha_n: float = 20.0
delta: float = 90.0
ha_star: float = 1.0
c_star: float = 0.167
rho_f_star: float = 0.3

gear_data_1: cq_gears.GearData = cq_gears.compute_gear_data(
    m_n=m_n,
    z=20,
    b=b,
    x=0.0,
    alpha_n=alpha_n,
    beta=0.0,
    delta=delta,
    ha_star=ha_star,
    c_star=c_star,
    rho_f_star=rho_f_star,
)

gear_data_2: cq_gears.GearData = cq_gears.compute_gear_data(
    m_n=m_n,
    z=20,
    b=b,
    x=2,
    alpha_n=alpha_n,
    beta=5.0,
    delta=delta,
    ha_star=ha_star,
    c_star=c_star,
    rho_f_star=rho_f_star,
)


def main() -> None:
    fig: Figure
    ax: Axes
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect("equal")
    ax = cq_gears.plotting.gear_plot(
        ax,
        gear_data_1,
        (0.0, 0.0),
        0.0,
        200,
        "points",
        linewidth=1.0,
        linestyle="-.",
        color="black",
    )
    ax = cq_gears.plotting.gear_plot(
        ax,
        gear_data_2,
        (gear_data_1.d/2, 0.0),
        0.0,
        200,
        "Arc",
        linewidth=1.0,
        linestyle="-.",
        color="red",
    )
    plt.show()


if __name__ == "__main__":
    main()
