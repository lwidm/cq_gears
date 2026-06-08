import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Circle, Rectangle, Arc
import subprocess
from typing import Literal
from pathlib import Path

from . import geometry
from . import core
from . import parametric_gear
from .core import (
    GearData,
    HelicalGearData,
    SpurGearData,
    RackGearData,
    make_rack_gear_data,
)

__all__ = [
    # Static plots
    "plot_involute_construction",
    "plot_undercut_construction",
    "plot_meshing_circles",
    "plot_tooth_profile",
    "plot_gear_profile",
    "plot_profile_shift_comparison",
    # Animations
    "animate_involute_construction",
    "animate_undercut_construction",
    "animate_meshing_circles",
]


def _ffmpeg_video(img_dir: Path, output_path: Path, name: str, framerate) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-framerate",
            str(framerate),
            "-i",
            str(img_dir / f"{name}_%03d.png"),
            "-vf",
            "scale=ceil(iw/2)*2:ceil(ih/2)*2",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-profile:v",
            "baseline",
            "-level",
            "3.0",
            "-pix_fmt",
            "yuv420p",
            str(output_path),
        ],
        check=True,
    )

    for f in img_dir.iterdir():
        f.unlink()
    img_dir.rmdir()


def _plot_points(ax: Axes, points_list: list[np.ndarray], *args, **kwargs) -> Axes:
    for i in np.arange(len(points_list)):
        ax.plot(points_list[i][0], points_list[i][1], *args, **kwargs)
    return ax


def _add_background_rect(
    ax: Axes,
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    color="black",
    pad: float = 0.05,
    zorder: int = -100,
) -> Axes:
    x0, x1 = xlim
    y0, y1 = ylim

    dx = x1 - x0
    dy = y1 - y0

    rect = Rectangle(
        (x0 - pad * dx, y0 - pad * dy),
        dx * (1 + 2 * pad),
        dy * (1 + 2 * pad),
        facecolor=color,
        edgecolor="none",
        zorder=zorder,
    )
    ax.add_patch(rect)
    return ax


def _plot_arrow(
    ax: Axes, x1: float, y1: float, x2: float, y2: float, color, zorder: int
) -> Axes:
    head_length: float = 0.2
    dx: float = x2 - x1
    dy: float = y2 - y1
    length: float = np.sqrt(dx**2 + dy**2)
    if length == 0:
        return ax
    scale: float = 1 - head_length / length
    dx = scale * dx
    dy = scale * dy
    ax.arrow(
        x=x1,
        y=y1,
        dx=dx,
        dy=dy,
        width=0.04,
        head_width=0.1,
        head_length=head_length,
        color=color,
        alpha=0.5,
        zorder=zorder,
    )

    return ax


def _arc_points(
    r: float,
    phi_start: float,
    phi_end: float,
    center: tuple[float, float],
    unit: Literal["degree", "radian"] = "degree",
    dir: Literal["clockwise", "counterclockwise"] = "counterclockwise",
    n: int = 200,
) -> np.ndarray:
    if unit == "degree":
        phi_start = np.radians(phi_start)
        phi_end = np.radians(phi_end)

    theta = np.linspace(
        phi_start,
        phi_end,
        n,
    )

    x: np.ndarray = center[0] + r * np.cos(theta)
    y: np.ndarray
    if dir == "clockwise":
        y = center[1] - r * np.sin(theta)
    else:
        y = center[1] + r * np.sin(theta)

    return np.vstack([x, y])


def _compute_involute_plot_data(
    r: float,
    phi_0: float,
    phi: float,
    rotate: float,
    phi_max: float | None = None,
) -> dict[str, np.ndarray]:
    phi_0_r: float = np.radians(phi_0)
    phi_r: float = np.radians(phi)
    phi_r_arr: np.ndarray = np.linspace(phi_0_r, phi_r, 500)
    points_inv: np.ndarray = geometry.involute(r, phi_r_arr)
    inv_start: np.ndarray = np.vstack([points_inv[0, 0], points_inv[1, 0]])
    inv_end: np.ndarray = np.vstack([points_inv[0, -1], points_inv[1, -1]])

    points_arc: np.ndarray = _arc_points(
        r=r,
        phi_start=0.0,
        phi_end=phi_r - np.sign(phi_r) * 2 * np.pi,
        center=(0.0, 0.0),
        unit="radian",
        dir="counterclockwise",
    )

    unrolling_string: np.ndarray = np.hstack([points_arc, inv_end])

    phi_r_max: float
    if phi_max is None:
        phi_r_max = phi_r
    else:
        phi_r_max = np.radians(phi_max)

    line_length: float = (phi_r_max - phi_0_r) * r * 1.2
    padding: float = (phi_r_max - phi_0_r) * r * 0.1

    rolling_line_contact: np.ndarray = np.vstack([r * np.cos(phi_r), r * np.sin(phi_r)])
    rolling_line_tangent: np.ndarray = np.vstack([np.sin(phi_r), -np.cos(phi_r)])
    start_line_distance: float = r * (phi_r - phi_0_r) + padding
    rolling_line_start: np.ndarray = rolling_line_contact + (
        rolling_line_tangent * start_line_distance
    )
    rolling_line_inv: np.ndarray = rolling_line_contact + (
        rolling_line_tangent * r * phi_r
    )
    rolling_line_end: np.ndarray = rolling_line_contact - (
        rolling_line_tangent * (line_length - start_line_distance)
    )

    def transform(points: np.ndarray) -> np.ndarray:
        return geometry.rotate(points, rotate)

    result: dict[str, np.ndarray] = {
        "points_inv": transform(points_inv),
        "points_arc": transform(points_arc),
        "inv_start": transform(inv_start),
        "inv_end": transform(inv_end),
        "unrolling_string": transform(unrolling_string),
        "rolling_line_contact": transform(rolling_line_contact),
        "rolling_line_tangent": transform(rolling_line_tangent),
        "rolling_line_start": transform(rolling_line_start),
        "rolling_line_inv": transform(rolling_line_inv),
        "rolling_line_end": transform(rolling_line_end),
    }

    return result


