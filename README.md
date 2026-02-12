# cq_gears

Parametric gear generation for CadQuery with DIN standard support.

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
