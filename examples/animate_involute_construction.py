from matplotlib import pyplot as plt
from pathlib import Path

import cq_gears


def main() -> None:
    output_dir: Path = Path("output")

    fig, ax = plt.subplots(figsize=(5, 5))
    cq_gears.plotting.plot_involute_construction(
        ax=ax, phi_0=0.0, phi=50, show_arrows=True, show_angle=True, type="line"
    )
    fig.savefig(output_dir / f"involute.png", dpi=300)
    plt.show()
    plt.close(fig)
    cq_gears.plotting.animate_involute_construction(
        output_dir=output_dir, video_length=10, type="line"
    )


if __name__ == "__main__":
    main()