def plot_involute_construction(
    ax: Axes,
    phi_0: float,
    phi: float,
    show_arrows: bool,
    show_angle: bool,
    type: Literal["string", "line"],
    phi_max: float | None = None,
) -> Axes:
    lw: float = 3.0
    r: float = 1.0

    involute_dict: dict[str, np.ndarray] = _compute_involute_plot_data(
        r=r,
        phi_0=phi_0,
        phi=phi,
        rotate=0.0,
        phi_max=phi_max,
    )

    zorder: int = 100

    circle = Circle((0, 0), r, color="gray", alpha=1, zorder=zorder)
    zorder += 1
    ax.add_patch(circle)

    if type == "string":
        ax.plot(
            involute_dict["unrolling_string"][0, :],
            involute_dict["unrolling_string"][1, :],
            color="red",
            lw=lw,
            ls="--",
            zorder=zorder,
        )
        zorder += 1
    else:
        ax.plot(
            [
                involute_dict["rolling_line_inv"][0, 0],
                involute_dict["rolling_line_end"][0, 0],
            ],
            [
                involute_dict["rolling_line_inv"][1, 0],
                involute_dict["rolling_line_end"][1, 0],
            ],
            color="red",
            lw=lw,
            ls="--",
            zorder=zorder,
        )
        zorder += 1
        ax.plot(
            [
                involute_dict["rolling_line_inv"][0, 0],
                involute_dict["rolling_line_start"][0, 0],
            ],
            [
                involute_dict["rolling_line_inv"][1, 0],
                involute_dict["rolling_line_start"][1, 0],
            ],
            color="red",
            lw=lw,
            ls="--",
            zorder=zorder,
        )
        zorder += 1
        circle = Circle(
            (
                involute_dict["rolling_line_inv"][0, 0],
                involute_dict["rolling_line_inv"][1, 0],
            ),
            0.04,
            color="yellow",
            alpha=1,
            zorder=zorder,
        )
        zorder += 1
        ax.add_patch(circle)

    ax.plot(
        involute_dict["points_inv"][0, :],
        involute_dict["points_inv"][1, :],
        color="white",
        linewidth=lw,
        zorder=zorder,
    )
    zorder += 1
    if show_angle:
        ax.plot(
            [r, 0, involute_dict["rolling_line_contact"][0, 0]],
            [0, 0, involute_dict["rolling_line_contact"][1, 0]],
            color="white",
            linewidth=lw / 3,
            zorder=zorder,
        )
        zorder += 1
        angle = Arc(
            (0, 0),
            width=r / 2,
            height=r / 2,
            theta1=0.0,
            theta2=phi,
            color="white",
            lw=lw / 3,
            alpha=1.0,
            zorder=zorder,
        )
        zorder += 1
        ax.add_patch(angle)
        mid_angle_deg: float = phi / 2
        mid_angle_rad: float = np.radians(mid_angle_deg)
        text_radius: float = r / 2.5
        x_text: float = text_radius * np.cos(mid_angle_rad)
        y_text: float = text_radius * np.sin(mid_angle_rad)
        ax.text(
            x_text,
            y_text,
            r"$\phi$",
            color="white",
            fontsize=14,
            ha="center",
            va="center",
            zorder=zorder,
        )
        zorder += 1

    if show_arrows:
        ax = _plot_arrow(
            ax,
            x1=0.0,
            y1=0.0,
            x2=involute_dict["rolling_line_contact"][0, 0],
            y2=involute_dict["rolling_line_contact"][1, 0],
            color="yellow",
            zorder=zorder,
        )
        zorder += 1
        ax = _plot_arrow(
            ax,
            x1=involute_dict["rolling_line_contact"][0, 0],
            y1=involute_dict["rolling_line_contact"][1, 0],
            x2=involute_dict["inv_end"][0, 0],
            y2=involute_dict["inv_end"][1, 0],
            color="blue",
            zorder=zorder,
        )
        zorder += 1

    ax.set_aspect("equal")
    ax.set_xlim(-1.5 * r, 3 * r)
    ax.set_ylim(-1.5 * r, 3 * r)
    ax = _add_background_rect(ax, (-1.5 * r, 3 * r), (-1.5 * r, 3 * r))
    ax.set_position((0, 0, 1, 1))
    ax.set_axis_off()

    return ax


def animate_involute_construction(
    output_dir: Path, video_length: float, type: Literal["line", "string"]
):
    temp_dir = output_dir / "involute"
    temp_dir.mkdir(exist_ok=True)

    phi_min: float = -90
    if type == "string":
        phi_min = 0.0
    phi_max: float = 140
    step: float = 1 if phi_max > phi_min else -1
    phi_arr: np.ndarray = np.arange(phi_min, phi_max, step)

    plt.ion()
    fig, ax = plt.subplots(figsize=(5, 5))
    plt.show(block=False)

    for i, phi in enumerate(phi_arr):
        ax.clear()
        plot_involute_construction(
            ax=ax,
            phi_0=phi_min,
            phi=phi,
            show_arrows=False,
            show_angle=True,
            type=type,
            phi_max=phi_arr[-1],
        )
        fig.canvas.draw()
        fig.canvas.flush_events()
        plt.pause(0.001)  # Brief pause to update display
        fig.savefig(temp_dir / f"involute_{i:03d}.png", dpi=300)

    plt.ioff()
    plt.close(fig)

    frame_files: list[Path] = sorted(temp_dir.glob("involute_*.png"))
    total_frames: int = len(frame_files)
    if total_frames == 0:
        raise ValueError(f"No frames found in {temp_dir}")

    framerate = int(total_frames / video_length)
    output_path: Path = output_dir / "involute.mp4"

    _ffmpeg_video(temp_dir, output_path, "involute", framerate)


