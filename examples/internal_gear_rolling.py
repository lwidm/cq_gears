import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from pathlib import Path

import cq_gears


def main() -> None:
    output_dir: Path = Path("output")
    d_ring: float = 5
    d_pinion: float = 3

    fig: Figure
    ax: Axes
    fig, ax = plt.subplots(figsize=(5, 5))
    cq_gears.plotting.plot_rolling_circle(
        ax, d_ring, d_pinion, 20.0/180*2*np.pi
    )
    fig.savefig(output_dir / f"rolling_circle.png", dpi=300)
    plt.show()
    plt.close(fig)
    cq_gears.plotting.create_rolling_circle_video(
        output_dir=output_dir, video_length=10
    )


if __name__ == "__main__":
    main()
