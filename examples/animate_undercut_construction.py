from matplotlib import pyplot as plt
from pathlib import Path

from cq_gears import plotting as cqg_plt

output_dir: Path = Path("output")

fig, ax = plt.subplots(figsize=(5, 5))
cqg_plt.plot_undercut_construction(
    ax=ax, phi_0=30.0, phi_undercut=-50, flank="right", show_arrows=True, show_line=True
)
fig.savefig(output_dir / f"undercut.png", dpi=300)
plt.show()
plt.close(fig)

cqg_plt.animate_undercut_construction(output_dir=output_dir, video_length=10)