def _compute_undercut_plot_data(
    phi_0: float,
    phi_undercut: float,
    flank: Literal["left", "right"],
    phi_inv: float,
    phi_undercut_max: float | None = None,
) -> dict[str, float | np.ndarray | SpurGearData | dict]:
    geardata: SpurGearData = core.make_spur_gear_data(
        m_n=1.0,
        z=7,
        b=1.0,
        x=0.0,
        alpha_n=20.0,
        ha_star=1.0,
        c_star=0.167,
    )
    df: float = geardata.df
    db: float = geardata.db
    dp: float = geardata.dp
    alpha_t_r: float = geardata.alpha_t_r

    if phi_undercut_max is None:
        phi_undercut_max = phi_undercut

    phi_undercut_r: float = np.radians(phi_undercut)
    phi_0_r: float = np.radians(phi_0)
    phi_r_arr: np.ndarray = np.linspace(phi_0_r, phi_undercut_r, 500)

    phi_r_arr_inv: np.ndarray = np.linspace(0.0, np.radians(phi_inv), 500)
    points_inv: np.ndarray = geometry.involute(db / 2, phi_r_arr_inv)
    if flank == "right":
        points_inv = geometry.rotate(points_inv, alpha_t_r)
    else:
        points_inv = geometry.rotate(points_inv, -alpha_t_r)

    points_undercut: np.ndarray = geometry.undercut_curve(
        dp, df, alpha_t_r, phi_r_arr, flank
    )

    undercut_inv_dict: dict[str, np.ndarray] = _compute_involute_plot_data(
        r=dp / 2,
        phi_0=phi_0,
        phi=phi_undercut,
        rotate=0.0,
        phi_max=phi_undercut_max,
    )

    result: dict[str, float | np.ndarray | SpurGearData | dict] = {
        "df": df,
        "db": db,
        "dp": dp,
        "alpha_t_r": alpha_t_r,
        "points_inv": points_inv,
        "points_undercut": points_undercut,
        "geardata": geardata,
        "undercut_inv_dict": undercut_inv_dict,
    }

    return result


def plot_undercut_construction(
    ax: Axes,
    phi_0: float,
    phi_undercut: float,
    flank: Literal["left", "right"],
    show_arrows: bool,
    show_line: bool,
    phi_undercut_max: float | None = None,
) -> Axes:
    lw: float = 1.0

    zorder: int = 100

    phi_inv: float
    if flank == "right":
        phi_inv = 30.0
    else:
        phi_inv = -30.0

    undercut_dict: dict = _compute_undercut_plot_data(
        phi_0, phi_undercut, flank, phi_inv, phi_undercut_max
    )
    involute_dict: dict[str, np.ndarray] = undercut_dict["undercut_inv_dict"]

    dedendum_circle = Circle(
        (0, 0),
        undercut_dict["df"] / 2,
        color="gray",
        alpha=1,
        fill=False,
        zorder=zorder,
    )
    ax.add_patch(dedendum_circle)
    zorder += 1
    pitch_circle = Circle(
        (0, 0),
        undercut_dict["dp"] / 2,
        color="gray",
        alpha=1,
        fill=False,
        zorder=zorder,
    )
    ax.add_patch(pitch_circle)
    zorder += 1
    base_circle = Circle(
        (0, 0),
        undercut_dict["db"] / 2,
        color="gray",
        alpha=1,
        fill=False,
        zorder=zorder,
    )
    ax.add_patch(base_circle)
    zorder += 1

    ax.plot(
        undercut_dict["points_inv"][0, :],
        undercut_dict["points_inv"][1, :],
        color="white",
        linewidth=lw,
        zorder=zorder,
    )
    zorder += 1

    ax.plot(
        involute_dict["points_inv"][0, :],
        involute_dict["points_inv"][1, :],
        color="red",
        linewidth=lw,
        zorder=zorder,
    )
    zorder += 1

    ax.plot(
        undercut_dict["points_undercut"][0, :],
        undercut_dict["points_undercut"][1, :],
        color="red",
        linewidth=lw,
        zorder=zorder,
    )
    zorder += 1

    if show_line:
        ax.plot(
            [
                involute_dict["rolling_line_inv"][0, 0],
                involute_dict["rolling_line_start"][0, 0],
            ],
            [
                involute_dict["rolling_line_inv"][1, 0],
                involute_dict["rolling_line_start"][1, 0],
            ],
            color="red",
            lw=lw,
            ls="--",
            zorder=zorder,
        )
        zorder += 1
        ax.plot(
            [
                involute_dict["rolling_line_inv"][0, 0],
                involute_dict["rolling_line_end"][0, 0],
            ],
            [
                involute_dict["rolling_line_inv"][1, 0],
                involute_dict["rolling_line_end"][1, 0],
            ],
            color="red",
            lw=lw,
            ls="--",
            zorder=zorder,
        )
        zorder += 1
        circle = Circle(
            (
                involute_dict["rolling_line_inv"][0, 0],
                involute_dict["rolling_line_inv"][1, 0],
            ),
            0.04,
            color="yellow",
            alpha=1,
            zorder=zorder,
        )
        zorder += 1
        ax.add_patch(circle)

    if show_arrows:
        ax = _plot_arrow(
            ax,
            x1=0.0,
            y1=0.0,
            x2=involute_dict["rolling_line_contact"][0, 0],
            y2=involute_dict["rolling_line_contact"][1, 0],
            color="yellow",
            zorder=zorder,
        )
        zorder += 1
        ax = _plot_arrow(
            ax,
            x1=involute_dict["rolling_line_contact"][0, 0],
            y1=involute_dict["rolling_line_contact"][1, 0],
            x2=involute_dict["inv_end"][0, 0],
            y2=involute_dict["inv_end"][1, 0],
            color="blue",
            zorder=zorder,
        )
        zorder += 1
        ax = _plot_arrow(
            ax,
            x1=involute_dict["points_inv"][0, -1],
            y1=involute_dict["points_inv"][1, -1],
            x2=undercut_dict["points_undercut"][0, -1],
            y2=undercut_dict["points_undercut"][1, -1],
            color="orange",
            zorder=zorder,
        )
        zorder += 1

    geardata: core.GearData = undercut_dict["geardata"]
    ax.set_aspect("equal")
    xlim: tuple[float, float] = (0.0, 0.6 * geardata.da)
    ylim: tuple[float, float] = (-0.3 * geardata.da, 0.3 * geardata.da)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax = _add_background_rect(ax, xlim, ylim)
    ax.set_position((0, 0, 1, 1))
    ax.set_axis_off()

    return ax


