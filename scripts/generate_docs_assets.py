"""
Generate all videos and plots required for the LaTeX documentation.

This script creates:
- involute_line.mp4 and involute_line.png
- involute_string.mp4 and involute_string.png
- hypotroichoid.mp4 and hypotroichoid.png

Run from repository root: python scripts/generate_docs_assets.py
"""

import sys
from pathlib import Path
from matplotlib import pyplot as plt

repo_root: Path = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

import cq_gears

output_dir: Path = repo_root / "docs" / "assets"
output_dir.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("Generating documentation assets")
print("=" * 60)

# 1. Involute - Line Construction
print("\n[1/6] Generating involute_line.png...")
fig, ax = plt.subplots(figsize=(5, 5))
cq_gears.plotting.involute_plot(
    ax=ax,
    phi_0=0.0,
    phi=50,
    show_arrows=True,
    show_angle=True,
    type="line"
)
fig.savefig(output_dir / "involute_line.png", dpi=300, bbox_inches='tight')
plt.close(fig)
print("Saved involute_line.png")

print("[2/6] Generating involute_line.mp4...")
cq_gears.plotting.create_involute_video(
    output_dir=output_dir,
    video_length=10,
    type="line"
)
(output_dir / "involute.mp4").rename(output_dir / "involute_line.mp4")
print("Saved involute_line.mp4")

# 2. Involute - String Construction
print("[3/6] Generating involute_string.png...")
fig, ax = plt.subplots(figsize=(5, 5))
cq_gears.plotting.involute_plot(
    ax=ax,
    phi_0=0.0,
    phi=50,
    show_arrows=True,
    show_angle=True,
    type="string"
)
fig.savefig(output_dir / "involute_string.png", dpi=300, bbox_inches='tight')
plt.close(fig)
print("Saved involute_string.png")

print("[4/6] Generating involute_string.mp4...")
cq_gears.plotting.create_involute_video(
    output_dir=output_dir,
    video_length=10,
    type="string"
)
(output_dir / "involute.mp4").rename(output_dir / "involute_string.mp4")
print("Saved involute_string.mp4")

# 3. Undercut (Hypotrochoid)
print("[5/6] Generating hypotroichoid.png...")
fig, ax = plt.subplots(figsize=(5, 5))
cq_gears.plotting.undercut_plot(
    ax=ax,
    phi_0=30.0,
    phi_undercut=-50,
    flank="right",
    show_arrows=True,
    show_line=True
)
fig.savefig(output_dir / "hypotroichoid.png", dpi=300, bbox_inches='tight')
plt.close(fig)
print("Saved hypotroichoid.png")

print("[6/6] Generating hypotroichoid.mp4...")
cq_gears.plotting.create_undercut_video(
    output_dir=output_dir,
    video_length=10
)
(output_dir / "undercut.mp4").rename(output_dir / "hypotroichoid.mp4")
print("Saved hypotroichoid.mp4")

print("\n" + "=" * 60)
print("All assets generated successfully!")
print(f"Output directory: {output_dir}")
print("=" * 60)
