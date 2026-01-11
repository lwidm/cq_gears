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
    type: Literal["degree", "radian"] = "degree",
    dir: Literal["clockwise", "counterclockwise"] = "counterclockwise",
    n: int = 200,
) -> np.ndarray:
    if type == "degree":
        phi_start = np.radians(phi_start)
        phi_end = np.radians(phi_end)

    if phi_end < phi_start:
        phi_end += 2 * np.pi

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
        phi_end=360 - np.abs(phi_r),
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


def create_involute_video(output_dir: Path, video_length: float):
    temp_dir = output_dir / "involute"
    temp_dir.mkdir(exist_ok=True)

    phi_min: float = -90
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
            type="line",
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


def hypotrochoid_plot_compute(
    phi_0: float, phi_hypo: float, phi_inv: float, phi_hypo_max: float | None = None
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
    rf: float = geardata.df / 2
    rb: float = geardata.db / 2
    rp: float = geardata.d / 2
    alpha_t_r: float = geardata.alpha_t_r

    phi_0 = - phi_0
    phi_hypo = -phi_hypo
    if phi_hypo_max is None:
        phi_hypo_max = phi_hypo
    else:
        phi_hypo_max = -phi_hypo_max

    phi_hypo_r: float = np.radians(phi_hypo)
    phi_0_r: float = np.radians(phi_0)
    phi_r_arr: np.ndarray = np.linspace(phi_0_r, phi_hypo_r, 500)

    phi_r_arr_inv: np.ndarray = np.linspace(0.0, np.radians(phi_inv), 500)
    points_inv: np.ndarray = math.involute(
        rb, phi_r_arr_inv
    )
    points_inv = math.rotate(points_inv, alpha_t_r)

    points_hypo: np.ndarray = math.hypotrochoid(
        rp, rf, alpha_t_r, phi_r_arr
    )


    hypo_inv_dict: dict[str, np.ndarray] = involute_plot_compute(
        r=rp,
        phi_0=phi_0,
        phi=phi_hypo,
        rotate=0.0,
        phi_max=phi_hypo_max,
    )

    result: dict[str, float | np.ndarray | GearData | dict] = {
        "rf": rf,
        "rb": rb,
        "rp": rp,
        "alpha_t_r": alpha_t_r,
        "points_inv": points_inv,
        "points_hypo": points_hypo,
        "geardata": geardata,
        "hypo_inv_dict": hypo_inv_dict,
    }

    return result


def hypotrochoid_plot(
    ax: Axes,
    phi_0: float,
    phi_hypo: float,
    show_arrows: bool,
    show_line: bool,
    phi_hypo_max: float | None = None,
) -> Axes:
    lw: float = 1.0

    zorder: int = 100

    hypotrochoid_dict: dict = hypotrochoid_plot_compute(
        phi_0, phi_hypo, 30, phi_hypo_max
    )
    involute_dict: dict[str, np.ndarray] = hypotrochoid_dict["hypo_inv_dict"]

    dedendum_circle = Circle(
        (0, 0),
        hypotrochoid_dict["rf"],
        color="gray",
        alpha=1,
        fill=False,
        zorder=zorder,
    )
    ax.add_patch(dedendum_circle)
    zorder += 1
    pitch_circle = Circle(
        (0, 0),
        hypotrochoid_dict["rp"],
        color="gray",
        alpha=1,
        fill=False,
        zorder=zorder,
    )
    ax.add_patch(pitch_circle)
    zorder += 1
    base_circle = Circle(
        (0, 0),
        hypotrochoid_dict["rb"],
        color="gray",
        alpha=1,
        fill=False,
        zorder=zorder,
    )
    ax.add_patch(base_circle)
    zorder += 1

    ax.plot(
        hypotrochoid_dict["points_inv"][0, :],
        hypotrochoid_dict["points_inv"][1, :],
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
        hypotrochoid_dict["points_hypo"][0, :],
        hypotrochoid_dict["points_hypo"][1, :],
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
            x2=hypotrochoid_dict["points_hypo"][0, -1],
            y2=hypotrochoid_dict["points_hypo"][1, -1],
            color="orange",
            zorder=zorder,
        )
        zorder += 1

    geardata: core.GearData = hypotrochoid_dict["geardata"]
    ax.set_aspect("equal")
    xlim: tuple[float, float] = (0.0, 0.6 * geardata.da)
    ylim: tuple[float, float] = (-0.3 * geardata.da, 0.3 * geardata.da)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax = add_background_rect(ax, xlim, ylim)
    ax.set_position((0, 0, 1, 1))
    ax.set_axis_off()

    return ax


def create_hypotrochoid_video(output_dir: Path, video_length: float):
    temp_dir = output_dir / "hypotrochoid"
    temp_dir.mkdir(exist_ok=True)

    phi_min: float = -30
    phi_max: float = 90
    step: float = 1 if phi_max > phi_min else -1
    step /= 3
    phi_arr: np.ndarray = np.arange(phi_min, phi_max, step)

    # Create a single figure for live preview
    plt.ion()  # Turn on interactive mode
    fig, ax = plt.subplots(figsize=(5, 5))
    plt.show(block=False)

    i: int = -1
    for phi in phi_arr:
        i += 1
        if (phi - phi_min) / step < 2:
            i -= 1
            continue
        if phi >= 0 and phi / step < 2:
            i -= 1
            continue
        ax.clear()  # Clear previous frame
        hypotrochoid_plot(
            ax=ax,
            phi_0=phi_min,
            phi_hypo=phi,
            show_arrows=True,
            show_line=True,
            phi_hypo_max=phi_arr[-1],
        )
        fig.canvas.draw()
        fig.canvas.flush_events()
        plt.pause(0.001)  # Brief pause to update display
        fig.savefig(temp_dir / f"hypotrochoid_{i:03d}.png", dpi=300)

    plt.ioff()  # Turn off interactive mode
    plt.close(fig)

    frame_files: list[Path] = sorted(temp_dir.glob("hypotrochoid_*.png"))
    total_frames: int = len(frame_files)
    if total_frames == 0:
        raise ValueError(f"No frames found in {temp_dir}")

    framerate = int(total_frames / video_length)
    output_path = output_dir / "hypotrochoid.mp4"

    ffmpeg_video(temp_dir, output_path, "hypotrochoid", framerate)