def animate_undercut_construction(output_dir: Path, video_length: float):
    temp_dir = output_dir / "undercut"
    temp_dir.mkdir(exist_ok=True)

    phi_min: float = 30
    phi_max: float = -50
    flank: Literal["left", "right"] = "right"
    phi_arr: np.ndarray = np.linspace(phi_min, phi_max, 500)

    plt.ion()
    fig, ax = plt.subplots(figsize=(5, 5))
    plt.show(block=False)

    for i, phi in enumerate(phi_arr):
        ax.clear()
        plot_undercut_construction(
            ax=ax,
            phi_0=phi_min,
            phi_undercut=phi,
            show_arrows=True,
            show_line=True,
            phi_undercut_max=phi_arr[-1],
            flank=flank,
        )
        fig.canvas.draw()
        fig.canvas.flush_events()
        plt.pause(0.001)  # Brief pause to update display
        fig.savefig(temp_dir / f"undercut_{i:03d}.png", dpi=300)

    plt.ioff()  # Turn off interactive mode
    plt.close(fig)

    frame_files: list[Path] = sorted(temp_dir.glob("undercut_*.png"))
    total_frames: int = len(frame_files)
    if total_frames == 0:
        raise ValueError(f"No frames found in {temp_dir}")

    framerate = int(total_frames / video_length)
    output_path: Path = output_dir / "undercut.mp4"

    _ffmpeg_video(temp_dir, output_path, "undercut", framerate)


def plot_meshing_circles(
    ax: Axes,
    dp_ring: float,
    dp_pinion: float,
    phi: float,
    show_gears: bool,
    show_rack: bool,
    show_line: bool,
    show_string: bool,
    *,
    geardata_ring: GearData | None = None,
    geardata_pinion: SpurGearData | HelicalGearData | None = None,
    phi_0: float | None = None,
    phi_max: float | None = None,
) -> Axes:
    if show_line and show_string:
        raise ValueError("show_line and show_string cannot both be True")

    lw: float = 1.0
    zorder: int = 100

    # internal_gear
    ring_pts: np.ndarray = _arc_points(
        dp_ring / 2, 0, 2 * np.pi, center=(0.0, 0.0), unit="radian"
    )

    # Rotated copy with a radial tick to make rotation visible
    alpha: float = dp_pinion / dp_ring * phi
    beta: float = (1 - dp_pinion / dp_ring) * phi
    translate_x: float = np.cos(alpha) * (dp_ring - dp_pinion) / 2
    translate_y: float = np.sin(alpha) * (dp_ring - dp_pinion) / 2

    pinion_pts: np.ndarray = _arc_points(
        dp_pinion / 2, 0, 2 * np.pi, center=(0.0, 0.0), unit="radian"
    )
    pinion_pts = geometry.rotate(pinion_pts, -beta)
    pinion_pts = geometry.translate(pinion_pts, (translate_x, translate_y))

    if show_gears:
        if geardata_ring is None or geardata_pinion is None:
            raise ValueError(
                "if show_gears is true geardata_ring and geardata_pinion must be non None"
            )
        ax = plot_gear_profile(
            ax,
            geardata_pinion,
            (translate_x, translate_y),
            -beta + geardata_pinion.p / geardata_pinion.dp,
            200,
            "Arc",
            linewidth=lw,
            linestyle="-",
            color="white",
            zorder=zorder,
        )
        zorder += 1

    if show_rack:
        if geardata_ring is None or geardata_pinion is None:
            raise ValueError(
                "if show_rack is true geardata_ring and geardata_pinion must be non None"
            )
        rack_geardata: RackGearData = make_rack_gear_data(
            m_n=geardata_pinion.m_n,
            z=20,
            b=geardata_pinion.b,
            rail_width=geardata_pinion.m_n / 2,
            x=-geardata_pinion.x,
            alpha_n=geardata_pinion.alpha_n,
            ha_star=geardata_pinion.ha_star,
            c_star=geardata_pinion.c_star,
            rho_f_star=0.3,
        )
        transforms: list[
            tuple[Literal["rotate"], float]
            | tuple[Literal["translate"], tuple[float, float]]
        ] = [
            ("translate", (geardata_pinion.dp / 2, 0)),
            ("rotate", -phi),
            ("translate", (geardata_ring.dp / 2 - geardata_pinion.dp / 2, 0)),
            ("rotate", (phi*geardata_pinion.dp/geardata_ring.dp)),
        ]

        plot_rack_profile(
            ax=ax,
            rack_geardata=rack_geardata,
            arc_type="points",
            tooth_offset=0,
            transforms=transforms,
            linewidth=lw,
            linestyle="-",
            color="white",
            zorder=zorder,
        )

    ax.set_aspect("equal")
    lim = dp_ring / 2 + 1
    xlim: tuple[float, float] = (-lim, lim + dp_ring / 4)
    ylim: tuple[float, float] = (-lim, lim)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax = _add_background_rect(ax, xlim, ylim)

    # internal_gear
    ax.plot(
        ring_pts[0],
        ring_pts[1],
        linewidth=lw,
        linestyle="--",
        color="gray",
        zorder=zorder,
    )
    zorder += 1
    ax.scatter([0], [0], marker="x", color="white", zorder=zorder)
    zorder += 1

    # Rotated copy with a radial tick to make rotation visible
    ax.plot(
        pinion_pts[0],
        pinion_pts[1],
        linewidth=lw,
        linestyle="--",
        color="gray",
        zorder=zorder,
    )
    zorder += 1
    ax.scatter([translate_x], [translate_y], marker="x", color="white", zorder=zorder)
    zorder += 1

    if show_line or show_string:
        if geardata_pinion is None:
            raise ValueError(
                "if show_line or show_string is true geardata_ring and geardata_pinion must be non None"
            )
        if phi_0 is None:
            raise ValueError(
                "if show_line or show_string is true geardata_ring and phi_0 must be non None"
            )
        involute_dict = _compute_involute_plot_data(
            r=geardata_pinion.dp / 2,
            phi_0=np.degrees(phi_0),
            phi=np.degrees(phi),
            rotate=-beta,
            phi_max=np.degrees(phi_max) if phi_max is not None else None,
        )
        if show_string:
            involute_dict["unrolling_string"] = geometry.translate(
                involute_dict["unrolling_string"], (translate_x, translate_y)
            )
            ax.plot(
                involute_dict["unrolling_string"][0, :],
                involute_dict["unrolling_string"][1, :],
                color="red",
                lw=lw,
                ls="--",
                zorder=zorder,
            )
            zorder += 1
        if show_line:
            involute_dict["rolling_line_inv"] = geometry.translate(
                involute_dict["rolling_line_inv"], (translate_x, translate_y)
            )
            involute_dict["rolling_line_start"] = geometry.translate(
                involute_dict["rolling_line_start"], (translate_x, translate_y)
            )
            involute_dict["rolling_line_end"] = geometry.translate(
                involute_dict["rolling_line_end"], (translate_x, translate_y)
            )
            ax.plot(
                [
                    involute_dict["rolling_line_inv"][0, 0],
                    involute_dict["rolling_line_end"][0, 0],
                ],
                [
                    involute_dict["rolling_line_inv"][1, 0],
                    involute_dict["rolling_line_end"][1, 0],
                ],
                color="red",
                lw=lw,
                ls="--",
                zorder=zorder,
            )
            zorder += 1
            ax.plot(
                [
                    involute_dict["rolling_line_inv"][0, 0],
                    involute_dict["rolling_line_start"][0, 0],
                ],
                [
                    involute_dict["rolling_line_inv"][1, 0],
                    involute_dict["rolling_line_start"][1, 0],
                ],
                color="red",
                lw=lw,
                ls="--",
                zorder=zorder,
            )
            zorder += 1
            circle = Circle(
                (
                    involute_dict["rolling_line_inv"][0, 0],
                    involute_dict["rolling_line_inv"][1, 0],
                ),
                geardata_pinion.dp / 40,
                color="yellow",
                alpha=1,
                zorder=zorder,
            )
            ax.add_patch(circle)
            zorder += 1

    return ax


