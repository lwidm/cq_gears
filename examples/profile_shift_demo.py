from matplotlib import pyplot as plt
from pathlib import Path
import numpy as np

from cq_gears import plotting

output_dir: Path = Path("output")

fig, ax = plt.subplots(figsize=(5, 5))
x_min: float = -0.8
x_max: float = 1
step: float = 0.1
num: int = int(np.ceil((x_max-x_min)/step))
x_vals: np.ndarray = np.linspace(x_min, x_max, num=num)
plotting.profile_shift_plot(ax=ax, x_values=x_vals.tolist())
fig.savefig(output_dir / "profile_shift.png", dpi=300)
plt.show()
plt.close(fig)
