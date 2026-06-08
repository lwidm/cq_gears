import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from typing import Literal, TypeAlias
import numpy as np

import cq_gears
from cq_gears import plotting as cqg_plt

Transform: TypeAlias = list[
    tuple[Literal["rotate"], float] | tuple[Literal["translate"], tuple[float, float]]
]

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
    rail_width=m_n / 2,
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
    rail_width=m_n / 2,
)

gear_data_3: cq_gears.RackGearData = cq_gears.make_rack_gear_data(
    m_n=m_n,
    z=5,
    b=b,
    x=0.0,
    alpha_n=alpha_n,
    ha_star=ha_star,
    c_star=c_star,
    rho_f_star=rho_f_star,
    rail_width=m_n / 2,
)


def main() -> None:
    fig: Figure
    ax: Axes
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect("equal")
    # ax = cqg_plt.plot_rack_profile(
    #     ax,
    #     gear_data_1,
    #     "points",
    #     tooth_offset=0.0,
    #     transforms=None,
    #     linewidth=1.0,
    #     linestyle="-.",
    #     color="black",
    # )
    # ax = cqg_plt.plot_rack_profile(
    #     ax,
    #     gear_data_2,
    #     "Arc",
    #     transforms=None,
    #     tooth_offset=0.5,
    #     linewidth=1.0,
    #     linestyle="-.",
    #     color="red",
    # )

    transforms_r: Transform = [("rotate", np.radians(20))]
    transforms_rt: Transform = [("rotate", np.radians(20)), ("translate", (10.0, -3.0))]
    transforms_rtr: Transform = [
        ("rotate", np.radians(20)),
        ("translate", (10.0, -3.0)),
        ("rotate", np.radians(-40)),
    ]

    ax = cqg_plt.plot_rack_profile(
        ax,
        gear_data_3,
        "Arc",
        tooth_offset=0.0,
        transforms=None,
        linewidth=1.0,
        linestyle=":",
        color="blue",
    )
    ax = cqg_plt.plot_rack_profile(
        ax,
        gear_data_3,
        "Arc",
        tooth_offset=0.0,
        transforms=transforms_r,
        linewidth=1.0,
        linestyle="-.",
        color="blue",
    )
    ax = cqg_plt.plot_rack_profile(
        ax,
        gear_data_3,
        "Arc",
        tooth_offset=0.0,
        transforms=transforms_rt,
        linewidth=1.0,
        linestyle="--",
        color="blue",
    )
    ax = cqg_plt.plot_rack_profile(
        ax,
        gear_data_3,
        "points",
        tooth_offset=0.0,
        transforms=transforms_rtr,
        linewidth=1.0,
        linestyle="-",
        color="blue",
    )
    plt.show()


if __name__ == "__main__":
    main()
