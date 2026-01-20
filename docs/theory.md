$$
	\require{physics}
	\require{xcolor}	
	\newcommand{\mypm}{\textcolor{red}{\pm}}	
	\newcommand{\mymp}{\textcolor{red}{\mp}}	
	\newcommand{\myppm}{\phantom{\textcolor{red}{\pm}}}	
	\newcommand{\mypmp}{\phantom{\textcolor{red}{\mp}}}	
$$
## TODO
- Profilverschiebung
## Sources
- Involute: [https://www.youtube.com/watch?v=nrsCoQN6V4M](https://www.youtube.com/watch?v=nrsCoQN6V4M)
- undercut: [https://www.youtube.com/watch?v=TftOx_B1n2M&t=317s](https://www.youtube.com/watch?v=TftOx_B1n2M&t=317s)
- Rack cutting: [https://www.tec-science.com/de/getriebe-technik/evolventenverzahnung/zahnstange-eingriff/](https://www.tec-science.com/de/getriebe-technik/evolventenverzahnung/zahnstange-eingriff/)
- General Geometry: [https://www.tec-science.com/de/getriebe-technik/evolventenverzahnung/evolventen-zahnrad-geometrie/](https://www.tec-science.com/de/getriebe-technik/evolventenverzahnung/evolventen-zahnrad-geometrie/)
- Profilverschiebung: [https://www.tec-science.com/de/getriebe-technik/evolventenverzahnung/profilverschiebung/](https://www.tec-science.com/de/getriebe-technik/evolventenverzahnung/profilverschiebung/)
## Involute
An involute can be constructed by "unrolling" a string on the base circle (see video below)
![[involute 3.mp4]]
![[involute 5.mp4]]
![[involute 1.png|400]]
The length of the blue arrow is $\tfrac{d_b}{2}\phi$ as it is equal to the length of the unrolled string (see video above)
$$
\begin{bmatrix}
x(\phi) \\
y(\phi)
\end{bmatrix}
= \textcolor{yellow}{\tfrac{d_b}{2} \begin{bmatrix}
\cos(\phi) \\
\sin(\phi)
\end{bmatrix}}
+ \textcolor{blue}{\tfrac{d_b}{2}\phi \begin{bmatrix}
\sin(\phi) \\
-\cos(\phi)
\end{bmatrix}}
$$
### Determine value of $\phi$ when involute reaches specific diameter
In order to avoid dealing with intersections it can be useful to know at which $\phi$ a certain diameter (for e.g. the addendum diameter $d_a$) is reached
$$
\begin{align}
d^* &\stackrel{!}{=} \sqrt{x(\phi^*)^2 + y(\phi^*)^2}\cdot2 \\
(d^*/2)^2 &= x(\phi^*)^2 + y(\phi^*)^2 \\
(d^*/2)^2 &= \left(\frac{d_b}{2}\cos\phi^* + \frac{d_b}{2}\phi^* \sin\phi^*\right)^2 + \left(\frac{d_b}{2}\sin\phi^* - \frac{d_b}{2}\phi^* \cos\phi^*\right)^2 \\
(d^*/2)^2 &= \frac{d_b^2}{4}(\cos^2\phi^* + \sin^2\phi^*) + \frac{d_b^2}{4}{\phi^*}^2(\sin^2\phi^* + \cos^2\phi^*) \\
(d^*/2)^2 &= \frac{d_b^2}{4}(1 + {\phi^*}^2) \\
{d^*}^2 &= d_b^2(1 + {\phi^*}^2) \\
{\phi^*}^2 &= \frac{{d^*}^2}{d_b^2} - 1 = \frac{{d^*}^2 - d_b^2}{d_b^2} \\
\phi^* &= \pm\frac{\sqrt{{d^*}^2 - d_b^2}}{d_b}
\end{align}
$$

### Determine angle w.r.t. x-axis when  reaches specific diameter
$$
\begin{align}
x(\phi^*) &= \frac{d_b}{2}\cos\phi^* + \frac{d_b}{2}\phi^*\sin\phi^*\\
&=\frac{d_b}{2}\cos\left(\pm\frac{\sqrt{{d^*}^2 - d_b^2}}{d_b}\right) \pm \frac{d_b}{2}\frac{\sqrt{{d^*}^2 - d_b^2}}{d_b}\sin\left(\pm\frac{\sqrt{{d^*}^2 - d_b^2}}{d_b}\right) \\
&=\frac{d_b}{2}\cos\left(\pm\frac{\sqrt{{d^*}^2 - d_b^2}}{d_b}\right) \pm \frac{\sqrt{{d^*}^2 - d_b^2}}{2}\sin\left(\pm\frac{\sqrt{{d^*}^2 - d_b^2}}{d_b}\right)
\end{align}
$$

$$
\begin{align}
y(\phi^*) &= \frac{d_b}{2}\sin\phi^* - \frac{d_b}{2}\phi^*\cos\phi^*\\
&=\frac{d_b}{2}\sin\left(\pm\frac{\sqrt{{d^*}^2 - d_b^2}}{d_b}\right) \mp \frac{d_b}{2}\frac{\sqrt{{d^*}^2 - d_b^2}}{d_b}\cos\left(\pm\frac{\sqrt{{d^*}^2 - d_b^2}}{d_b}\right) \\
&=\frac{d_b}{2}\sin\left(\pm\frac{\sqrt{{d^*}^2 - d_b^2}}{d_b}\right) \mp \frac{\sqrt{{d^*}^2 - d_b^2}}{2}\cos\left(\pm\frac{\sqrt{{d^*}^2 - d_b^2}}{d_b}\right)
\end{align}
$$
$$
\begin{align}
\theta(\phi^*) &= \arctan\frac{y(\phi^*)}{x(\phi^*)} \\
 &= \arctan\frac{\frac{d_b}{2}\sin\phi^* - \frac{d_b}{2}\phi^*\cos\phi^*)}{\frac{d_b}{2}\cos\phi^* + \frac{d_b}{2}\phi^*\sin\phi^*} \\
 &= \arctan\frac{\sin\phi^* - \phi^*\cos\phi^*}{\cos\phi^* + \phi^*\sin\phi^*} 
 \textcolor{orange}{\cdot \frac{1/\cos\phi^*}{1/\cos\phi^*}}\\
 &= \arctan\frac{\tan\phi^* - \phi^*}{1 + \phi^*\tan\phi^*} 
\end{align}
$$
tangent subtraction /addition formula:
$$
\tan(\alpha \pm \beta) = \frac{\tan\alpha \pm \tan\beta}{1\mp\tan\alpha\tan{\beta}}
$$
Applying tangent subtraction formula w/ $\alpha=\phi^*$ and $\beta=\arctan{\phi^*}$
$$
\theta(\phi^*) =  \phi^* - \arctan(\phi^*)
$$
( unsurprisingly this is the involute function: $\operatorname{inv}(\phi) = \phi - \arctan\phi$ )

Inserting $\phi^* = \pm\frac{\sqrt{{d^*}^2 - d_b^2}}{d_b}$
$$
\begin{align}
\theta(d^*) &=  \pm\frac{\sqrt{{d^*}^2 - d_b^2}}{d_b} - \arctan\left(\pm\frac{\sqrt{{d^*}^2 - d_b^2}}{d_b}\right) \\
&=  \pm\left[\left(\frac{d^*}{d_b}\right)^2 - 1\right]^{\tfrac{1}{2}} - \arctan\left(\pm\left[\left(\frac{d^*}{d_b}\right)^2 - 1\right]^{\tfrac{1}{2}}\right)
\end{align}
$$

### Summery Involute
$$
\begin{align}
\vb{r_{inv}}(\phi) = 
\begin{bmatrix}
x(\phi) \\
y(\phi)
\end{bmatrix}
&= \tfrac{d_b}{2} \begin{bmatrix}
\cos(\phi) \\
\sin(\phi)
\end{bmatrix}
+ \tfrac{d_b}{2}\phi \begin{bmatrix}
\sin(\phi) \\
-\cos(\phi)
\end{bmatrix} \\

\\

\phi(d^*) &= \mypm\frac{\sqrt{{d^*}^2 - d_b^2}}{d_b}\\

\\


\theta(d^*) &=  \mypm\left[\left(\frac{d^*}{d_b}\right)^2 - 1\right]^{\tfrac{1}{2}} - \arctan\left(\mypm\left[\left(\frac{d^*}{d_b}\right)^2 - 1\right]^{\tfrac{1}{2}}\right)


\end{align}
$$

**Note**: The $\mypm$ as well as the monotonicity of $\phi$ depends on which flank
- $\textcolor{red}{+}$: Left flank (involute rotating counterclockwise) $\Rightarrow$ $\phi$ is monotonically increasing ($\phi_{start} < \phi_{end}$
	usually: $\phi_{start} = 0$  and  $\phi_{end} > 0$
- $\textcolor{red}{-}$: Right flank (involute rotating clockwise) $\Rightarrow$ $\phi$ is monotonically decreasing ($\phi_{start} > \phi_{end}$)
	usually: $\phi_{start} = 0$  and  $\phi_{end} < 0$
	
## Undercut (hypotroichoid)
### Prep math on base involute
#### 1. get tangent vector of involute
##### a) write down involute equations
$$
\vb{r_{inv}}(\phi) =
\begin{bmatrix}
x(\phi) \\
y(\phi)
\end{bmatrix}
= \textcolor{yellow}{\tfrac{d_p}{2} \begin{bmatrix}
\cos(\phi) \\
\sin(\phi)
\end{bmatrix}}
+ \textcolor{blue}{\tfrac{d_p}{2}\phi \begin{bmatrix}
\sin(\phi) \\
-\cos(\phi)
\end{bmatrix}}
$$
##### b) compute derivative of the involute

$$
\vb{r_{inv}}'(\phi) = \dv{\vb{r_{inv}}(\phi)}{\phi}
$$
x:
$$
\begin{align}
x(\phi) &= \frac{d_p}{2}(\cos(\phi) + \phi \sin(\phi))\\
x'(\phi) &= \frac{d_p}{2}(-\sin(\phi) + \sin(\phi) + \phi\cos(\phi)) \\
&= \frac{d_p}{2}\phi\cos(\phi)
\end{align}
$$

y:
$$
\begin{align}
y(\phi) &= \frac{d_p}{2}(\sin(\phi) - \phi \cos(\phi))\\
x'(\phi) &= \frac{d_p}{2}(\cos(\phi) - \cos(\phi) + \phi\sin(\phi)) \\
&= \frac{d_p}{2}\phi\sin(\phi)
\end{align}
$$
##### c) Result:

$$
\vb{r_{inv}}'(\phi) = \frac{d_p}{2}\phi\begin{bmatrix}\cos(\phi)\\\sin(\phi)\end{bmatrix}
$$

#### 2. Compute tanget and normal vectors of involute
##### a) compute magnitude of derivative
$$
\begin{align}
\norm{\vb{r_{inv}'}(\phi)} &= \frac{d_p}{2}\abs{\phi}\sqrt{\cos^2(\phi) + \sin^2(\phi)} \\
&= \frac{d_p}{2}\abs{\phi}
\end{align}
$$
##### b) tangent
The tangent vector is just $\vb{r_{inv}}'$  
$$
\begin{align}
\vb{T}(\phi) &= \frac{\vb{r_{inv}}'(\phi)}{\norm{\vb{r_{inv}}'(\phi)}}\\
&= \frac{\phi}{\abs{\phi}}\begin{bmatrix}\cos(\phi)\\\sin(\phi)\end{bmatrix}\\
&= \operatorname{sgn}(\phi) \begin{bmatrix}\cos(\phi)\\\sin(\phi)\end{bmatrix}
\end{align}
$$
##### c) normal
A unit normal is obtained by rotating the tangent by $+90°$ (or $-90°$):
$$
\vb{N}(\phi) = \operatorname{sgn}(\phi)\begin{bmatrix}-\sin(\phi)\\\cos(\phi)\end{bmatrix}
$$
#### 3. Angle of nomal/tangent w.r.t. horizontal
The angle $\theta_t$ of the tangent relative to the $x$-axis satisfies:
$$
\tan(\theta_t) = \frac{y'(\phi)}{x'(\phi)} = \frac{\phi\sin(\phi)}{\phi\cos(\phi)}=\tan{\phi}
$$
Hence:
$$
\theta_t(\phi) = \phi
$$
similarly for the angle of the normal vector:
$$
\theta_n(\phi) = \phi + \tfrac{\pi}{2}
$$
#### 4. Summary
$$
\begin{align}
\vb{r_{inv}}'(\phi) &= \frac{d_p}{2}\phi\begin{bmatrix}\cos(\phi)\\\sin(\phi)\end{bmatrix}\\
\norm{\vb{r_{inv}'}(\phi)} &= \frac{d_p}{2}\abs{\phi} \\
\vb{T}(\phi) &= \operatorname{sgn}(\phi) \begin{bmatrix}\cos(\phi)\\ \sin(\phi)\end{bmatrix}\\
\vb{N}(\phi) &= \operatorname{sgn}(\phi) \begin{bmatrix}-\sin(\phi)\\ \cos(\phi)\end{bmatrix} \\
\theta_t(\phi) &= \phi \\
\theta_n(\phi) &= \phi + \tfrac{\pi}{2} \\
\end{align}
$$

### Parametric Hypotroichoid
![[Pasted image 20260107124432.png]]
![[hypotroichoid.png|400]]
![[hypotrochoid.mp4]]
### base Involute
$$
\vb{r_{inv}}(\phi) =
\begin{bmatrix}
x(\phi) \\
y(\phi)
\end{bmatrix}
= \textcolor{yellow}{\tfrac{d_p}{2} \begin{bmatrix}
\cos(\phi) \\
\sin(\phi)
\end{bmatrix}}
+ \textcolor{blue}{\tfrac{d_p}{2}\phi \begin{bmatrix}
\sin(\phi) \\
-\cos(\phi)
\end{bmatrix}}
$$
### Involute shift
Confusion here:
- x direction in graph above is _up/down_ (pos: down) where the y directions is _left/right_ (pos: )
- I use $v_y=\pm r_f\tan(\alpha_t)$  to show that the vector is flipped based on which flank is drawn. + being the right and - the left flank (seen from the perspective of the gear center). Keep in mind that for a left flank we still need negative $\phi$ values instead of positive ones.
$$
\vb v = \begin{bmatrix}v_x \\ v_y\end{bmatrix} = \begin{bmatrix}
r_d - r_p \\ \pm r_f\tan(\alpha_t)
\end{bmatrix}
$$
or using $d_f = 2\cdot r_d$ and $d_p = 2\cdot r_p$
$$
\vb v = \begin{bmatrix}v_x \\ v_y\end{bmatrix} = \begin{bmatrix}
\tfrac{d_f - d_p}{2} \\
\pm\tfrac{d_f}{2}\tan(\alpha_t)
\end{bmatrix}
$$
### Rotation matrix
$$
\vb R(\theta) = \begin{bmatrix}\cos(\theta) & -\sin(\theta) \\ \sin(\theta) & \cos(\theta) \end{bmatrix}
$$
### Parametric equation
Derivation
$$
\begin{align}
\vb{r_{hypo}}(\phi) &=\vb{R}(\phi)\vb v + \vb{r_{inv}}(\phi)\\
&= \underbrace{\begin{bmatrix}\cos(\phi) & -\sin(\phi) \\ \sin(\phi) & \cos(\phi) \end{bmatrix}}_{\vb R(\phi)}
\underbrace{\begin{bmatrix}
\tfrac{d_f - d_p}{2} \\
\pm\tfrac{d_f}{2}\tan(\alpha_t)
\end{bmatrix}}_{\vb v}
+ \underbrace{\tfrac{d_p}{2} \begin{bmatrix}
\cos(\phi) \\
\sin(\phi)
\end{bmatrix}
+ \tfrac{d_p}{2}\phi \begin{bmatrix}
\sin(\phi) \\
-\cos(\phi)
\end{bmatrix}}_{\vb{r_{inv}(\phi)}}\\

&= \frac{1}{2}\left(\begin{bmatrix}\cos(\phi) & -\sin(\phi) \\ \sin(\phi) & \cos(\phi) \end{bmatrix}
\begin{bmatrix}
d_f - d_p \\
\pm d_f\tan(\alpha_t)
\end{bmatrix}
+d_p \begin{bmatrix}
\cos(\phi) \\
\sin(\phi)
\end{bmatrix}
+ d_p\phi \begin{bmatrix}
\sin(\phi) \\
-\cos(\phi)
\end{bmatrix}\\
\right)
\end{align}
$$
$$
\begin{align}
\vb{r_{hypo}}(\phi) =&
\frac{1}{2}\left(
\begin{bmatrix}
(d_f - d_p)\cos(\phi) \mp d_f\tan(\alpha_t)\sin(\phi)\\
(d_f - d_p)\sin(\phi) \pm d_f\tan(\alpha_t)\cos(\phi)
\end{bmatrix}
+ \begin{bmatrix}
d_p(\cos(\phi) + \phi\sin(\phi))\\
d_p(\sin(\phi) - \phi\cos(\phi))\\
\end{bmatrix}
\right)
\\
&=
\frac{1}{2}
\begin{bmatrix}
(d_f - d_p + d_p)\cos(\phi) + d_f\tan(\alpha_t)\sin(\phi) + d_p\phi\sin(\phi) \\
(d_f - d_p + d_p)\sin(\phi) - d_f\tan(\alpha_t)\cos(\phi) - d_p\phi\cos(\phi) \\
\end{bmatrix}
\\
&=
\frac{1}{2}
\begin{bmatrix}
d_f\cos(\phi) \mp d_f\tan(\alpha_t)\sin(\phi) + d_p\phi\sin(\phi) \\
d_f\sin(\phi) \pm d_f\tan(\alpha_t)\cos(\phi) - d_p\phi\cos(\phi) \\
\end{bmatrix}
\\
&=
\frac{1}{2}
\left(
\begin{bmatrix}
d_f\\
\pm d_f\tan(\alpha_t)\\
\end{bmatrix}
\cos(\phi)
+
\begin{bmatrix}
\mp d_f\tan(\alpha_t) \\
 d_f \\
\end{bmatrix}
\sin(\phi)
+
d_p\,\phi
\begin{bmatrix}
\sin(\phi) \\
- \cos(\phi) \\
\end{bmatrix}
\right)
\end{align}
$$
**Final result:**
Single Matrix:
$$

\vb{r_{hypo}}(\phi) 
=
\frac{1}{2}
\begin{bmatrix}
d_f\cos(\phi) \mp d_f\tan(\alpha_t)\sin(\phi) + d_p\phi\sin(\phi) \\
d_f\sin(\phi) \pm d_f\tan(\alpha_t)\cos(\phi) - d_p\phi\cos(\phi) \\
\end{bmatrix}
$$

Separated terms:
$$
\vb{r_{hypo}}(\phi) 
=
\frac{1}{2}
\left(
\begin{bmatrix}
d_f\\
\pm d_f\tan(\alpha_t)\\
\end{bmatrix}
\cos(\phi)
+
\begin{bmatrix}
\mp d_f\tan(\alpha_t) \\
 d_f \\
\end{bmatrix}
\sin(\phi)
+
d_p\,\phi
\begin{bmatrix}
\sin(\phi) \\
- \cos(\phi) \\
\end{bmatrix}
\right)
$$

Compact notation:

$$
\begin{align}
\vb{r_{hypo}}(\phi)
=
\frac{1}{2}
\left(
\vb A
\cos(\phi)
+
\vb B
\sin(\phi)
+
d_p\,\phi\;
\vb t(\phi)
\right)
\end{align}
$$
$$
\begin{align}
\vb A = 
\begin{bmatrix}
a \\ b
\end{bmatrix}
=
\begin{bmatrix}
 d_f \\
\pm d_f\tan(\alpha_t)\\
\end{bmatrix}

\quad
\quad

\vb B =
\begin{bmatrix}
-b \\ a
\end{bmatrix}
=
\begin{bmatrix}
\mp d_f\tan(\alpha_t)\\
d_f \\
\end{bmatrix}

\quad
\quad

\vb t(\phi) =
\begin{bmatrix}
\sin(\phi) \\
- \cos(\phi) \\
\end{bmatrix}

\end{align}
$$
$$
a = d_f \quad\quad b = \pm d_f\tan(\alpha_t)
$$
### Determine value of $\phi$ when hypotroichoid reaches specific diameter
Hypotroichoid equations
$$
\begin{align}
\vb{r_{hypo}}(\phi)
=
\frac{1}{2}
\left(
\begin{bmatrix}
a \\ b
\end{bmatrix}
\cos(\phi)
+
\begin{bmatrix}
-b \\ a
\end{bmatrix}
\sin(\phi)
+
d_p\,\phi\;
\begin{bmatrix}
\sin\phi \\ -\cos\phi
\end{bmatrix}
\right)
\end{align}
$$
$$
a = d_f \quad\quad b = \pm d_f\tan(\alpha_t)
$$
$$
\begin{align}
x_{inv}(\phi) &= \frac{1}{2}\left(a\cos\phi - b \sin\phi + d_p\phi\sin\phi\right) \\
y_{inv}(\phi) &= \frac{1}{2}\left(b\cos\phi + a \sin\phi - d_p\phi\cos\phi\right)
\end{align}
$$
 $d^*$ derivation

$$
\begin{align}
d^* &\stackrel{!}{=} \sqrt{x_{inv}(\phi)^2 + y_{inv}(\phi)^2} \;\;\cdot 2 \\
&= \sqrt{\frac{1}{4}\cdot \left(\left(a\cos\phi - b \sin\phi + d_p\phi\sin\phi\right)^2 + \left(b\cos\phi + a \sin\phi - d_p\phi\cos\phi\right)^2\right)} \;\;\cdot 2 \\
&= \sqrt{\left(a\cos\phi - b \sin\phi + d_p\phi\sin\phi\right)^2 + \left(b\cos\phi + a \sin\phi - d_p\phi\cos\phi\right)^2}
\end{align}
$$
$$
\begin{align}
\left(a\cos\phi - b \sin\phi + d_p\phi\sin\phi\right)^2 &= a^2\cos^2\phi + b^2\sin^2\phi + d_p^2\phi^2\sin^2\phi \\
&\phantom{=} - 2ab\cos\phi\sin\phi + 2ad_p\phi\cos\phi\sin\phi - 2bd_p\phi\sin^2\phi
\end{align}
$$

$$
\begin{align}
\left(b\cos\phi + a \sin\phi - d_p\phi\cos\phi\right)^2 &= b^2\cos^2\phi + a^2\sin^2\phi + d_p^2\phi^2\cos^2\phi \\
&\phantom{=} + 2ab\cos\phi\sin\phi - 2bd_p\phi\cos^2\phi - 2ad_p\phi\sin\phi\cos\phi
\end{align}
$$
$$
\begin{align}
d^* &= \Big[ \\
&\phantom{= [ }\big( a^2\cos^2\phi + b^2\sin^2\phi + d_p^2\phi^2\sin^2\phi \\
&\phantom{= [ }\textcolor{orange}{\cancel{- 2ab\cos\phi\sin\phi}} \textcolor{blue}{\cancel{+ 2ad_p\phi\cos\phi\sin\phi}} - 2bd_p\phi\sin^2\phi \big) + \\
&\phantom{= [ } \big( b^2\cos^2\phi + a^2\sin^2\phi + d_p^2\phi^2\cos^2\phi \\
&\phantom{= [ } \textcolor{orange}{\cancel{+ 2ab\cos\phi\sin\phi}} - 2bd_p\phi\cos^2\phi \textcolor{blue}{\cancel{- 2ad_p\phi\sin\phi\cos\phi}} \big) \\
&\phantom{= [ }\Big]^{\tfrac{1}{2}} \\
&= \sqrt{(a^2 + b^2)\cos^2\phi + (a^2 + b^2) \sin^2\phi +d_p^2\phi^2(\sin^2\phi + \cos^2\phi) - 2bd_p\phi(\sin^2+\cos^2)}\\
&= \sqrt{(a^2 + b^2)(\cos^2\phi + \sin^2\phi) +d_p^2\phi^2(\sin^2\phi + \cos^2\phi) - 2bd_p\phi(\sin^2+\cos^2)}\\
&= \sqrt{a^2 + b^2 +d_p^2\phi^2 - 2bd_p\phi}\\
\end{align}
$$
$$
\begin{align}
d^* &= \sqrt{a^2 + b^2 +d_p^2\phi^2 - 2bd_p\phi}\\
{d^*}^2 &= a^2 + b^2 +d_p^2\phi^2 - 2bd_p\phi\\
(d_p^2)\cdot\phi^2 - (2bd_p)\cdot\phi + (a^2 + b^2 - {d^*}^2)& = 0\\
\end{align}
$$
$$
ax^2+bx + c = 0 \qq{$\Longrightarrow$} x = \frac{-b \pm \sqrt{b^2 -4ac}}{2a}
$$
$$
\begin{align}
\phi(d^*) &= \frac{2bd_p \pm \sqrt{4b^2d_p^2 - 4d_p^2(a^2 + b^2 - {d^*}^2)}}{2d_p^2} \\
&= \frac{2bd_p \pm \sqrt{\cancel{4b^2d_p^2} - 4a^2d_p^2 \cancel{- 4b^2d_p^2} + 4{d^*}^2d_p^2}}{2d_p^2} \\
&= \frac{2bd_p \pm 2d_p\sqrt{- a^2 + {d^*}^2}}{2d_p^2}\\
&= \frac{b \pm \sqrt{{d^*}^2- a^2}}{d_p} \\
&= \frac{b}{d_p} \pm \sqrt{\left(\frac{d^*}{d_p}\right)^2- \left(\frac{a}{d_p}\right)^2}
\end{align}
$$
#### Inserting $a$ and $b$
$$
a = d_f \quad\quad b = \mypm d_f\tan(\alpha_t)
$$

$$
\begin{align}
\phi(d^*) &= \mypm\frac{b}{d_p} \pm \sqrt{\left(\frac{d^*}{d_p}\right)^2- \left(\frac{a}{d_p}\right)^2} \\
&= \mypm\frac{d_f}{d_p}\tan{\alpha_t} \pm \sqrt{\left(\frac{d^*}{d_p}\right)^2- \left(\frac{d_f}{d_p}\right)^2} \\
\end{align}
$$
**Right Flank:**
$$
b = \textcolor{red}{+} d_f\tan(\alpha_t)
$$
When dealing with the **right flank** the base involute rotates **clockwise**, therefore we are interested in the smaller (usually negative) value for $\phi$:
$$
\begin{align}
\phi_{right}(d^*)&= \frac{d_f}{d_p}\tan{\alpha_t} \;\mathbf{-}\; \sqrt{\left(\frac{d^*}{d_p}\right)^2- \left(\frac{d_f}{d_p}\right)^2} \\
\end{align}
$$

**Left Flank:**
$$
b = \textcolor{red}{-} d_f\tan(\alpha_t)
$$
When dealing with the **left flank** the base involute rotates **counterclockwise**, therefore we are interested in the larger (usually positive) value for $\phi$:
$$
\begin{align}
\phi_{left}(d^*)&= -\frac{d_f}{d_p}\tan{\alpha_t} \;\mathbf{+}\; \sqrt{\left(\frac{d^*}{d_p}\right)^2- \left(\frac{d_f}{d_p}\right)^2} \\
\end{align}
$$

#### Special case $d^*=d_f$:
The case of $d^* = d_f$ is interesting since this is the starting angle where one generally wants to start the involute:
$$
\begin{align}
\phi_0 = \phi(d_f) &=  \mypm\frac{d_f}{d_p}\tan{\alpha_t} \pm \sqrt{\cancel{\left(\frac{d_f}{d_p}\right)^2- \left(\frac{d_f}{d_p}\right)^2}} \\
&= \mypm\frac{d_f}{d_p}\tan{\alpha_t} \\
\end{align}
$$

**Right Flank:**
$$
b = \textcolor{red}{+} d_f\tan(\alpha_t)
$$
$$
\begin{align}
\phi_{0,right} = \phi_{right}(d_f) &= \frac{d_f}{d_p}\tan{\alpha_t} \\
\end{align}
$$

**Left Flank:**
$$
b = \textcolor{red}{-} d_f\tan(\alpha_t)
$$
$$
\begin{align}
\phi_{0,left} =\phi_{left}(d_f) &= -\frac{d_f}{d_p}\tan{\alpha_t} \\
\end{align}
$$

### Summary Hypotroichoid
$$
\begin{align}
\vb{r_{hypo}}(\phi)
=
\frac{1}{2}
\left(
\vb A
\cos(\phi)
+
\vb B
\sin(\phi)
+
d_p\,\phi\;
\vb t(\phi)
\right)
\end{align}
$$
$$
\begin{align}
\vb A = 
\begin{bmatrix}
a \\ b
\end{bmatrix}
=
\begin{bmatrix}
 d_f \\
\pm d_f\tan(\alpha_t)\\
\end{bmatrix}

\quad
\quad

\vb B =
\begin{bmatrix}
-b \\ a
\end{bmatrix}
=
\begin{bmatrix}
\mp d_f\tan(\alpha_t)\\
d_f \\
\end{bmatrix}

\quad
\quad

\vb t(\phi) =
\begin{bmatrix}
\sin(\phi) \\
- \cos(\phi) \\
\end{bmatrix}

\end{align}
$$

$$
a = d_f \quad\quad b = \mypm d_f\tan(\alpha_t)
$$

$$
\begin{align}
\phi(d^*) &= \mypm\frac{d_f}{d_p}\tan{\alpha_t} \pm \sqrt{\left(\frac{d^*}{d_p}\right)^2- \left(\frac{d_f}{d_p}\right)^2} \\
\phi_{right}(d^*)&= \frac{d_f}{d_p}\tan{\alpha_t} \;\mathbf{-}\; \sqrt{\left(\frac{d^*}{d_p}\right)^2- \left(\frac{d_f}{d_p}\right)^2} \\
\phi_{left}(d^*)&= -\frac{d_f}{d_p}\tan{\alpha_t} \;\mathbf{+}\; \sqrt{\left(\frac{d^*}{d_p}\right)^2- \left(\frac{d_f}{d_p}\right)^2} \\
\end{align}
$$
$$
\begin{align}
\phi_0 = \phi(d_f) &= \mypm\frac{d_f}{d_p}\tan{\alpha_t} \\
\end{align}
$$
**Note**: The $\mypm$ depends on which flank
- $\textcolor{red}{+}$: Right flank $\Rightarrow$ $\phi$ is monotonically decreasing ($\phi_{start} > \phi_{end}$)
	usually: $\phi_0 > 0 \quad \phi_{end} < 0$ 
- $\textcolor{red}{-}$: Left flank $\Rightarrow$ $\phi$ is monotonically increasing ($\phi_{start} < \phi_{end}$)
	usually: $\phi_0 < 0 \quad \phi_{end} > 0$ 
	
## Positioning
## Tooth thickness at base
tooth thickness at pitch circle in case of **no profile shift**
$$
s_0 = \frac{m\pi}{2}
$$
additional thickness for base can be computed from involute angle (of a positively rotating, i.e. counterclockwise, involute):
$$
\theta(d^*) = \left[\left(\frac{d^*}{d_b}\right)^2 - 1\right]^{\tfrac{1}{2}} - \arctan\left(\left[\left(\frac{d^*}{d_b}\right)^2 - 1\right]^{\tfrac{1}{2}}\right)
$$
the additional thickness is:
$$
\begin{align}
\Delta{s} &= d_b\cdot\left(\theta(d_p) - \cancelto{0}{\theta(d_b)}\right) \\
 &= d_b\;\theta(d_p) \\
&= d_b\;\left[\left(\frac{d_p}{d_b}\right)^2 - 1\right]^{\tfrac{1}{2}} - d_b\;\arctan\left(\left[\left(\frac{d_p}{d_b}\right)^2 - 1\right]^{\tfrac{1}{2}}\right) \\
\end{align}
$$
tooth width at base
$$
\begin{align}
s_b &= s_0 + \Delta s \\
&= \frac{m\pi}{2} + d_b\;\left[\left(\frac{d_p}{d_b}\right)^2 - 1\right]^{\tfrac{1}{2}} - d_b\;\arctan\left(\left[\left(\frac{d_p}{d_b}\right)^2 - 1\right]^{\tfrac{1}{2}}\right) \\
\end{align}
$$

Half the tooth angle:
$$
\begin{align}
\gamma &= \frac{s_b}{d_b} \\ 
&= \frac{m\pi}{2\,d_b} + \left[\left(\frac{d_p}{d_b}\right)^2 - 1\right]^{\tfrac{1}{2}} - \arctan\left(\left[\left(\frac{d_p}{d_b}\right)^2 - 1\right]^{\tfrac{1}{2}}\right) \\
\end{align}
$$

Rotation matrix
$$
\vb R(\theta) = \begin{bmatrix}\cos(\theta) & -\sin(\theta) \\ \sin(\theta) & \cos(\theta) \end{bmatrix}
$$
###  Involute
$$
\begin{align}
\vb{r_{inv}}(\phi) = 
\begin{bmatrix}
x(\phi) \\
y(\phi)
\end{bmatrix}
&= \tfrac{d_b}{2} \begin{bmatrix}
\cos(\phi) \\
\sin(\phi)
\end{bmatrix}
+ \tfrac{d_b}{2}\phi \begin{bmatrix}
\sin(\phi) \\
-\cos(\phi)
\end{bmatrix} \\
\end{align}
$$
The involute needs to be rotated by half the tooth angle
$$
\begin{align}
\vb{r_{inv}}(\phi) = 
\begin{bmatrix}
x(\phi) \\
y(\phi)
\end{bmatrix}
&= \tfrac{d_b}{2} \begin{bmatrix}
\cos(\phi) \\
\sin(\phi)
\end{bmatrix}
+ \tfrac{d_b}{2}\phi \begin{bmatrix}
\sin(\phi) \\
-\cos(\phi)
\end{bmatrix} \\
\end{align}
$$

The involute needs to be rotated by half the tooth angle

$$
\begin{align}
\vb{r_{inv,pos}}(\phi) &= \vb{R}(\mypm(-\gamma))\vb{r_{inv}}(\phi) \\[1ex]
&=
\begin{bmatrix}
\cos(\gamma) & \sin(\mypm\gamma) \\ -\sin(\mypm\gamma) & \cos(\gamma)
\end{bmatrix}
\left(
\tfrac{d_b}{2} \begin{bmatrix}
\cos(\phi) \\
\sin(\phi)
\end{bmatrix}
+ \tfrac{d_b}{2}\phi \begin{bmatrix}
\sin(\phi) \\
-\cos(\phi)
\end{bmatrix}
\right) \\[1ex]
&=
\frac{d_b}{2}
\begin{bmatrix}
\cos(\gamma) & \sin(\mypm\gamma) \\ -\sin(\mypm\gamma) & \cos(\gamma)
\end{bmatrix}
\begin{bmatrix}
\cos(\phi) +\phi \sin(\phi)\\
\sin(\phi) -\phi \cos(\phi))
\end{bmatrix} \\[1ex]
&=
\frac{d_b}{2}
\begin{bmatrix}
\phantom{-}\cos(\myppm\gamma)\;\cos(\phi) +\cos(\myppm\gamma)\;\phi \sin(\phi) + \sin(\mypm\gamma)\;\sin(\phi) - \sin(\mypm\gamma)\;\phi\cos(\phi)\\

-\sin(\mypm\gamma)\;\cos(\phi) - \sin(\mypm\gamma)\;\phi \sin(\phi) + \cos(\myppm\gamma)\;\sin(\phi) - \cos(\myppm\gamma)\;\phi\cos(\phi)\\
\end{bmatrix}
\end{align}
$$
### Hypotroichoid
$$
\begin{align}
\vb{r_{hypo}}(\phi)
=
\frac{1}{2}
\left(
\vb A
\cos(\phi)
+
\vb B
\sin(\phi)
+
d_p\,\phi\;
\vb t(\phi)
\right)
\end{align}
$$

$$
\begin{align}
\vb A = 
\begin{bmatrix}
a \\ b
\end{bmatrix}
=
\quad
\quad

\vb B =
\begin{bmatrix}
-b \\ a
\end{bmatrix}
=
\quad
\quad

\vb t(\phi) =
\begin{bmatrix}
\sin(\phi) \\
- \cos(\phi) \\
\end{bmatrix}

\end{align}
$$

$$
a = d_f \quad\quad b = \mypm d_f\tan(\alpha_t)
$$

In the way parametric hypotroichoid is defined it needs to be rotated by half the tooth angle

$$
\begin{align}
\vb{r_{hypo,pos}}(\phi) &= \vb{R}(\mypm(-\gamma - \alpha_t)))\;\vb{r_{hypo}}(\phi) \\[1ex]
&=
\begin{bmatrix}
\cos(\gamma+\alpha_t) & \sin(\mypm(\gamma+\alpha_t)) \\ -\sin(\mypm(\gamma+\alpha_t)) & \cos(\gamma+\alpha_t)
\end{bmatrix}
\;
\frac{1}{2}
\left(
\vb A
\cos(\phi)
+
\vb B
\sin(\phi)
+
d_p\,\phi\;
\vb t(\phi)
\right) \\[1ex]
&=
\frac{1}{2}
\begin{bmatrix}
\cos(\gamma+\alpha_t) & \sin(\mypm(\gamma+\alpha_t)) \\ -\sin(\mypm(\gamma+\alpha_t)) & \cos(\gamma+\alpha_t)
\end{bmatrix}
\left(
\begin{bmatrix}
a \\ b
\end{bmatrix}
\cos(\phi)
+
\begin{bmatrix}
-b \\ a
\end{bmatrix}
\sin(\phi)
+
d_p\,\phi\;
\begin{bmatrix}
\sin(\phi) \\ -\cos(\phi)
\end{bmatrix}
\right)
\\[1ex]
&= \frac{1}{2}
\begin{bmatrix}
\cos(\gamma+\alpha_t) & \sin(\mypm(\gamma+\alpha_t)) \\ -\sin(\mypm(\gamma+\alpha_t)) & \cos(\gamma+\alpha_t)
\end{bmatrix}
\begin{bmatrix}
a\cos(\phi) - b \sin(\phi) + d_p\,\phi\sin(\phi) \\
b\cos(\phi) + a \sin(\phi) - d_p\,\phi\cos(\phi)
\end{bmatrix}\\[1ex]
&=
\frac{1}{2}\bigg[
\begin{array}{cc}
\phantom{-}a\cos(\myppm\;\gamma+\alpha_t\;)\;\cos(\phi) 
- b\cos(\myppm\;\gamma+\alpha_t\;)\;\sin(\phi)
+ d_p\cos(\myppm\;\gamma+\alpha_t\;)\;\phi\sin(\phi)\dots
\\
-a\sin(\mypm(\gamma+\alpha_t))\;\cos(\phi)
+b\sin(\mypm(\gamma+\alpha_t))\;\sin(\phi)
- d_p\sin(\mypm(\gamma+\alpha_t))\;\phi\sin(\phi)\dots
\end{array}
\\
&\phantom{= \frac{1}{2}\bigg[}
\begin{array}{cc}
\hspace{1em}\dots + b\sin(\mypm(\gamma+\alpha_t))\;\cos(\phi) 
+ a\sin(\mypm(\gamma+\alpha_t))\;\sin(\phi)
- d_p\sin(\mypm(\gamma+\alpha_t))\;\phi\cos(\phi)
\\
\hspace{1em}\dots+ b\cos(\myppm\;\gamma+\alpha_t\;)\;\cos(\phi) 
+ a\cos(\myppm\;\gamma+\alpha_t\;)\;\sin(\phi)
- d_p\cos(\myppm\;\gamma+\alpha_t\;)\;\phi\cos(\phi)
\end{array}
\bigg] \\[1ex]
\end{align}
$$

$$
\begin{align}
\vb{r_{inv}}(\phi) = 
\begin{bmatrix}
x(\phi) \\
y(\phi)
\end{bmatrix}
&= \tfrac{d_b}{2} \begin{bmatrix}
\cos(\phi) \\
\sin(\phi)
\end{bmatrix}
+ \tfrac{d_b}{2}\phi \begin{bmatrix}
\sin(\phi) \\
-\cos(\phi)
\end{bmatrix} \\
\end{align}
$$

The involute needs to be rotated by half the tooth angle

## Intersections
### Intersection between left and right involute
$$
\begin{align}
\vb{r_{inv,pos,right}}(\phi) &= \vb{R}(-\gamma)\;\vb{r_{inv}}(\phi) \\[1ex]
&=
\frac{d_b}{2}
\begin{bmatrix}
\phantom{-}\cos(\gamma)\;\cos(\phi) +\cos(\gamma)\;\phi \sin(\phi) + \sin(\gamma)\;\sin(\phi) - \sin(\gamma)\;\phi\cos(\phi)\\

-\sin(\gamma)\;\cos(\phi) - \sin(\gamma)\;\phi \sin(\phi) + \cos(\gamma)\;\sin(\phi) - \cos(\gamma)\;\phi\cos(\phi)\\
\end{bmatrix}
\end{align}
$$

$$
\begin{align}
\vb{r_{inv,pos,left}}(\phi) &= \vb{R}(\gamma)\;\vb{r_{inv}}(\phi) \\[1ex]
&=
\frac{d_b}{2}
\begin{bmatrix}
\phantom{-}\cos(\phantom{-}\gamma)\;\cos(\phi) +\cos(\phantom{-}\gamma)\;\phi \sin(\phi) + \sin(-\gamma)\;\sin(\phi) - \sin(-\gamma)\;\phi\cos(\phi)\\

-\sin(-\gamma)\;\cos(\phi) - \sin(-\gamma)\;\phi \sin(\phi) + \cos(\phantom{-}\gamma)\;\sin(\phi) - \cos(\phantom{-}\gamma)\;\phi\cos(\phi)\\
\end{bmatrix}
\end{align}
$$
**x:**
$$
\begin{align}
&\phantom{=}\,\;\cos(\gamma)\;\cos(\phi_r) + \cos(\gamma)\;\phi_r \sin(\phi_r) + \sin(\gamma)\;\sin(\phi_r) - \sin(\gamma)\;\phi_r\cos(\phi_r)\\

&= \cos(\gamma)\;\cos(\phi_l) +\cos(\gamma)\;\phi_l \sin(\phi_l) - \sin(\gamma)\;\sin(\phi_l) + \sin(\gamma)\;\phi_l\cos(\phi_l)\\
\end{align}
$$
**y:**
$$
\begin{align}
&\phantom{=}\,\; -\sin(\gamma)\;\cos(\phi_r) - \sin(\gamma)\;\phi_r \sin(\phi_r) + \cos(\gamma)\;\sin(\phi_r) - \cos(\gamma)\;\phi_r\cos(\phi_r)\\
&= 
\phantom{-}\sin(\gamma)\;\cos(\phi_l) + \sin(\gamma)\;\phi_l \sin(\phi_l) + \cos(\gamma)\;\sin(\phi_l) - \cos(\gamma)\;\phi_l\cos(\phi_l)\\
\end{align}
$$
#### Solution
**a) Due to the symmetry of the two cuves: $\phi_r = -\phi_l = \phi$
Proof by inserting $\phi$ into eq. x:
$$
\begin{align}
&\phantom{=}\,\;\cos(\gamma)\;\cos(\phi)_l + \cos(\gamma)\;\phi \sin(\phi) + \sin(\gamma)\;\sin(\phi) - \sin(\gamma)\;\phi\cos(\phi)\\

&= \cos(\gamma)\;\cos(\phi) + \cos(\gamma)\;\phi \sin(\phi) + \sin(\gamma)\;\sin(\phi) - \sin(\gamma)\;\phi\cos(\phi)\\
\end{align}
$$

**b) Inserting $\phi_r = -\phi_l = \phi$ into eq. y:**
$$
\begin{align}
&\phantom{=}\,\; -\sin(\gamma)\;\cos(\phi) - \sin(\gamma)\;\phi \sin(\phi) + \cos(\gamma)\;\sin(\phi) - \cos(\gamma)\;\phi\cos(\phi)\\
&= 
\phantom{-}\sin(\gamma)\;\cos(\phi) + \sin(\gamma)\;\phi \sin(\phi) - \cos(\gamma)\;\sin(\phi) + \cos(\gamma)\;\phi\cos(\phi)\\
\end{align}
$$
RHS-LHS=0 and simplify
$$
\begin{align}
2\sin(\gamma)\cos(\phi) + 2\sin(\gamma)\phi\sin(\phi) - 2\cos(\gamma)\sin(\phi) + 2\cos(\gamma)\phi\cos(\phi) &= 0\\
\sin(\gamma)\cos(\phi) + \sin(\gamma)\phi\sin(\phi) - \cos(\gamma)\sin(\phi) + \cos(\gamma)\phi\cos(\phi) &= 0\\
\sin(\gamma)\left[\cos(\phi) + \phi\sin(\phi)\right] - \cos(\gamma)\left[\sin(\phi) - \phi\cos(\phi)\right]&= 0\\
\sin(\gamma)\left[\cos(\phi) + \phi\sin(\phi)\right] &= \cos(\gamma)\left[\sin(\phi) - \phi\cos(\phi)\right]\\
\tan(\gamma) &= \frac{\sin(\phi) - \phi\cos(\phi)}{\cos(\phi) + \phi\sin(\phi)}\\
\frac{\sin(\phi) - \phi\cos(\phi)}{\cos(\phi) + \phi\sin(\phi)} - \tan(\gamma) &=0\\
\end{align}
$$
#### Newton Raphson
This means we need to solve:
$$
\begin{align}
F(\phi) = \frac{\sin(\phi) - \phi\cos(\phi)}{\cos(\phi) + \phi\sin(\phi)} - \tan(\gamma) &=0\\
\end{align}
$$
This can be solved using Newton-Raphson, however first the derivative $F'(\phi)$ needs to be computed

**Derivative of of $F(x)$**
_a) split into components_
$$
F(\phi) = \frac{u(\phi)}{v(\phi)} - C
$$
$$
\begin{align}
u(\phi) &= \sin(\phi) - \phi\cos(\phi)\\
v(\phi) &= \cos(\phi) + \phi\sin(\phi) \\
C &= \tan(\gamma)
\end{align}
$$
_b) compute $u'(\phi)$
$$
\begin{align}
u'(\phi) &= \cos(\phi) - \cos(\phi) +\phi\sin(\phi)\\
&=\phi\sin(\phi)
\end{align}
$$
_c) compute $v'(\phi)$_
$$
\begin{align}
v'(\phi) &= -\sin(\phi) + \sin(\phi) + \phi\cos(\phi)\\
&=\phi\cos(\phi)
\end{align}
$$
_d) Apply quotient rule_
$$
\dv{}{\phi}\left[\frac{u(\phi)}{v(\phi)}\right] = \frac{u'v - uv'}{v^2}
$$

$$
\begin{align}
\dv{F(\phi)}{\phi} &= \frac{u'v - uv'}{v^2} \\

&= \frac{\phi\sin(\phi)\cdot\left[\cos(\phi) + \phi\sin(\phi)\right] - \phi\cos(\phi)\cdot\left[\sin(\phi) - \phi\cos(\phi)\right]}
{\left[\cos(\phi) + \phi\sin(\phi)\right]^2}\\[1ex]

&= \frac{\cancel{\phi\sin(\phi)\cos(\phi)} + \phi^2\sin^2(\phi) \cancel{ -\phi\sin(\phi)\cos(\phi)} + \phi^2\cos^2(\phi)}
{\left[\cos(\phi) + \phi\sin(\phi)\right]^2}\\[1ex]

&= \frac{\phi^2\cancelto{1}{\left[\sin^2(\phi) + \cos^2(\phi)\right]}}
{\left[\cos(\phi) + \phi\sin(\phi)\right]^2}\\[1ex]
&= \frac{\phi^2}
{\left[\cos(\phi) + \phi\sin(\phi)\right]^2}\\[1ex]
\end{align}
$$
_e) Formulate Newton-Raphson_
$$
\begin{align}
\phi_{n+1} &= \phi_n - \frac{F(\phi_n)}{F'(\phi_n)} \\
 &= \phi_n - \left(\frac{\sin(\phi_n) - \phi_n\cos(\phi_n)}{\cos(\phi_n) + \phi_n\sin(\phi_n)} - \tan(\gamma)\right) \frac{\left[\cos(\phi_n) + \phi_n\sin(\phi_n)\right]^2}{\phi_n^2}\\[1ex]
 
 &= \phi_n - \frac{\cos(\phi_n) + \phi_n\sin(\phi_n)}{\phi_n^2}\left(\sin(\phi_n) - \phi_n\cos(\phi_n) - \tan(\gamma)\;\left[\cos(\phi_n) + \phi_n\sin(\phi_n)\right]\right)\\[1ex]
\end{align}
$$
or more presentable
$$
\begin{align}
\phi_{n+1} &= \phi_n - \frac{a}{\phi_n^2}\left(b - \tan(\gamma)\;a\right)\\[1ex]
\end{align}
$$
$$
a =\cos(\phi_n) + \phi_n\sin(\phi_n) \qq{and} b=\sin(\phi_n) - \phi_n\cos(\phi_n)
$$

### Intersection between involute and hypotroichoid

$$
\begin{align}
\vb{r_{inv}}(\phi) = 
\begin{bmatrix}
x(\phi) \\
y(\phi)
\end{bmatrix}
&= \tfrac{d_b}{2} \begin{bmatrix}
\cos(\phi) \\
\sin(\phi)
\end{bmatrix}
+ \tfrac{d_b}{2}\phi \begin{bmatrix}
\sin(\phi) \\
-\cos(\phi)
\end{bmatrix} \\
\end{align}
$$
$$
\begin{align}
\vb{r_{hypo}}(\phi)
=
\frac{1}{2}
\left(
\begin{bmatrix}
a \\ b
\end{bmatrix}
\cos(\phi)
+
\begin{bmatrix}
-b \\ a
\end{bmatrix}
\sin(\phi)
+
d_p\,\phi\;
\begin{bmatrix}
\sin\phi \\ -\cos\phi
\end{bmatrix}
\right)
\end{align}
$$
$$
a = d_f \quad\quad b = \mypm d_f\tan(\alpha_t)
$$
The involute needs to be rotated by $\mypm(-\gamma)$ and the hypotroichoid needs to be rotated by $\mypm(-\gamma - \alpha_t)$. When finding the intersection this is equivalent to rotating the involute by $\mypm \alpha_t$ . 
$$
\begin{align}
\vb{r_{inv,pos}}(\phi) &= \vb{R}(\mypm\alpha_t))\;\vb{r_{inv}}(\phi) \\[1ex]
&=
\frac{d_b}{2} \begin{bmatrix}
\cos(\alpha_t) & -\sin(\mypm\alpha_t) \\ \sin(\mypm\alpha_t) & \cos(\alpha_t)
\end{bmatrix}
\begin{bmatrix}
\cos(\phi) + \phi\sin(\phi)\\
\sin(\phi) -\phi \cos(\phi)
\end{bmatrix}
\\
&=\frac{d_b}{2}\begin{bmatrix}
\cos(\alpha_t)\cos(\phi) +\cos(\alpha_t)\phi\sin(\phi) -\sin(\mypm\alpha_t)\sin(\phi) +\sin(\mypm\alpha_t)\phi\cos(\phi) \\
\sin(\mypm\alpha_t)\cos(\phi) +\sin(\mypm\alpha_t)\phi\sin(\phi) + \cos(\alpha_t)\sin(\phi) -\cos(\alpha_t)\phi\cos(\phi) \\
\end{bmatrix}
\end{align}
$$
shorthand
$$
\begin{align}
\vb{r_{inv,pos}}(\phi) &= \vb{R}(\mypm\alpha_t))\;\vb{r_{inv}}(\phi) \\[1ex]
&=
\frac{d_b}{2} \begin{bmatrix}
c & -d \\ d & c
\end{bmatrix}
\begin{bmatrix}
\cos(\phi) + \phi\sin(\phi)\\
\sin(\phi) -\phi \cos(\phi)
\end{bmatrix}
\\
&=\frac{d_b}{2}\begin{bmatrix}
c\cos(\phi) +c\phi\sin(\phi) -d\sin(\phi) +d\phi\cos(\phi) \\
d\cos(\phi) +d\phi\sin(\phi) + c\sin(\phi) -c\phi\cos(\phi) \\
\end{bmatrix}
\end{align}
$$
$$
c = \cos(\alpha_t) \qq{,} d = \sin(\mypm\alpha_t)
$$
Finding intersection:

$$
\begin{align}
\vb{r_{inv,pos}}(\phi_i) &= \vb{r_{hypo}}(\phi_h)
\\
\frac{d_b}{2}\begin{bmatrix}
c\cos(\phi_i) +c\phi_i\sin(\phi_i) -d\sin(\phi_i) +d\phi_i\cos(\phi_i) \\
d\cos(\phi_i) +d\phi_i\sin(\phi_i) + c\sin(\phi_i) -c\phi_i\cos(\phi_i) \\
\end{bmatrix} &=
\frac{1}{2}\left(\begin{bmatrix}a \\ b\end{bmatrix}\cos\phi_h + \begin{bmatrix} -b \\ a\end{bmatrix}\sin\phi_h + d_p\phi_h\begin{bmatrix} \sin\phi_h \\ - \cos\phi_h\end{bmatrix}\right)
\\
d_b\begin{bmatrix}
c\cos(\phi_i) +c\phi_i\sin(\phi_i) -d\sin(\phi_i) +d\phi_i\cos(\phi_i) \\
d\cos(\phi_i) +d\phi_i\sin(\phi_i) + c\sin(\phi_i) -c\phi_i\cos(\phi_i) \\
\end{bmatrix} &=
\begin{bmatrix}a \cos(\phi_h) - b\sin(\phi_h)+ d_p\phi_h\sin(\phi_h)
\\ b\cos(\phi_h) + a \sin(\phi_h) - d_p\phi_h\cos(\phi_h)\end{bmatrix}
\end{align}
$$
**x:**
$$
\begin{align}
f_1 &= d_bc\cos(\phi_i) + d_bc\phi_i\sin(\phi_i) - d_bd\sin(\phi_i) + d_bd\phi_i\cos(\phi_i)\\
&\phantom{=}- a\cos(\phi_h) + b\sin(\phi_h) - d_p\phi_h\sin(\phi_h)\\
&= 0
\end{align}
$$

**y:**
$$
\begin{align}
f_2 &= d_bd\cos(\phi_i) + d_bd\phi_i\sin(\phi_i) + d_bc\sin(\phi_i) -d_bc\phi_i\cos(\phi_i)\\ 
&\phantom{=}-b\cos(\phi_h) - a \sin(\phi_h) + d_p\phi_h\cos(\phi_h) \\
&= 0
\end{align}
$$

#### Newton-Raphson
$$
\begin{align}
x_1 = \phi_i \qq{,} x_2=\phi_h \\[3ex]
\vb J = \begin{bmatrix}\pdv{f_1}{x_1} & \pdv{f_1}{x_2} \\ \pdv{f_2}{x_1} & \pdv{f_2}{x_2}\end{bmatrix}
\end{align}
$$

$$
\begin{align}
f_1 &= d_bc\cos(x_1) + d_bcx_1\sin(x_1) - d_bd\sin(x_1) + d_bdx_1\cos(x_1)\\
&\phantom{=}- a\cos(x_2) + b\sin(x_2) - d_px_2\sin(x_2)\\[1ex]
f_2 &= d_bd\cos(x_1) + d_bdx_1\sin(x_1) + d_bc\sin(x_1) -d_bcx_1\cos(x_1)\\ 
&\phantom{=}-b\cos(x_2) - a \sin(x_2) + d_px_2\cos(x_2) \\
\end{align}
$$
$$
\begin{align}
\pdv{f_1}{x_1} &= \cancel{-d_bc\sin(x_1) + d_bc\sin(x_1)} + d_bcx_1\cos(x_1) \cancel{- d_bd\cos(x_1) + d_bd\cos(x_1)} - d_bdx_1\sin(x_1)\\
&= d_bcx_1\cos(x_1) - d_bdx_1\sin(x_1)\\
&= d_bx_1[c\cos(x_1) - d\sin(x_1)]\\
\pdv{f_1}{x_2} &= a\sin x_2 + b\cos x_2 - d_p \sin x_2 - d_px_2 \cos x_2 \\
\pdv{f_2}{x_1} &= \cancel{-d_bd\sin(x_1) + d_bd\sin(x_1)} + d_bdx_1\cos(x_1) \cancel{+ db_c\cos(x_1) - d_bc\cos(x_1)} + d_bcx_1\sin(x_1)\\
&= d_bdx_1\cos(x_1) + d_bcx_1\sin(x_1)\\
&= d_bx_1[d\cos(x_1) + c\sin(x_1)]\\
\pdv{f_2}{x_2} &= b\sin x_2 - a\cos x_2 + d_p\cos x_2 - d_px_2\sin x_2\\
\end{align}
$$
$$
\begin{align}
\vb J = \begin{bmatrix}
d_bx_1[c\cos x_1 - d\sin x_1] & a\sin x_2 + b\cos x_2 - d_p \sin x_2 - d_px_2 \cos x_2\\
d_bx_1[d\cos x_1 + c\sin x_1] & b\sin x_2+a\cos x_2 + d_p\cos x_2 - d_px_2\sin x_2 \\
\end{bmatrix}
\end{align}
$$
Recalling the inverse of a 2D matrix:
$$
\begin{align}
\vb A^{-1} = \frac{1}{ac -bd}\begin{bmatrix} d & -c \\ -b & a\end{bmatrix}
\vb J^{-1} = \frac{1}{-d_bx_1 -bd}\begin{bmatrix} d & -b \\ -c & a\end{bmatrix}
\end{align}
$$
Putting it all together:
$$
\begin{align}
f_1 &= d_bc\cos(x_1) + d_bcx_1\sin(x_1) - d_bd\sin(x_1) + d_bdx_1\cos(x_1)\\
&\phantom{=}- a\cos(x_2) + b\sin(x_2) - d_px_2\sin(x_2)\\[1ex]
f_2 &= d_bd\cos(x_1) + d_bdx_1\sin(x_1) + d_bc\sin(x_1) -d_bcx_1\cos(x_1)\\ 
&\phantom{=}-b\cos(x_2) - a \sin(x_2) + d_px_2\cos(x_2) \\
\end{align}
$$
$$
\begin{align}
\vb {J^{-1}} &= \frac{1}{J_{11}J_{22} - J_{12}J_{21}} \begin{bmatrix} J_{22} & - J_{12} \\ -J_{21} & J_{11} \end{bmatrix}\\[2ex]
J_{11} &= d_bx_1[c\cos x_1 - d\sin x_1] \\
J_{12} &= a\sin x_2 + b\cos x_2 - d_p \sin x_2 - d_px_2 \cos x_2  \\
J_{21} &= d_bx_1[d\cos x_1 + c\sin x_1] \\
J_{22} &= b\sin x_2 - a\cos x_2 + d_p\cos x_2 - d_px_2\sin x_2 \\

\end{align}
$$
$$
a = d_f \qq{,} b = \mypm d_f\tan(\alpha_t) \qq{,}c = \cos(\alpha_t) \qq{,} d = \sin(\mypm\alpha_t)
$$
where the $\textcolor{red}{+}$ refers to the right flank and and $\textcolor{red}{-}$ refers to the left flank (use starting $\phi_0$ near where the intersection is, for e.g. at $d_p$, as there are multiple intersections)

**Newton-Raphson Itteration:**
$$
\begin{align}
\begin{bmatrix}
x_1 \\ x_2
\end{bmatrix}^{(k+1)}
= 
\begin{bmatrix}
x_1 \\ x_2
\end{bmatrix}^{(k)}
- \vb{J^{-1}} \cdot \begin{bmatrix} f_1 \\ f_2 \end{bmatrix}
\end{align}
$$