def animate_meshing_circles(
    output_dir: Path,
    video_length: float,
    show_gears: bool,
    show_rack: bool,
    show_line: bool,
    show_string: bool,
    geardata_ring: GearData | None = None,
    geardata_pinion: SpurGearData | HelicalGearData | None = None,
):
    temp_dir = output_dir / "internal_rolling_circles"
    temp_dir.mkdir(exist_ok=True)

    phi_min: float = -90.0 * np.pi / 180
    phi_max: float = 140.0 * np.pi / 180
    n_frames: int = 360
    phi_arr: np.ndarray = np.linspace(phi_min, phi_max, n_frames, endpoint=True)

    plt.ion()
    fig: Figure
    ax: Axes
    fig, ax = plt.subplots(figsize=(5, 5))
    plt.show(block=False)

    for i, phi in enumerate(phi_arr):
        ax.clear()
        if geardata_ring is not None and geardata_pinion is not None:
            ax = plot_meshing_circles(
                ax,
                geardata_ring.dp,
                geardata_pinion.dp,
                phi,
                show_gears=show_gears,
                show_rack=show_rack,
                show_line=show_line,
                show_string=show_string,
                geardata_ring=geardata_ring,
                geardata_pinion=geardata_pinion,
                phi_0=0.0,
                phi_max=phi_max,
            )
        else:
            ax = plot_meshing_circles(
                ax,
                3.0,
                2.0,
                phi,
                show_gears=False,
                show_rack=show_rack,
                show_line=show_line,
                show_string=show_string,
                geardata_ring=None,
                geardata_pinion=None,
                phi_0=0.0,
                phi_max=phi_max,
            )
        fig.canvas.draw()
        fig.canvas.flush_events()
        plt.pause(0.001)  # Brief pause to update display
        fig.savefig(temp_dir / f"rolling_{i:03d}.png", dpi=300)

    plt.ioff()
    plt.close(fig)

    frame_files: list[Path] = sorted(temp_dir.glob("rolling_*.png"))
    total_frames: int = len(frame_files)
    if total_frames == 0:
        raise ValueError(f"No frames found in {temp_dir}")

    framerate = int(total_frames / video_length)
    output_path: Path = output_dir / "rolling_circle.mp4"

    _ffmpeg_video(temp_dir, output_path, "rolling", framerate)


