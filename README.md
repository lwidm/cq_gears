# cq_gears

Parametric gear generation for CadQuery with DIN standard support.

## Obtaining and running the code
Make sure lfs is installed:
```zsh
git lfs install
```
Then clone:
```zsh
git clone git@github.com:lwidm/cq_gears.git
```
The project requires `conda` to work. So after making it available (e.g. through `miniconda`), `cd` into the repository:
```zsh
cd cq_gears
```
Then create and activate the environment:
```zsh
conda env create -f ./environment.yaml
conda activate cqdev
```
Finally, install the package in editable mode so you can modify the source:
```zsh
pip install -e .
```

## Point array convention

2D point sets in this codebase are stored as **column-stacked** `numpy` arrays of shape `(2, N)`:
**This convention is very important due to rotation and translation opperations!**

- Row 0 (`points[0]`) holds all x-coordinates
- Row 1 (`points[1]`) holds all y-coordinates
- Column `i` (`points[:, i]`) is the i-th point `[x, y]`


### Extracting points

```python
pt = points[:, i]                        # i-th point, shape (2,)
x, y = points[:, i]                      # unpack into scalars
sub = points[:, start:end]               # slice a range, shape (2, end-start)
xs, ys = points[0], points[1]            # all x's and y's separately
```

Note that `points[i]` returns **row `i`** (all x's or all y's), not the i-th point. Always index with `points[:, i]` to get a single point.


## Theory

- [Theory (PDF)](https://lwidm.github.io/cq_gears/theory.pdf) — Derivations of the parametric equations used for gear tooth geometry, including involute, undercut, profile shift, curve positioning, and intersections.

### Building the theory PDF locally

1. **Generate assets** (videos and plots used in the PDF):
   ```bash
   python scripts/generate_docs_assets.py
   ```
   This creates `.png` and `.mp4` files in `docs/assets/`.

2. **Compile the LaTeX document** (requires a TeX Live installation with `biber`):
   ```bash
   cd docs/latex
   pdflatex theory.tex
   biber theory
   pdflatex theory.tex
   pdflatex theory.tex
   ```

### Videos in the PDF

The PDF includes clickable images that link to companion videos. When compiled locally, these use `run:` links with relative paths (e.g. `run:../assets/involute_line.mp4`), which open the video file from `docs/assets/` in your system's default player. This requires the PDF to be opened from its original location so that the relative paths resolve correctly.

When compiled in the GitHub Actions workflow, the links point to the GitHub Pages hosted versions instead (e.g. `https://lwidm.github.io/cq_gears/involute_line.mp4`), so the videos are accessible from anywhere. This switch is controlled by the `\iflocal` conditional in the LaTeX source. The workflow activates it by compiling with `pdflatex "\def\notlocal{}\input{theory.tex}"` instead of `pdflatex theory.tex`.
