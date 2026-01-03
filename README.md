# CadQuery Gear Cutting Simulation

A CadQuery-based simulation of the gear cutting process using a rack cutter. Generates gears through hobbing simulation and (optionally) creates a video of the cutting process.

## Setup

Create the conda environment:

```bash
conda env create -f environment.yaml
conda activate cqdev
```

## Usage

Run the main script:

```bash
python cog4.py
```

Edit parameters in `cog4.py`:
- `m` - module
- `z` - number of teeth
- `alpha` - pressure angle
- `num_cut_positions` - number of cutting steps
- `visualize` - visualization mode: `None`, `"show"`, `"step"`, `"img"`

## Features

- Parametric gear generation with DIN standard parameters
- Rack cutter profile with filleted tooth bases
- Step-by-step hobbing simulation
- Multiple visualization modes:
  - Interactive 3D view (`"show"`)
  - STEP file export (`"step"`)
  - PNG frame sequence (`"img"`)
- Automatic video generation from frames
- High-quality rendering with PyVista

## TODO

- [ ] Profile shift (Profilverschiebung)
- [ ] Shaft/axis integration (Achse)
