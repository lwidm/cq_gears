import cadquery as cq
from cadquery import exporters
from cadquery.vis import show
import pyvista as pv
from pathlib import Path
import subprocess
from typing import Literal


def render_to_image(
    gear: cq.Workplane,
    rack: cq.Workplane | None,
    image_dir: Path,
    tmp_dir: Path,
    filename: str,
    window_size: tuple[int, int] = (1920, 1080),
    camera_position: tuple | None = None,
) -> None:
    """
    Render CadQuery objects to PNG image using PyVista.

    Args:
        gear: The gear workplane to render
        rack: Optional rack workplane to render alongside gear
        image_dir: Directory where PNG image will be saved
        tmp_dir: Directory for temporary files
        filename: Name of the output PNG file
        window_size: Tuple of (width, height) for the output image
        camera_position: Fixed camera position for consistent framing
    """
    temp_gear_stl: Path = tmp_dir / "temp_gear.stl"
    exporters.export(gear, str(temp_gear_stl), tolerance=0.01, angularTolerance=0.1)

    plotter = pv.Plotter(off_screen=True, window_size=list(window_size))
    plotter.set_background("#E8E8E8")

    gear_mesh = pv.read(str(temp_gear_stl))
    gear_mesh = gear_mesh.clean(tolerance=1e-6)
    gear_mesh = gear_mesh.triangulate()
    gear_mesh = gear_mesh.compute_normals(
        cell_normals=False,
        point_normals=True,
        split_vertices=True,
        feature_angle=30,
        flip_normals=False,
        auto_orient_normals=True,
    )

    plotter.add_mesh(
        gear_mesh,
        color="#5D6E7A",
        smooth_shading=True,
        ambient=0.4,
        diffuse=0.6,
        specular=0.2,
        specular_power=15,
    )

    if rack is not None:
        temp_rack_stl: Path = tmp_dir / "temp_rack.stl"
        exporters.export(rack, str(temp_rack_stl), tolerance=0.01, angularTolerance=0.1)

        rack_mesh = pv.read(str(temp_rack_stl))
        rack_mesh = rack_mesh.clean(tolerance=1e-6)
        rack_mesh = rack_mesh.triangulate()
        rack_mesh = rack_mesh.compute_normals(
            cell_normals=False,
            point_normals=True,
            split_vertices=True,
            feature_angle=30,
            flip_normals=False,
            auto_orient_normals=True,
        )

        plotter.add_mesh(
            rack_mesh,
            color="#B89650",
            smooth_shading=True,
            ambient=0.4,
            diffuse=0.6,
            specular=0.2,
            specular_power=15,
        )
        temp_rack_stl.unlink()

    plotter.add_light(
        pv.Light(position=(100, 100, 150), light_type="scene light", intensity=0.5)
    )
    plotter.add_light(
        pv.Light(position=(-80, -80, 100), light_type="scene light", intensity=0.4)
    )
    plotter.add_light(
        pv.Light(position=(0, -100, 80), light_type="scene light", intensity=0.3)
    )
    plotter.add_light(
        pv.Light(position=(0, 100, -50), light_type="scene light", intensity=0.2)
    )

    if camera_position is not None:
        plotter.camera_position = camera_position
    else:
        plotter.camera_position = "iso"
        plotter.camera.zoom(1.3)

    plotter.enable_anti_aliasing("fxaa")

    plotter.screenshot(str(image_dir / filename), transparent_background=False)
    plotter.close()
    temp_gear_stl.unlink()


