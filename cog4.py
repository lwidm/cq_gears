import cadquery as cq
from cadquery.vis import show
import numpy as np
from typing import Literal
from pathlib import Path
from cadquery import exporters
import pyvista as pv
import subprocess

m: float = 2.0  # Module, Modul
z: int = 20  # Number of teeth, Zähnezahl
x: float = 0.0  # Profile shift, Profilverschiebung
alpha: float = 20.0  # [degree] Pressure angle, Eingriffswinkel
thickness: float = 10
c_star: float = 0.167


def render_to_image(
    gear: cq.Workplane,
    rack: cq.Workplane | None,
    output_path: Path,
    window_size: tuple[int, int] = (1920, 1080),
    camera_position: tuple | None = None,
) -> None:
    temp_gear_stl = output_path.parent / "temp_gear.stl"
    exporters.export(gear, str(temp_gear_stl))

    plotter = pv.Plotter(off_screen=True, window_size=list(window_size))

    gear_mesh = pv.read(str(temp_gear_stl))
    plotter.add_mesh(gear_mesh, color='lightblue', smooth_shading=True) # type: ignore

    if rack is not None:
        temp_rack_stl = output_path.parent / "temp_rack.stl"
        exporters.export(rack, str(temp_rack_stl))
        rack_mesh = pv.read(str(temp_rack_stl))
        plotter.add_mesh(rack_mesh, color='orange', smooth_shading=True) # type: ignore
        temp_rack_stl.unlink()

    if camera_position is not None:
        plotter.camera_position = camera_position
    else:
        plotter.camera_position = 'iso'
        plotter.camera.zoom(1.2)

    plotter.screenshot(str(output_path))
    plotter.close()

    temp_gear_stl.unlink()


def create_rack_cutter_sketch(
    m: float,
    alpha: float,
    ha_star: float,
    c_star: float,
    rho_f_star: float,
    z: int,
) -> cq.Sketch:
    """
    Create a rack cutter profile with multiple teeth.

    The rack consists of multiple trapezoid teeth with rounded tips,
    arranged along the X-axis with proper pitch spacing.

    Args:
        m: module (DE: Modul)
        alpha: pressure angle [degree] (DE: Eingriffswinkel [grad])
        ha_star: addendum coefficient (DE: Kopfhöhenfaktor)
        c_star: clearance coefficient (DE: Kopfspielfaktor)
        rho_f_star: fillet radius coefficient (DE: Fussrundungsfaktor).
                    If negative, use tangentArcPoint instead.
        z: number of teeth (DE: Zähnezahl)
    Returns:
        CadQuery Workplane with rack cutter profile
    """

    d: float = m * float(z)  # pitch diameter (DE: Teilkreisdurchmesser)
    ha: float = ha_star * m  # addendum (DE: Zahnkopfhöhe)
    hf: float = (ha_star + c_star) * m  # dedendum (DE: Zahnfusshöhe)
    rho_f: float = abs(rho_f_star) * m  # fillet radius at tip (DE: Fussrundung)
    alpha_r: float = np.radians(alpha)
    p: float = np.pi * m  # pitch (DE: Teilung)

    rack_length: float = (z + 4) * p
    base_height: float = 3 * m

    toothwidth_at_base: float = p / 2 + 2 * hf * np.tan(alpha_r)

    rack_sketch: cq.Sketch = (
        cq.Sketch()
        .push([(0, -base_height / 2 - hf)])
        .rect(rack_length, base_height)
        .push([(0, (ha + hf) / 2 - hf)])
        .rarray(p, 1, z + 4, 1)
        .trapezoid(toothwidth_at_base, ha + hf, 90 - alpha, mode="a")
        .clean()
    )

    return rack_sketch


