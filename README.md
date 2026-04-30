# cq_gears

Parametric involute gear generation for [CadQuery](https://github.com/CadQuery/cadquery), built around analytical curve equations rather than boolean cuts. Follows DIN / ISO 21771 conventions.

## Overview

`cq_gears` produces high-precision involute gear solids in CadQuery. Two construction methods are available:

- **Parametric (recommended).** A user-defined number of points is sampled along the tooth flanks using the closed-form parametric equations (involute, undercut, tip arc). The points are connected with splines or arcs and stitched into a single tooth profile, which is then polar-patterned around the root cylinder.
- **Hobbing.** A standard rack cutter is swept around a blank cylinder and subtracted in many positions. This mirrors how real gears are cut and is useful as a reference, but it's expensive (minutes per gear) and the resulting solid is approximated by short straight cuts rather than continuous curves.

## Why parametric

- **Smooth curves, sharp edges only where intended.** The output consists of a few clean splines and arcs joined at well-defined points (the involute–untercut junction and the tip corners). This makes downstream work (exporting to other CAD tools, meshing for FEA, or rendering) much cleaner than dealing with the dense facet network that boolean hobbing produces.
- **Fast.** Each gear is a single sketch plus an extrude / twist-extrude, though the computation of the parametric points does also take a couple seconds. Hobbing requires one boolean cut per rack position and is several orders of magnitude slower.
- **No approximations.** The undercut curve below the base circle is computed from its exact equations, and the involute–untercut and involute-involute intersection is solved with Newton-Raphson rather than approximated.

## Supported gear types

| Type                                     | Parametric | Hobbing | Status   |
|------------------------------------------|:----------:|:-------:|----------|
| Spur (*Stirnräder*)                      | yes          | yes       | Done     |
| Helical, external (*Schrägverzahnung*)   | yes          | yes       | Done     |
| Internal (spur / helical)                | —          | —       | Planned  |
| Bevel (*Kegelräder*)                     | —          | —       | Planned  |
| Worm (*Schneckenräder*)                  | —          | —       | Planned  |
| Crossed helical / screw (hyperboloid)    | —          | —       | Planned  |
| Hypoid (*Hypoidräder*)                   | —          | —       | Planned  |

## Obtaining and running the code
Make sure lfs is installed:
```zsh
git lfs install
```
Then clone:
```zsh
git clone git@github.com:lwidm/cq_gears.git
```
The project requires `conda` to work. So after making it available (), `cd` into the repository:
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

`cq_gears` builds tooth profiles from closed-form analytical equations rather than from approximations or boolean cuts. The flank of every involute gear obviously is an involute of the base circle and at the tooth root the rack tip sweeps out the undercut curve as it rolls along the pitch circle. Profile shift is also considered. Where these curves meet (the involute to undercut junction and the left to right self-intersection that can occur for small tooth counts with positive profile shift), Newton-Raphson computes the exact intersection point. Helical gears reduce to spur gears as the helix angle goes to zero, with the standardised flank normal inputs ($\alpha_n$, $m_n$) converted to the transverse (normal to the gear) parameters ($\alpha_t$, $m_t$) used to construct the 2D profile.

Complete derivations, including all Jacobians and integration bounds, are available in the [Theory (PDF)](https://lwidm.github.io/cq_gears/theory.pdf). All conventions follow DIN / ISO 21771. The summary below mirrors the formula sheet at the end of the PDF. Personally I do not recommend using the summary below as the PDF is more accurate in its description and renders the equations better. Also I pay more attention to the PDF so there is a chance the following summary is out of date.

### Notation and symbols

#### Gear parameters

| Symbol | Meaning | German |
|--------|---------|--------|
| $m_n$ | Normal module | *Normalmodul* |
| $m_t$ | Transverse module | *Stirnmodul* |
| $z$ | Number of teeth | *Zähnezahl* |
| $\alpha_n$ | Normal pressure angle | *Normaleingriffswinkel* |
| $\alpha_t$ | Transverse pressure angle | *Stirneingriffswinkel* |
| $\beta$ | Helix angle (at pitch cylinder) | *Schrägungswinkel* |
| $\beta_b$ | Base helix angle | *Grundschrägungswinkel* |
| $x$ | Profile shift coefficient | *Profilverschiebungsfaktor* |
| $h_a^{\ast}$ | Addendum coefficient | *Kopfhöhenfaktor* |
| $c^{\ast}$ | Tip clearance factor | *Kopfspielfaktor* |
| $p$ | Pitch | *Teilung* |

#### Diameters and tooth heights

| Symbol | Meaning | German |
|--------|---------|--------|
| $d_p$ | Pitch (reference) circle diameter | *Teilkreisdurchmesser* |
| $d_b$ | Base circle diameter | *Grundkreisdurchmesser* |
| $d_a$ | Addendum (tip) circle diameter | *Kopfkreisdurchmesser* |
| $d_f$ | Dedendum (root) circle diameter | *Fusskreisdurchmesser* |
| $d^{\ast}$ | Arbitrary diameter | — |
| $h_a$ | Addendum height | *Zahnkopfhöhe* |
| $h_f$ | Dedendum height | *Zahnfusshöhe* |
| $s_0$ | Tooth thickness at pitch circle | — |
| $\gamma$ | Half tooth angle at base circle | — |

#### Curves and operators

| Symbol | Meaning |
|--------|---------|
| $\phi$ | Curve parameter (rolling angle) |
| $\theta$ | Angle with respect to x-axis |
| $\phi_0, \phi_{start}$ | Starting parameter value |
| $\phi_{end}$ | Ending parameter value |
| $\mathbf{r}_\text{inv}(\phi)$ | Involute position vector |
| $\mathbf{r}_\text{undercut}(\phi)$ | Undercut curve position vector |
| $\mathbf{T}(\phi)$ | Unit tangent vector |
| $\mathbf{N}(\phi)$ | Unit normal vector |
| $\mathbf{R}(\theta)$ | 2D rotation matrix |

The sign $\pm$ refers to the flank: $+$ for the right flank (counterclockwise rotating involute) and $-$ for the left flank.

### Equation summary

Inputs: $m_n$, $z$, $\alpha_n$, $\beta$, $x$, $h_a^{\ast}$, $c^{\ast}$. Standard involute gears use $\alpha_n = 20°$, $h_a^{\ast} = 1$, $c^{\ast} = 0.25$.

#### Helical-to-transverse conversions

For a helical gear with helix angle $\beta$, the tooth profile is constructed in the transverse plane (perpendicular to the gear axis); the transverse pressure angle $\alpha_t$, transverse module $m_t$, and base helix angle $\beta_b$ are derived from the standardised normal-section inputs by:

$$
\tan(\alpha_t) = \frac{\tan(\alpha_n)}{\cos(\beta)}, \qquad m_t = \frac{m_n}{\cos(\beta)}, \qquad \tan(\beta_b) = \tan(\beta) \cos(\alpha_t)
$$

For spur gears ($\beta = 0$) these collapse to $\alpha_t = \alpha_n$, $m_t = m_n$, $\beta_b = 0$.

#### Circle diameters

$$
d_p = m_t \cdot z, \qquad d_b = d_p \cos(\alpha_t)
$$

$$
d_a = d_p + 2 h_a = m_t z + 2 m_n (h_a^{\ast} + x), \qquad d_f = d_p - 2 h_f = m_t z - 2 m_n (h_a^{\ast} + c^{\ast} - x)
$$

with $h_a = (h_a^{\ast} + x)  m_n$ and $h_f = (h_a^{\ast} + c^{\ast} - x)  m_n$.

#### Half tooth angle γ at base circle

$$
\gamma = \frac{m_t \pi + 4  x  m_n \tan(\alpha_n)}{2  d_p} + \sqrt{\left(\frac{d_p}{d_b}\right)^2 - 1} - \arctan\sqrt{\left(\frac{d_p}{d_b}\right)^2 - 1}
$$

The first term is the half tooth thickness at the pitch circle (including profile shift); the remaining two terms account for the involute angle from base to pitch circle.

#### Involute curve

$$
\mathbf{r}_\text{inv}(\phi) = \frac{d_b}{2}\begin{bmatrix} \cos(\phi) + \phi \sin(\phi) \\ \sin(\phi) - \phi \cos(\phi) \end{bmatrix}, \qquad \phi(d^{\ast}) = \pm \sqrt{\left(\frac{d^{\ast}}{d_b}\right)^2 - 1}
$$

Bounds: $\phi_\text{start} = 0$ (base circle) and $\phi_\text{end} = \phi(d_a)$ (addendum circle), unless truncated by one of the intersections below.

#### Undercut curve

$$
\mathbf{r}_\text{undercut}(\phi) = \frac{1}{2}\left( \begin{bmatrix} a \\ b \end{bmatrix} \cos(\phi) + \begin{bmatrix} -b \\ a \end{bmatrix} \sin(\phi) + d_p \phi \begin{bmatrix} \sin(\phi) \\ -\cos(\phi) \end{bmatrix} \right)
$$

with $a = d_f$ and $b = \pm d_f \tan(\alpha_t)$. Start: $\phi_0 = \pm \tfrac{d_f}{d_p} \tan(\alpha_t)$ (dedendum circle). End: at the involute–undercut intersection (below).

#### Curve positioning (γ rotation)

To assemble a symmetric tooth, each flank curve is rotated about the gear center:

- Involute: rotate by $\pm(-\gamma)$
- Undercut: rotate by $\pm(-\gamma - \alpha_t)$

The opposite flank is obtained by mirroring across the x-axis.

#### Curve intersections (Newton-Raphson)

**Left–right involute self-intersection.** Relevant for small $z$ with positive profile shift, where the two flanks of one tooth meet before reaching $d_a$. Solve

$$
\frac{\sin(\phi) - \phi \cos(\phi)}{\cos(\phi) + \phi \sin(\phi)} = \tan(\gamma)
$$

with iteration

$$
\phi_{n+1} = \phi_n - \frac{a}{\phi_n^2}\left(b - a \tan(\gamma)\right), \quad a = \cos(\phi_n) + \phi_n \sin(\phi_n), \quad b = \sin(\phi_n) - \phi_n \cos(\phi_n)
$$

If the solution $\phi_\infty < \phi(d_a)$, the involute is truncated at $\phi_\infty$ instead of the addendum circle.

**Involute–undercut intersection.** Solve the 2D system $\mathbf{F}(\phi_i, \phi_u) = \mathbf{0}$ with $c = \cos(\alpha_t)$, $d = \sin(\pm \alpha_t)$:

$$\begin{aligned}
f_1 &= d_b c \cos(\phi_i) + d_b c \phi_i \sin(\phi_i) - d_b d \sin(\phi_i) + d_b d \phi_i \cos(\phi_i) \\
    &\quad - a \cos(\phi_u) + b \sin(\phi_u) - d_p \phi_u \sin(\phi_u) \\
f_2 &= d_b d \cos(\phi_i) + d_b d \phi_i \sin(\phi_i) + d_b c \sin(\phi_i) - d_b c \phi_i \cos(\phi_i) \\
    &\quad - b \cos(\phi_u) - a \sin(\phi_u) + d_p \phi_u \cos(\phi_u)
\end{aligned}$$

via $\mathbf{x}^{(k+1)} = \mathbf{x}^{(k)} - \mathbf{J}^{-1}  \mathbf{F}(\mathbf{x}^{(k)})$ where $\mathbf{x} = (\phi_i, \phi_u)^\top$ and the Jacobian is

$$
\mathbf{J} = \begin{bmatrix} d_b \phi_i \big(c \cos\phi_i - d \sin\phi_i\big) & a \sin\phi_u + b \cos\phi_u - d_p \sin\phi_u - d_p \phi_u \cos\phi_u \\ d_b \phi_i \big(d \cos\phi_i + c \sin\phi_i\big) & b \sin\phi_u - a \cos\phi_u + d_p \cos\phi_u - d_p \phi_u \sin\phi_u \end{bmatrix}
$$

The solution gives the actual start of the involute ($\phi_i$) and end of the undercut ($\phi_u$). Initial guesses come from the diameters of the involute–pitch and undercut–pitch crossings.

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

#### PDF viewer support for `run:` links

Whether the click-to-play actually works depends on the PDF viewer. Most modern viewers prompt the user the first time before launching the external file:

| Viewer                                | OS              | `run:` links work? |
|---------------------------------------|-----------------|--------------------|
| Okular                                | Linux (KDE)     | Yes (prompts)      |
| SumatraPDF                            | Windows         | Yes (prompts)      |
| Adobe Acrobat Reader                  | Windows / macOS / Linux | Yes (prompts)      |
| zathura                               | Linux           | No                 |
| Firefox / Chrome built-in PDF viewer  | All             | No (blocked)       |

#### Video player

Clicking a `run:` link launches the file with your OS's default video player. Make sure one is installed and registered as the handler for `.mp4`. `mpv` is a good lightweight default:

- **openSUSE:** `sudo zypper install mpv`
- **Debian/Ubuntu:** `sudo apt install mpv`
- **Arch:** `sudo pacman -S mpv`

Quick sanity check on Linux: `xdg-open docs/assets/involute_line.mp4` should open the video in your default player. If it doesn't, the PDF click won't work either.
