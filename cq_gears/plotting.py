import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.patches import Circle, Rectangle, Arc
import subprocess
from typing import Literal
from pathlib import Path

from . import math
from . import core
from .core import GearData


def ffmpeg_video(img_dir: Path, output_path: Path, name: str, framerate) -> None:
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


def add_background_rect(
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
    dx: float = scale * dx
    dy: float = scale * dy
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
    unit: Literal["degree", "radian"] = "degree",
    dir: Literal["clockwise", "counterclockwise"] = "counterclockwise",
    n: int = 200,
) -> np.ndarray:
    if unit == "degree":
        phi_start = np.radians(phi_start)
        phi_end = np.radians(phi_end)

    # if phi_end < phi_start:
    #     phi_end += 2 * np.pi

    theta = np.linspace(
        phi_start,
        phi_end,
        n,
    )

    x: np.ndarray = r * np.cos(theta)
    y: np.ndarray
    if dir == "clockwise":
        y = -r * np.sin(theta)
    else:
        y = r * np.sin(theta)

    return np.vstack([x, y])


def involute_plot_compute(
    r: float,
    phi_0: float,
    phi: float,
    rotate: float,
    phi_max: float | None = None,
) -> dict[str, np.ndarray]:
    phi_0_r: float = np.radians(phi_0)
    phi_r: float = np.radians(phi)
    phi_r_arr: np.ndarray = np.linspace(phi_0_r, phi_r, 500)
    points_inv: np.ndarray = math.involute(r, phi_r_arr)
    inv_start: np.ndarray = np.vstack([points_inv[0, 0], points_inv[1, 0]])
    inv_end: np.ndarray = np.vstack([points_inv[0, -1], points_inv[1, -1]])

    points_arc: np.ndarray = _arc_points(
        r=r,
        phi_start=0.0,
        phi_end=phi_r - np.sign(phi_r) * 2 * np.pi,
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
        return math.rotate(points, rotate)

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


def involute_plot(
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

    involute_dict: dict[str, np.ndarray] = involute_plot_compute(
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
    ax = add_background_rect(ax, (-1.5 * r, 3 * r), (-1.5 * r, 3 * r))
    ax.set_position((0, 0, 1, 1))
    ax.set_axis_off()

    return ax


def create_involute_video(
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
        involute_plot(
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
    output_path = output_dir / "involute.mp4"

    ffmpeg_video(temp_dir, output_path, "involute", framerate)


def undercut_plot_compute(
    phi_0: float,
    phi_undercut: float,
    flank: Literal["left", "right"],
    phi_inv: float,
    phi_undercut_max: float | None = None,
) -> dict[str, float | np.ndarray | GearData | dict]:
    geardata: GearData = core.compute_gear_data(
        m=1.0,
        z=7,
        b=1.0,
        x=0.0,
        alpha_t=20.0,
        beta=0.0,
        delta=90.0,
        ha_star=1.0,
        c_star=0.167,
        rho_f_star=0.3,
    )
    df: float = geardata.df
    db: float = geardata.db
    dp: float = geardata.d
    alpha_t_r: float = geardata.alpha_t_r

    if phi_undercut_max is None:
        phi_undercut_max = phi_undercut

    phi_undercut_r: float = np.radians(phi_undercut)
    phi_0_r: float = np.radians(phi_0)
    phi_r_arr: np.ndarray = np.linspace(phi_0_r, phi_undercut_r, 500)

    phi_r_arr_inv: np.ndarray = np.linspace(0.0, np.radians(phi_inv), 500)
    points_inv: np.ndarray = math.involute(db / 2, phi_r_arr_inv)
    if flank == "right":
        points_inv = math.rotate(points_inv, alpha_t_r)
    else:
        points_inv = math.rotate(points_inv, -alpha_t_r)

    points_undercut: np.ndarray = math.undercut_curve(
        dp, df, alpha_t_r, phi_r_arr, flank
    )

    undercut_inv_dict: dict[str, np.ndarray] = involute_plot_compute(
        r=dp / 2,
        phi_0=phi_0,
        phi=phi_undercut,
        rotate=0.0,
        phi_max=phi_undercut_max,
    )

    result: dict[str, float | np.ndarray | GearData | dict] = {
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


def undercut_plot(
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

    undercut_dict: dict = undercut_plot_compute(
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
    ax = add_background_rect(ax, xlim, ylim)
    ax.set_position((0, 0, 1, 1))
    ax.set_axis_off()

    return ax


def create_undercut_video(output_dir: Path, video_length: float):
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
        undercut_plot(
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
    output_path = output_dir / "undercut.mp4"

    ffmpeg_video(temp_dir, output_path, "undercut", framerate)


def tooth_plot_compute(
    geardata: GearData,
) -> dict[str, float | np.ndarray | GearData]:
    m: float = geardata.m
    x: float = geardata.x
    df: float = geardata.df
    db: float = geardata.db
    dp: float = geardata.d
    da: float = geardata.da
    alpha_n_r: float = geardata.alpha_n_r
    alpha_t_r: float = geardata.alpha_t_r

    n_points: int = 500

    phi_r_addendum: float = math.involute_phi_d(da, db, "right")
    phi_r_addendum_intersection: float = math.involute_self_intersection(
        phi_r_addendum, m, x, dp, db, alpha_n_r
    )

    phi_inv_start: float = math.involute_phi_d(dp, db, "right")
    phi_undercut_end: float = math.undercut_phi_d(dp, dp, df, alpha_t_r, "right")
    phi_inv_start, phi_undercut_end = math.undercut_involute_intersection(
        phi_inv_start, phi_undercut_end, df, dp, db, alpha_t_r, "right", 200
    )

    phi_r_end: float
    if phi_r_addendum > phi_r_addendum_intersection:
        phi_r_end = phi_r_addendum_intersection
    else:
        phi_r_end = phi_r_addendum

    points_inv_right: np.ndarray = math.involute_tooth(
        m, x, dp, db, alpha_n_r, phi_inv_start, phi_r_end, n_points, "right"
    )
    points_inv_left: np.ndarray = math.involute_tooth(
        m, x, dp, db, alpha_n_r, -phi_inv_start, -phi_r_end, n_points, "left"
    )
    points_undercut_right: np.ndarray = math.undercut_tooth(
        m, x, dp, db, df, alpha_n_r, alpha_t_r, phi_undercut_end, n_points, "right"
    )
    points_undercut_left: np.ndarray = math.undercut_tooth(
        m, x, dp, db, df, alpha_n_r, alpha_t_r, -phi_undercut_end, n_points, "left"
    )

    result: dict[str, float | np.ndarray | GearData] = {
        "m": m,
        "df": df,
        "db": db,
        "dp": dp,
        "da": da,
        "geardata": geardata,
        "points_inv_right": points_inv_right,
        "points_inv_left": points_inv_left,
        "points_undercut_right": points_undercut_right,
        "points_undercut_left": points_undercut_left,
    }

    return result


def tooth_plot(
    ax: Axes,
    geardata: GearData,
) -> Axes:
    lw: float = 1.0

    zorder: int = 100

    tooth_dict: dict = tooth_plot_compute(geardata)

    dedendum_circle = Circle(
        (0, 0),
        tooth_dict["df"] / 2,
        color="gray",
        alpha=1,
        fill=False,
        zorder=zorder,
    )
    ax.add_patch(dedendum_circle)
    zorder += 1
    pitch_circle = Circle(
        (0, 0),
        tooth_dict["dp"] / 2,
        color="gray",
        alpha=1,
        fill=False,
        zorder=zorder,
    )
    ax.add_patch(pitch_circle)
    zorder += 1
    base_circle = Circle(
        (0, 0),
        tooth_dict["db"] / 2,
        color="gray",
        alpha=1,
        fill=False,
        zorder=zorder,
    )
    ax.add_patch(base_circle)
    zorder += 1
    base_circle = Circle(
        (0, 0),
        tooth_dict["da"] / 2,
        color="gray",
        alpha=1,
        fill=False,
        zorder=zorder,
    )
    ax.add_patch(base_circle)
    zorder += 1

    ax.plot(
        tooth_dict["points_inv_right"][0, :],
        tooth_dict["points_inv_right"][1, :],
        color="white",
        linewidth=lw,
        zorder=zorder,
    )
    zorder += 1
    ax.plot(
        tooth_dict["points_inv_left"][0, :],
        tooth_dict["points_inv_left"][1, :],
        color="white",
        linewidth=lw,
        zorder=zorder,
    )
    zorder += 1

    ax.plot(
        tooth_dict["points_undercut_right"][0, :],
        tooth_dict["points_undercut_right"][1, :],
        color="white",
        linewidth=lw,
        zorder=zorder,
    )
    zorder += 1
    ax.plot(
        tooth_dict["points_undercut_left"][0, :],
        tooth_dict["points_undercut_left"][1, :],
        color="white",
        linewidth=lw,
        zorder=zorder,
    )
    zorder += 1

    ax.set_aspect("equal")
    xlim: tuple[float, float] = (0.0, 0.6 * tooth_dict["da"])
    ylim: tuple[float, float] = (-0.3 * tooth_dict["da"], 0.3 * tooth_dict["da"])
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax = add_background_rect(ax, xlim, ylim)
    ax.set_position((0, 0, 1, 1))
    ax.set_axis_off()

    return ax


def profile_shift_plot(
    ax: Axes,
    x_values: list[float],
    m: float = 1.0,
    z: int = 8,
) -> Axes:
    lw: float = 1.0
    zorder: int = 100

    n_values: int = len(x_values)
    geardatas: list[GearData] = [
        core.compute_gear_data(
            m=m,
            z=z,
            b=1.0,
            x=x_val,
            alpha_t=20.0,
            beta=0.0,
            delta=90.0,
            ha_star=1.0,
            c_star=0.25,
            rho_f_star=0.3,
        )
        for x_val in x_values
    ]

    tooth_dicts: list[dict] = [tooth_plot_compute(gd) for gd in geardatas]

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

    da_max: float = max(td["da"] for td in tooth_dicts)

    zorder_circles: int = zorder + 6 * n_values

    for i, td in enumerate(tooth_dicts):
        color: str = colors[i]

        # right involute
        ax.plot(
            td["points_inv_right"][0, :],
            td["points_inv_right"][1, :],
            color=color,
            linewidth=lw,
            zorder=zorder,
        )
        zorder += 1

        # left involute
        ax.plot(
            td["points_inv_left"][0, :],
            td["points_inv_left"][1, :],
            color=color,
            linewidth=lw,
            zorder=zorder,
        )
        zorder += 1

        # right undercut
        ax.plot(
            td["points_undercut_right"][0, :],
            td["points_undercut_right"][1, :],
            color=color,
            linewidth=lw,
            zorder=zorder,
        )
        zorder += 1

        # left undercut
        ax.plot(
            td["points_undercut_left"][0, :],
            td["points_undercut_left"][1, :],
            color=color,
            linewidth=lw,
            zorder=zorder,
        )
        zorder += 1

        # addendum arc connecting involute tips
        angle_right: float = np.degrees(
            np.arctan2(
                td["points_inv_right"][1, -1], td["points_inv_right"][0, -1]
            )
        )
        angle_left: float = np.degrees(
            np.arctan2(
                td["points_inv_left"][1, -1], td["points_inv_left"][0, -1]
            )
        )
        if not np.isclose(angle_left, angle_right, rtol=1e-3):
            ax.add_patch(
                Arc(
                    (0, 0),
                    td["da"],
                    td["da"],
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
                td["df"] / 2,
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
                td["da"] / 2,
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
    ax = add_background_rect(ax, xlim, ylim)
    ax.set_position((0, 0, 1, 1))
    ax.set_axis_off()

    return ax
