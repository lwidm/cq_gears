import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.patches import Circle
from matplotlib.patches import Arc
import subprocess
from pathlib import Path

from . import math


def _my_arrow(
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
        width=0.02,
        head_width=0.1,
        head_length=head_length,
        color=color,
        alpha=1.0,
        zorder=zorder,
    )

    return ax


def involute_plot(ax: Axes, phi: float, show_arrows: bool, show_angle: bool) -> Axes:
    lw: float = 3.0
    r: float = 1.0

    phi_r: float = np.radians(phi)
    phi_r_arr: np.ndarray = np.linspace(0, phi_r, 500)

    x_inv: np.ndarray
    y_inv: np.ndarray
    x_inv, y_inv = math.involute(r, phi_r_arr)

    x_arc_end: float = r * np.cos(phi_r)
    y_arc_end: float = r * np.sin(phi_r)

    zorder: int = 100

    circle = Circle((0, 0), r, color="gray", alpha=1)
    arc = Arc(
        (0, 0),
        width=r * 2,
        height=r * 2,
        theta2=0.0,
        theta1=phi,
        color="green",
        lw=lw,
        alpha=1.0,
        zorder=zorder,
    )
    zorder += 1
    ax.add_patch(circle)
    ax.add_patch(arc)

    ax.plot(
        [x_arc_end, x_inv[-1]],
        [y_arc_end, y_inv[-1]],
        color="green",
        linewidth=lw,
        zorder=zorder,
    )
    zorder += 1

    ax.plot(
        x_inv,
        y_inv,
        color="white",
        linewidth=lw,
        zorder=zorder,
    )
    zorder += 1
    if show_angle:
        ax.plot(
            [r, 0, x_arc_end],
            [0, 0, y_arc_end],
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
        ax = _my_arrow(
            ax,
            x1=0.0,
            y1=0.0,
            x2=x_arc_end,
            y2=y_arc_end,
            color="yellow",
            zorder=zorder,
        )
        zorder += 1
        ax = _my_arrow(
            ax,
            x1=x_arc_end,
            y1=y_arc_end,
            x2=x_inv[-1],
            y2=y_inv[-1],
            color="orange",
            zorder=zorder,
        )
        zorder += 1

    ax.set_aspect("equal")
    ax.set_facecolor("black")
    ax.set_xlim(-1.5 * r, 3 * r)
    ax.set_ylim(-1.5 * r, 3 * r)

    return ax

def create_involute_video(output_dir: Path, video_length: float):
    temp_dir = output_dir / "involute"
    temp_dir.mkdir(exist_ok=True)

    phi_arr: np.ndarray = np.arange(15, 180, 1)
    for i, phi in enumerate(phi_arr):
        fig, ax = plt.subplots(figsize=(5, 5))
        involute_plot(ax=ax, phi=phi, show_arrows=True, show_angle=True)
        fig.savefig(temp_dir / f"involute_{i:03d}.png", dpi=300, bbox_inches="tight")
        plt.close(fig)

    frame_files: list[Path] = sorted(temp_dir.glob("involute_*.png"))
    total_frames: int = len(frame_files)
    if total_frames == 0:
        raise ValueError(f"No frames found in {temp_dir}")

    framerate = int(total_frames / video_length)
    output_path = output_dir / "involute.mp4"

    subprocess.run([
        "ffmpeg",
        "-y",
        "-framerate", str(framerate),
        "-i", str(temp_dir / "involute_%03d.png"),
        "-vf", "scale=ceil(iw/2)*2:ceil(ih/2)*2",
        "-c:v", "libx264",
        "-preset", "medium",
        "-profile:v", "baseline",
        "-level", "3.0",
        "-pix_fmt", "yuv420p",
        str(output_path),
    ], check=True)

    for f in temp_dir.iterdir():
        f.unlink()
    temp_dir.rmdir()
