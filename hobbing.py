import cadquery as cq
import numpy as np
from typing import Literal
from pathlib import Path
import pyvista as pv

from core import Gear
from visualization import setup_visualization, visualize_step


def _simulate_gear_cutting(
    gear: Gear,
    num_cut_positions: int,
    visualize: Literal[None, "show", "step", "img"],
) -> cq.Workplane:

    if gear.rack is None:
        raise ValueError(
            "Could not simulate gear cutting. No rack found in gear (None value)"
        )
    rack: cq.Workplane = gear.rack

    m: float = gear.data.m
    z: float = gear.data.z
    b: float = gear.data.b
    d: float = gear.data.d
    p: float = gear.data.p

    r: float = d / 2
    d_blank: float = d + 3 * m

    gear_blank: cq.Workplane = cq.Workplane("XY").circle(d_blank / 2).extrude(b)

    cut_counter: int = 0
    output_dir: Path = Path("output")
    step_dir: Path = output_dir / "step"
    image_dir: Path = output_dir / "img"
    tmp_dir: Path = output_dir / "tmp"

    fixed_camera_position: pv.CameraPosition | None = setup_visualization(
        visualize, step_dir, image_dir, tmp_dir, gear_blank
    )

    result: cq.Workplane = gear_blank
    cut_counter = visualize_step(
        result,
        None,
        visualize,
        cut_counter,
        step_dir,
        image_dir,
        tmp_dir,
        fixed_camera_position,
    )

    for i in range(num_cut_positions):
        t: float = i / (num_cut_positions)
        x_rack: float = p * z * (1 / 2 - t)
        theta: float = x_rack / r

        positioned_rack: cq.Workplane = rack.translate((-x_rack, -r, 0.0)).rotate(
            (0, 0, 0), (0, 0, 1), np.degrees(theta)
        )

        result = result.cut(positioned_rack)
        cut_counter = visualize_step(
            result,
            positioned_rack,
            visualize,
            cut_counter,
            step_dir,
            image_dir,
            tmp_dir,
            fixed_camera_position,
        )

    return result