def simulate_gear_cutting(
    z: int,
    m: float,
    alpha: float,
    num_cut_positions: int,
    extrude_depth: float,
    visualize: Literal[None, "show", "step", "img"],
) -> cq.Workplane:
    d: float = m * z
    r: float = d / 2
    p: float = np.pi * m

    d_blank: float = d + 3 * m
    gear_blank: cq.Workplane = (
        cq.Workplane("XY").circle(d_blank / 2).extrude(extrude_depth)
    )

    rack_cutter_sketch: cq.Sketch = create_rack_cutter_sketch(
        m=m,
        alpha=alpha,
        ha_star=1.0,
        c_star=c_star,
        rho_f_star=0.3,
        z=z,
    )
    rack_cutter: cq.Workplane = (
        cq.Workplane("XY").placeSketch(rack_cutter_sketch).extrude(extrude_depth)
    )

    cut_counter = [0]
    output_dir: Path = Path("output")
    fixed_camera_position = [None]  # Will be set on first render

    if visualize == "step":
        output_dir = Path("output_step")
        output_dir.mkdir(exist_ok=True)
    elif visualize == "img":
        output_dir = Path("output_img")
        output_dir.mkdir(exist_ok=True)

        # Setup fixed camera by rendering gear once to get camera position
        temp_stl = output_dir / "temp_setup.stl"
        exporters.export(gear_blank, str(temp_stl))
        plotter = pv.Plotter(off_screen=True)
        mesh = pv.read(str(temp_stl))
        plotter.add_mesh(mesh)
        plotter.camera_position = 'iso'
        plotter.camera.zoom(1.2)
        fixed_camera_position[0] = plotter.camera_position
        plotter.close()
        temp_stl.unlink()

    def visualize_fun(rack: cq.Workplane | None =None) -> None:
        if visualize == "show":
            if rack is not None:
                assy: cq.Assembly = cq.Assembly()
                assy.add(result, name="gear", color=cq.Color("lightblue"))
                assy.add(rack, name="rack", color=cq.Color("orange"))
                show(assy)
            else:
                show(result, alpha=0.5)
        elif visualize == "step":
            if rack is not None:
                assy: cq.Assembly = cq.Assembly()
                assy.add(result, name="gear", color=cq.Color("lightblue"))
                assy.add(rack, name="rack", color=cq.Color("orange"))
                filename: Path = output_dir / f"step_{cut_counter[0]:03d}.step"
                assy.save(str(filename))
            else:
                filename: Path = output_dir / f"step_{cut_counter[0]:03d}.step"
                cq.exporters.export(result, str(filename))
            cut_counter[0] += 1
            print(f"Saved: {filename}")
        elif visualize == "img":
            filename: Path = output_dir / f"frame_{cut_counter[0]:03d}.png"
            render_to_image(result, rack, filename, camera_position=fixed_camera_position[0])
            cut_counter[0] += 1
            print(f"Saved: {filename}")

    result: cq.Workplane = gear_blank
    visualize_fun()

    for i in range(num_cut_positions):
        t: float = i / (num_cut_positions)
        x_rack: float = p * z * (1 / 2 - t)
        theta: float = x_rack / r

        positioned_rack: cq.Workplane = rack_cutter.translate((-x_rack, -r, 0.0)).rotate(
            (0, 0, 0), (0, 0, 1), np.degrees(theta)
        )

        result = result.cut(positioned_rack)
        visualize_fun(positioned_rack)

    if visualize == "img":
        print("\nGenerating videos...")

        total_frames: int = cut_counter[0]
        target_duration: float = 4.0  # [s]
        framerate: float = float(total_frames) / target_duration

        print(f"Total frames: {total_frames}, Framerate: {framerate:.2f} fps for {target_duration}s video")

        video_path_mp4 = output_dir / "gear_cutting.mp4"
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-framerate", str(framerate),
                    "-i", str(output_dir / "frame_%03d.png"),
                    "-c:v", "libx264",
                    "-profile:v", "baseline",
                    "-level", "3.0",
                    "-pix_fmt", "yuv420p",
                    "-preset", "medium",
                    "-crf", "23",
                    str(video_path_mp4)
                ],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"✓ MP4 video created: {video_path_mp4}")
        except subprocess.CalledProcessError as e:
            print(f"✗ MP4 creation failed: {e.stderr}")
        except FileNotFoundError:
            print("✗ ffmpeg not found")

    return result


result = simulate_gear_cutting(
    z=z, m=m, alpha=alpha, num_cut_positions=10, extrude_depth=thickness, visualize="img"
)

show(result)