def plot_tooth_profile(
    ax: Axes,
    geardata: GearData,
) -> Axes:
    lw: float = 1.0

    zorder: int = 100

    tooth_dict: dict[str, bool | np.ndarray] = parametric_gear.compute_tooth_points(
        geardata, 500
    )

    dedendum_circle = Circle(
        (0, 0),
        geardata.df / 2,
        color="gray",
        alpha=1,
        fill=False,
        zorder=zorder,
    )
    ax.add_patch(dedendum_circle)
    zorder += 1
    pitch_circle = Circle(
        (0, 0),
        geardata.dp / 2,
        color="gray",
        alpha=1,
        fill=False,
        zorder=zorder,
    )
    ax.add_patch(pitch_circle)
    zorder += 1
    base_circle = Circle(
        (0, 0),
        geardata.db / 2,
        color="gray",
        alpha=1,
        fill=False,
        zorder=zorder,
    )
    ax.add_patch(base_circle)
    zorder += 1
    base_circle = Circle(
        (0, 0),
        geardata.da / 2,
        color="gray",
        alpha=1,
        fill=False,
        zorder=zorder,
    )
    ax.add_patch(base_circle)
    zorder += 1

    ax.plot(
        tooth_dict["points_inv_right"][0, :],  # type: ignore
        tooth_dict["points_inv_right"][1, :],  # type: ignore
        color="white",
        linewidth=lw,
        zorder=zorder,
    )
    zorder += 1
    ax.plot(
        tooth_dict["points_inv_left"][0, :],  # type: ignore
        tooth_dict["points_inv_left"][1, :],  # type: ignore
        color="white",
        linewidth=lw,
        zorder=zorder,
    )
    zorder += 1

    if tooth_dict["has_undercut"]:
        ax.plot(
            tooth_dict["points_undercut_right"][0, :],  # type: ignore
            tooth_dict["points_undercut_right"][1, :],  # type: ignore
            color="white",
            linewidth=lw,
            zorder=zorder,
        )
        zorder += 1
        ax.plot(
            tooth_dict["points_undercut_left"][0, :],  # type: ignore
            tooth_dict["points_undercut_left"][1, :],  # type: ignore
            color="white",
            linewidth=lw,
            zorder=zorder,
        )
        zorder += 1

    ax.set_aspect("equal")
    xlim: tuple[float, float] = (0.0, 0.6 * geardata.da)
    ylim: tuple[float, float] = (-0.3 * geardata.da, 0.3 * geardata.da)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax = _add_background_rect(ax, xlim, ylim)
    ax.set_position((0, 0, 1, 1))
    ax.set_axis_off()

    return ax


def plot_rack_profile(
    ax: Axes,
    rack_geardata: RackGearData,
    arc_type: Literal["Arc", "points"],
    tooth_offset: float,
    transforms: (
        list[
            tuple[Literal["rotate"], float]
            | tuple[Literal["translate"], tuple[float, float]]
        ]
        | None
    ),
    **kwargs,
) -> Axes:
    z: int = rack_geardata.z
    ha: float = rack_geardata.ha
    hf: float = rack_geardata.hf
    p: float = rack_geardata.p
    rail_w: float = rack_geardata.rail_width
    rho_f: float = rack_geardata.rho_f
    alpha: float = rack_geardata.alpha_t_r

    arc_patches: list[tuple[np.ndarray, float, float]] = []
    line_segments: list[np.ndarray] = []
    plot_array: np.ndarray

    if z < 2:
        raise ValueError(
            f"needs at least 2 teeth to plot rack profile. Instead got {z} teeth"
        )

    y_shift: float = -tooth_offset * p

    tip_w: float = p / 2 - 2 * np.tan(alpha) * ha
    base_w: float = p / 2 + 2 * np.tan(alpha) * hf

    beta: float = (np.pi / 2 + alpha) / 2
    gamma: float = np.pi / 2 - alpha
    d: float = rho_f / np.tan(beta)
    e: float = d * np.sin(alpha)

    a_x: float = hf
    a_y: float = d + base_w / 2
    b_x: float = -(d * np.cos(alpha)) + hf
    b_y: float = -(d * np.sin(alpha)) + base_w / 2
    c_x: float = hf - rho_f
    c_y: float = d + base_w / 2

    arc_enter_t1: float = np.degrees(0)
    arc_enter_t2: float = np.degrees(gamma)
    arc_exit_t1: float = np.degrees(-gamma)
    arc_exit_t2: float = np.degrees(0)

    points_list: list[np.ndarray] = []

    # --- Helpers ---

    def add_arc_patch(y_center: float, t1: float, t2: float) -> None:
        center: np.ndarray = np.array([[c_x], [c_y + y_center + y_shift]])
        arc_patches.append((center, t1, t2))

    def fillet_points(
        angle_start: float, angle_end: float, y_center: float
    ) -> np.ndarray:
        return _arc_points(
            rho_f,
            angle_start,
            angle_end,
            center=(c_x, c_y + y_center),
            dir="counterclockwise",
            unit="radian",
        )

    def make_tip(y_offset: float) -> np.ndarray:
        return np.asarray(
            [
                [-ha, -ha],
                [-tip_w / 2, tip_w / 2],
            ]
        ) + np.asarray([[0], [y_offset]])

    def append_enter_fillet(
        tooth_number: int, points_list: list[np.ndarray], ax: Axes
    ) -> tuple[Axes, list[np.ndarray]]:
        fillet_center_offset: float = p * tooth_number - base_w - 2 * d
        fillet_tooth_offset: float = p * tooth_number - base_w + 2 * e
        if arc_type == "points":
            points_list.append(fillet_points(0, gamma, fillet_center_offset))
        else:
            points_list.append(np.asarray([[a_x], [a_y + fillet_center_offset]]))
            segment = np.hstack(points_list)
            segment[1, :] += y_shift
            line_segments.append(segment)
            points_list = []
            add_arc_patch(fillet_center_offset, arc_enter_t1, arc_enter_t2)
            points_list.append(np.asarray([[b_x], [b_y + fillet_tooth_offset]]))
        return ax, points_list

    def append_exit_fillet(
        tooth_number: float, points_list: list[np.ndarray], ax: Axes
    ) -> tuple[Axes, list[np.ndarray]]:
        fillet_center_offset: float = p * tooth_number
        fillet_tooth_offset: float = p * tooth_number
        if arc_type == "points":
            points_list.append(fillet_points(-gamma, 0, fillet_center_offset))
        else:
            points_list.append(np.asarray([[b_x], [b_y + fillet_tooth_offset]]))
            segment = np.hstack(points_list)
            segment[1, :] += y_shift
            line_segments.append(segment)
            points_list = []
            add_arc_patch(fillet_center_offset, arc_exit_t1, arc_exit_t2)
            points_list.append(np.asarray([[a_x], [a_y + fillet_center_offset]]))
        return ax, points_list

    # --- Profile construction ---

    first_tooth: np.ndarray = np.asarray(
        [
            [hf + rail_w, hf, -ha, -ha],
            [-base_w / 2, -base_w / 2, -tip_w / 2, tip_w / 2],
        ]
    )

    points_list.append(first_tooth)
    ax, points_list = append_exit_fillet(0, points_list, ax)

    for i in range(1, z - 1):
        ax, points_list = append_enter_fillet(i, points_list, ax)
        points_list.append(make_tip(p * i))
        ax, points_list = append_exit_fillet(i, points_list, ax)

    ax, points_list = append_enter_fillet(z - 1, points_list, ax)

    last_tooth: np.ndarray = np.asarray(
        [
            [-ha, -ha, hf, hf + rail_w],
            [-tip_w / 2, tip_w / 2, base_w / 2, base_w / 2],
        ]
    ) + np.asarray([[0], [p * (z - 1)]])

    points_list.append(last_tooth)
    points_list.append(
        np.asarray(
            [
                [hf + rail_w, hf + rail_w],
                [base_w / 2 + p * (z - 1), -base_w / 2],
            ]
        )
    )

    plot_array = np.hstack(points_list)
    plot_array[1, :] += y_shift

    # --- Apply transforms and plot ---

    if arc_type == "points":
        if transforms:
            for transform_type, value in transforms:
                match transform_type:
                    case "rotate":
                        assert isinstance(
                            value, float
                        ), f'rotate needs a single float: ("rotate", angle)'
                        plot_array = geometry.rotate(plot_array, value)
                    case "translate":
                        assert isinstance(
                            value, tuple
                        ), f'translate needs a float tuple: ("translate", (dx, dy))'
                        plot_array = geometry.translate(plot_array, value)
        ax = _plot_points(ax, [plot_array], **kwargs)

    else:  # arc_type == "Arc"
        # flush the final segment
        if points_list:
            segment = np.hstack(points_list)
            segment[1, :] += y_shift
            line_segments.append(segment)

        if transforms:
            for transform_type, value in transforms:
                match transform_type:
                    case "rotate":
                        assert isinstance(
                            value, float
                        ), f'rotate needs a single float: ("rotate", angle)'
                        line_segments = geometry.rotate_list(line_segments, value)
                    case "translate":
                        assert isinstance(
                            value, tuple
                        ), f'translate needs a float tuple: ("translate", (dx, dy))'
                        line_segments = geometry.translate_list(line_segments, value)

        ax = _plot_points(ax, line_segments, **kwargs)

        for center, t1, t2 in arc_patches:
            if transforms:
                for transform_type, value in transforms:
                    match transform_type:
                        case "rotate":
                            assert isinstance(
                                value, float
                            ), f'rotate needs a single float: ("rotate", angle)'
                            center = geometry.rotate(center, value)
                            t1 += np.degrees(value)
                            t2 += np.degrees(value)
                        case "translate":
                            assert isinstance(
                                value, tuple
                            ), f'translate needs a float tuple: ("translate", (dx, dy))'
                            center = geometry.translate(center, value)
            ax.add_patch(
                Arc(
                    (center[0, 0], center[1, 0]),
                    2 * rho_f,
                    2 * rho_f,
                    theta1=t1,
                    theta2=t2,
                    **kwargs,
                )
            )

    return ax