def setup_visualization(
    visualize: Literal[None, "show", "step", "img"],
    step_dir: Path,
    image_dir: Path,
    tmp_dir: Path,
    gear_blank: cq.Workplane | None = None,
) -> tuple | None:
    """
    Setup directories and camera position for visualization.

    Args:
        visualize: Visualization mode
        step_dir: Directory for STEP files
        image_dir: Directory for image files
        tmp_dir: Directory for temporary files
        gear_blank: Gear blank workplane for camera setup (required for img mode)

    Returns:
        Fixed camera position for img mode, None otherwise
    """
    if visualize == "step":
        step_dir.mkdir(parents=True, exist_ok=True)
        # Clean directory except .gitignore
        for file in step_dir.iterdir():
            if file.name != ".gitignore":
                file.unlink()
        return None

    elif visualize == "img":
        image_dir.mkdir(parents=True, exist_ok=True)
        tmp_dir.mkdir(parents=True, exist_ok=True)

        # Clean directories except .gitignore
        for file in image_dir.iterdir():
            if file.name != ".gitignore":
                file.unlink()
        for file in tmp_dir.iterdir():
            if file.name != ".gitignore":
                file.unlink()

        # Setup fixed camera position
        if gear_blank is None:
            raise ValueError("gear_blank required for img visualization mode")

        temp_stl: Path = tmp_dir / "temp_setup.stl"
        exporters.export(gear_blank, str(temp_stl))
        plotter = pv.Plotter(off_screen=True)
        mesh = pv.read(str(temp_stl))
        plotter.add_mesh(mesh)
        plotter.camera_position = "iso"
        plotter.camera.zoom(1.2)
        fixed_camera_position = plotter.camera_position
        plotter.close()
        temp_stl.unlink()

        return fixed_camera_position

    return None


def visualize_step(
    result: cq.Workplane,
    rack: cq.Workplane | None,
    visualize: Literal[None, "show", "step", "img"],
    counter: int,
    step_dir: Path,
    image_dir: Path,
    tmp_dir: Path,
    camera_position: tuple | None = None,
) -> int:
    """
    Visualize a single step of the gear cutting process.

    Args:
        result: Current gear workplane
        rack: Optional rack workplane
        visualize: Visualization mode
        counter: Current frame/step counter
        step_dir: Directory for STEP files
        image_dir: Directory for image files
        tmp_dir: Directory for temporary files
        camera_position: Fixed camera position for img mode

    Returns:
        Updated counter value
    """
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
            filename: Path = step_dir / f"step_{counter:05d}.step"
            assy.save(str(filename))
        else:
            filename: Path = step_dir / f"step_{counter:05d}.step"
            exporters.export(result, str(filename))
        print(f"Saved: {filename}")
        return counter + 1

    elif visualize == "img":
        name: str = f"frame_{counter:05d}.png"
        render_to_image(
            result,
            rack,
            image_dir,
            tmp_dir,
            name,
            camera_position=camera_position,
        )
        print(f"Saved: {name}")
        return counter + 1

    return counter


def create_video(
    input_dir: Path,
    output_path: Path,
    video_length: float = 10.0,
    frame_pattern: str = "frame_%05d.png",
) -> None:
    """
    Create MP4 video from sequence of PNG images.

    Args:
        input_dir: Directory containing the PNG frames
        output_path: Path where the MP4 video will be saved
        video_length: Desired length of video in seconds
        frame_pattern: Printf-style pattern for frame filenames (default: frame_%05d.png)
    """
    # Count frames to calculate framerate
    frame_files = sorted(input_dir.glob("frame_*.png"))
    total_frames = len(frame_files)

    if total_frames == 0:
        print(f"✗ No frames found in {input_dir}")
        return

    framerate = total_frames / video_length

    print(f"Creating video from {total_frames} frames...")
    print(f"Framerate: {framerate:.2f} fps for {video_length}s video")

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-framerate",
                str(framerate),
                "-i",
                str(input_dir / frame_pattern),
                "-c:v",
                "libx264",
                "-profile:v",
                "baseline",
                "-level",
                "3.0",
                "-pix_fmt",
                "yuv420p",
                "-preset",
                "medium",
                "-crf",
                "23",
                str(output_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"✓ Video created: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"✗ Video creation failed: {e.stderr}")
    except FileNotFoundError:
        print("✗ ffmpeg not found. Install ffmpeg to generate videos.")