def plot_gear_profile(
    ax: Axes,
    geardata: SpurGearData | HelicalGearData,
    center: tuple[float, float],
    rotation: float,
    n_points: int,
    arc_types: Literal["Arc", "points"],
    **kwargs,
) -> Axes:
    center_arr: np.ndarray = np.array(center)
    neg_center: tuple[float, float] = (-center[0], -center[1])
    tooth_pitch: float = 2 * np.pi / geardata.z

    tooth_dict: dict = parametric_gear.compute_tooth_points(geardata, n_points)
    inv_right: np.ndarray = geometry.translate(
        geometry.rotate(tooth_dict["points_inv_right"], rotation), center
    )
    inv_left: np.ndarray = geometry.translate(
        geometry.rotate(tooth_dict["points_inv_left"], rotation), center
    )
    inv_intersect: bool = tooth_dict["involutes_intersect"]
    has_undercut: bool = tooth_dict["has_undercut"]

    undercut_right: np.ndarray | None = None
    undercut_left: np.ndarray | None = None
    if has_undercut:
        undercut_right = geometry.translate(
            geometry.rotate(tooth_dict["points_undercut_right"], rotation), center
        )
        undercut_left = geometry.translate(
            geometry.rotate(tooth_dict["points_undercut_left"], rotation), center
        )

    base_start: np.ndarray
    base_end_local: np.ndarray
    if undercut_left is not None:
        base_start = undercut_left[:, 0]
    else:
        base_start = inv_left[:, 0]
    if undercut_right is not None:
        base_end_local = undercut_right[:, 0]
    else:
        base_end_local = inv_right[:, 0]
    next_base_end: np.ndarray = geometry.translate(
        geometry.rotate(
            geometry.translate(base_end_local[:, None], neg_center), tooth_pitch
        ),
        center,
    )[:, 0]

    _, radius_base, start_angle_base, sweep_angle_base = geometry.arc_from_endpoints(
        center=center_arr,
        start=base_start,
        end=next_base_end,
        ccw=True,
    )

    radius_tip: float = 0.0
    start_angle_tip: float = 0.0
    sweep_angle_tip: float = 0.0
    if not inv_intersect:
        _, radius_tip, start_angle_tip, sweep_angle_tip = geometry.arc_from_endpoints(
            center=center_arr,
            start=inv_right[:, -1],
            end=inv_left[:, -1],
            ccw=True,
        )

    points_list: list[np.ndarray] = []
    if undercut_right is not None:
        points_list.append(undercut_right)
    points_list.append(inv_right)
    if arc_types == "points" and not inv_intersect:
        points_list.append(
            _arc_points(
                radius_tip,
                start_angle_tip,
                start_angle_tip + sweep_angle_tip,
                center=center,
                unit="degree",
            )
        )
    points_list.append(inv_left[:, ::-1])
    if undercut_left is not None:
        points_list.append(undercut_left[:, ::-1])
    if arc_types == "points":
        points_list.append(
            _arc_points(
                radius_base,
                start_angle_base,
                start_angle_base + sweep_angle_base,
                center=center,
                unit="degree",
            )
        )

    points_list = geometry.polar_pattern_list(
        points_list,
        center,
        2 * np.pi,
        geardata.z,
        endpoint=False,
        direction="counterclockwise",
    )

    if arc_types == "points":
        ax = _plot_points(ax, [np.hstack(points_list)], **kwargs)
    else:
        ax = _plot_points(ax, points_list, **kwargs)
        for i in range(geardata.z):
            tooth_offset_deg: float = np.degrees(tooth_pitch) * i
            ax.add_patch(
                Arc(
                    center,
                    radius_base * 2,
                    radius_base * 2,
                    theta1=start_angle_base + tooth_offset_deg,
                    theta2=start_angle_base + sweep_angle_base + tooth_offset_deg,
                    fill=False,
                    **kwargs,
                )
            )
            if not inv_intersect:
                ax.add_patch(
                    Arc(
                        center,
                        radius_tip * 2,
                        radius_tip * 2,
                        theta1=start_angle_tip + tooth_offset_deg,
                        theta2=start_angle_tip + sweep_angle_tip + tooth_offset_deg,
                        fill=False,
                        **kwargs,
                    )
                )

    return ax


def plot_profile_shift_comparison(
    ax: Axes,
    x_values: list[float],
    m: float = 1.0,
    z: int = 8,
) -> Axes:
    lw: float = 1.0
    zorder: int = 100

    n_values: int = len(x_values)
    geardatas: list[SpurGearData] = [
        core.make_spur_gear_data(
            m_n=m,
            z=z,
            b=1.0,
            x=x_val,
            alpha_n=20.0,
            ha_star=1.0,
            c_star=0.25,
        )
        for x_val in x_values
    ]

    tooth_dicts: list[dict[str, bool | np.ndarray]] = [
        parametric_gear.compute_tooth_points(gd, 500) for gd in geardatas
    ]

    x_max: float = max(abs(xv) for xv in x_values) if x_values else 1.0
    colors: list[str] = []
    for x_val in x_values:
        if np.isclose(x_val, 0, rtol=1e-9):
            colors.append("#ffffff")
        else:
            t: float = abs(x_val) / x_max
            if x_val > 0:
                r: int = int(255 * (1 - t))
                g: int = int(255 * (1 - t))
                b: int = 255
            elif x_val < 0:
                r = 255
                g = int(255 * (1 - t))
                b = int(255 * (1 - t))
            else:
                r, g, b = 255, 255, 255
            colors.append(f"#{r:02x}{g:02x}{b:02x}")

    da_max: float = max(gd.da for gd in geardatas)

    zorder_circles: int = zorder + 6 * n_values

    for i, (gd, td) in enumerate(zip(geardatas, tooth_dicts)):
        color: str = colors[i]

        # right involute
        ax.plot(
            td["points_inv_right"][0, :],  # type: ignore
            td["points_inv_right"][1, :],  # type: ignore
            color=color,
            linewidth=lw,
            zorder=zorder,
        )
        zorder += 1

        # left involute
        ax.plot(
            td["points_inv_left"][0, :],  # type: ignore
            td["points_inv_left"][1, :],  # type: ignore
            color=color,
            linewidth=lw,
            zorder=zorder,
        )
        zorder += 1

        if td["has_undercut"]:
            # right undercut
            ax.plot(
                td["points_undercut_right"][0, :],  # type: ignore
                td["points_undercut_right"][1, :],  # type: ignore
                color=color,
                linewidth=lw,
                zorder=zorder,
            )
            zorder += 1

            # left undercut
            ax.plot(
                td["points_undercut_left"][0, :],  # type: ignore
                td["points_undercut_left"][1, :],  # type: ignore
                color=color,
                linewidth=lw,
                zorder=zorder,
            )
            zorder += 1

        # addendum arc connecting involute tips
        angle_right: float = np.degrees(
            np.arctan2(td["points_inv_right"][1, -1], td["points_inv_right"][0, -1])  # type: ignore
        )
        angle_left: float = np.degrees(
            np.arctan2(td["points_inv_left"][1, -1], td["points_inv_left"][0, -1])  # type: ignore
        )
        if not np.isclose(angle_left, angle_right, rtol=1e-3):
            ax.add_patch(
                Arc(
                    (0, 0),
                    gd.da,
                    gd.da,
                    angle=0,
                    theta1=angle_right,
                    theta2=angle_left,
                    color=color,
                    linewidth=lw,
                    zorder=zorder,
                )
            )
            zorder += 1

        # dedendum circle
        ax.add_patch(
            Circle(
                (0, 0),
                gd.df / 2,
                color="gray",
                alpha=0.6,
                fill=False,
                linewidth=lw,
                linestyle="dotted",
                zorder=zorder_circles,
            )
        )
        zorder_circles += 1

        # addendum circle
        ax.add_patch(
            Circle(
                (0, 0),
                gd.da / 2,
                color="gray",
                alpha=0.6,
                fill=False,
                linewidth=lw,
                linestyle="dotted",
                zorder=zorder_circles,
            )
        )
        zorder_circles += 1

    ax.set_aspect("equal")
    xlim: tuple[float, float] = (0.0, 0.6 * da_max)
    ylim: tuple[float, float] = (-0.3 * da_max, 0.3 * da_max)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax = _add_background_rect(ax, xlim, ylim)
    ax.set_position((0, 0, 1, 1))
    ax.set_axis_off()

    return ax
