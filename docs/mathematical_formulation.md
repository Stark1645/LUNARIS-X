# LUNARIS-X (SIH26166): Comprehensive Mathematical Formulation & Scientific Derivations

**Project Title**: Multi-Modal, Sun Angle & Scale-Invariant Lunar Image Registration Platform  
**Problem Statement ID**: SIH26166 (ISRO / SAC / Department of Space)  
**Document Status**: Official Mathematical & Algorithmic Reference Specification  

---

## Executive Overview

This document provides the complete, rigorous mathematical foundation for **LUNARIS-X**. It details the governing physical equations, frequency-domain transformations, spatial statistics, optimization theorems, and error formulations that distinguish this platform from conventional computer vision matchers.

```
+===================================================================================================+
|                               MATHEMATICAL PIPELINE TAXONOMY                                      |
+===================================================================================================+
|  1. Photometry & Gradients    : Non-Lambertian Hapke Scattering & Shadow Vector Inversion         |
|  2. Frequency Representation  : 2D Multi-Orientation Log-Gabor Phase Congruency (PC)             |
|  3. Hierarchical Scale Bridge : Dyadic Gaussian Octave Scaling across 1:18+ Disparities           |
|  4. Spatial Uniformity        : 16-Bin Quad-Tree Discretization & Gini Dispersion Index (G_k)     |
|  5. Sub-Pixel Precision       : 2D Parabolic Taylor Series Expansion (delta = -H^-1 g)            |
|  6. Geometric Stabilization   : Matrix Condition Number Stability & Dynamic Projectivity Models   |
|  7. Evaluation Metrology      : Inlier Reprojection Residuals, SPA@0.5px, and Ground-Truth RMSE   |
+===================================================================================================+
```

---

## 1. Lunar Photometric Physics & Gradient Failure Modes

### 1.1 Non-Atmospheric Photometric Scattering (Hapke Model)
Unlike Earth observation imagery, where atmospheric Rayleigh and aerosol scattering produce diffuse ambient skylight, the lunar surface resides in a hard vacuum ($P < 10^{-12}\text{ torr}$). Radiometric surface reflectance $r(i, e, \alpha)$ is governed by Hapke's bidirectional reflectance model:

$$r(i, e, \alpha) = \frac{w}{4\pi} \frac{\mu_0}{\mu_0 + \mu} \left[ (1 + B(\alpha)) P(\alpha) + H(\mu_0) H(\mu) - 1 \right] S(i, e, \alpha, \bar{\theta})$$

Where:
* $i$ = Solar incidence angle ($\mu_0 = \cos i$)
* $e$ = Emission angle ($\mu = \cos e$)
* $\alpha$ = Phase angle between illumination and view vector
* $w$ = Single-scattering albedo of lunar regolith
* $B(\alpha)$ = Opposition surge effect function
* $P(\alpha)$ = Particle phase scattering function
* $H(\mu)$ = Chandrasekhar isotropic scattering function: $H(x) \approx \frac{1 + 2x}{1 + 2x\sqrt{1 - w}}$
* $S(i, e, \alpha, \bar{\theta})$ = Macroscopic surface roughness correction factor

### 1.2 Mathematical Derivation of SIFT / Gradient Failure
Standard intensity-based detectors (SIFT, SURF, ORB, AKAZE) construct orientation histograms based on local intensity gradients:

$$\nabla I(x, y) = \begin{bmatrix} I_x \\ I_y \end{bmatrix} = \begin{bmatrix} \frac{\partial I}{\partial x} \\ \frac{\partial I}{\partial y} \end{bmatrix}, \quad \theta(x, y) = \arctan\left(\frac{I_y}{I_x}\right)$$

When the solar azimuth shifts by $\Delta\phi_\odot \approx 180^\circ$ between orbital passes (e.g. morning vs. afternoon observations):
1. The illuminated crater wall switches from the eastern flank to the western flank.
2. The cast shadow switches from the western floor to the eastern floor.
3. The gradient vector across every crater boundary undergoes sign inversion:

$$\nabla I_{\text{afternoon}}(\mathbf{x}) \approx -\nabla I_{\text{morning}}(\mathbf{x})$$

The corresponding orientation shifts by exactly $\pi$ radians ($180^\circ$):

$$\theta_{\text{afternoon}}(\mathbf{x}) = \arctan\left(\frac{-I_y}{-I_x}\right) = \theta_{\text{morning}}(\mathbf{x}) \pm \pi$$

Consequently:
* SIFT descriptor feature vectors flip bins, dropping Euclidean distance below match thresholds.
* Keypoints that do match correlate opposing sides of the crater rather than identical surface landmarks, inducing catastrophic reprojection errors ($\text{RMSE} > 300\text{ px}$).

---

## 2. Frequency-Domain Structural Phase Congruency

To achieve complete illumination invariance, LUNARIS-X bypasses intensity gradients entirely, extracting structural morphology via frequency-phase alignment.

### 2.1 1D and 2D Log-Gabor Filter Bank
Standard Gabor filters suffer from a non-zero DC component at wider bandwidths. We employ logarithmic Gabor transfer functions which are Gaussian on a logarithmic frequency scale:

$$G(\omega) = \exp\left( -\frac{\left(\ln(\omega / \omega_0)\right)^2}{2 \left(\ln(\kappa / \omega_0)\right)^2} \right)$$

Where:
* $\omega_0$ = Center frequency of the filter
* $\kappa / \omega_0$ = Fractional bandwidth parameter (set to $0.55$, giving bandwidth $\approx 2$ octaves)

In 2D spatial frequency $(\rho, \theta)$, the filter bank across scale $n$ and orientation $o$ is formulated as:

$$LG_{n, o}(\rho, \theta) = \exp\left( -\frac{\left(\ln(\rho / \rho_n)\right)^2}{2 \sigma_\rho^2} \right) \cdot \exp\left( -\frac{(\theta - \theta_o)^2}{2 \sigma_\theta^2} \right)$$

Where:
* $\rho_n = \frac{1}{\lambda_n}$, with geometric octave scaling $\lambda_n = \lambda_{\min} \cdot s^{n-1}$ for scales $n \in \{1, \dots, N_s\}$
* $\theta_o = \frac{(o - 1)\pi}{N_o}$ for orientations $o \in \{1, \dots, N_o\}$ (configured with $N_s = 4$ scales, $N_o = 6$ orientations)

### 2.2 Phase Congruency Formulation
The image is convolved with the even-symmetric (cosine) component $M_{no}^e$ and odd-symmetric (sine) component $M_{no}^o$ of the Log-Gabor filter:

$$[e_{no}(x, y), o_{no}(x, y)] = \left[ I(x, y) \circledast M_{no}^e, \; I(x, y) \circledast M_{no}^o \right]$$

The local amplitude $A_{no}(x, y)$ and local phase $\phi_{no}(x, y)$ are:

$$A_{no}(x, y) = \sqrt{e_{no}^2(x, y) + o_{no}^2(x, y)}, \quad \phi_{no}(x, y) = \arctan\left(\frac{o_{no}(x, y)}{e_{no}(x, y)}\right)$$

Total local energy $E_o(x, y)$ across scales at orientation $o$ is computed as:

$$E_o(x, y) = \sqrt{\left( \sum_n e_{no}(x, y) \right)^2 + \left( \sum_n o_{no}(x, y) \right)^2}$$

Phase Congruency $PC(x, y)$ is then defined as the ratio of local energy to total amplitude sum, incorporating noise thresholding $T_o$ and frequency spread weighting $W_o(x, y)$:

$$PC(x, y) = \frac{\sum_o \sum_n W_o(x, y) \left\lfloor A_{no}(x, y) \Delta\Phi_{no}(x, y) - T_o \right\rfloor}{\sum_o \sum_n A_{no}(x, y) + \epsilon}$$

Where:
* $\lfloor \cdot \rfloor$ denotes soft thresholding ($\lfloor z \rfloor = z$ if $z > 0$, else $0$).
* $\Delta\Phi_{no}(x, y) = \cos(\phi_{no}(x, y) - \bar{\phi}_o(x, y)) - |\sin(\phi_{no}(x, y) - \bar{\phi}_o(x, y))|$.
* Noise threshold $T_o = \mu_{E_o} + k_{\text{noise}} \cdot \sigma_{E_o}$, derived from the Rayleigh noise distribution of the lowest octave filter response.
* $PC(x, y) \in [0.0, 1.0]$ is dimensionless and strictly invariant to intensity scaling, lighting direction, and contrast inversion.

### 2.3 Maximum Index Map (MIM) Construction
To preserve directional texture without relying on intensity gradients, the Maximum Index Map assigns each pixel the orientation index of maximum phase response:

$$MIM(x, y) = \arg\max_{o \in \{1, \dots, N_o\}} PC_o(x, y)$$

### 2.4 Shadow-Boundary Edge Suppression
To prevent moving shadow edges from registering as static geological features, we attenuate $PC(x, y)$ by the illumination shadow gradient divergence:

$$w_{\text{shadow}}(x, y) = 1.0 - \exp\left( -\frac{\|\nabla I_{\text{norm}}(x, y)\|^2}{2 \sigma_{\text{shadow}}^2} \right) \cdot \mathbb{I}_{\text{shadow}}(x, y)$$

$$PC_{\text{morph}}(x, y) = PC(x, y) \cdot w_{\text{shadow}}(x, y)$$

This suppresses moving cast shadow penumbras while isolating invariant physical crater rims.

---

## 3. Hierarchical Multi-Scale Pyramid Scale Bridge

### 3.1 Scale Disparity Formulation
Let $\text{GSD}_{\text{src}}$ and $\text{GSD}_{\text{ref}}$ denote the Ground Sample Distance (meters per pixel) of the source (OHRC) and reference (TMC-2) observations:

$$S = \frac{\text{GSD}_{\text{ref}}}{\text{GSD}_{\text{src}}} = \frac{5.00\text{ m/px}}{0.28\text{ m/px}} \approx 17.86$$

Classical feature detectors degrade when $S > 3.5$. To span $S \approx 18$, we construct a dyadic multi-scale Gaussian-Laplacian octave pyramid.

### 3.2 Octave Scale Decomposition
For the higher-resolution observation $\mathcal{I}_{\text{high}}$ (OHRC):

$$\mathcal{O}_k(x, y) = \left[ \mathcal{I}_{\text{high}} \circledast G(2^k \sigma_0) \right] \downarrow_{2^k}, \quad k \in \{0, 1, \dots, K\}$$

Where:
* $K = \lceil \log_2(S) \rceil = \lceil \log_2(17.86) \rceil = 5$ octaves.
* Downsampling operator $\downarrow_{2^k}$ uses area interpolation (anti-aliasing integration over $2^k \times 2^k$ pixel blocks).
* At octave $K$, the effective resolution matches the reference frame: $\text{GSD}(\mathcal{O}_K) \approx \text{GSD}_{\text{ref}}$.

### 3.3 Hierarchical Coordinate Up-Propagation
Features detected at octave $K$ with coordinates $\mathbf{x}^{(K)} = [u_K, v_K]^T$ are recursively mapped back to native sensor coordinates:

$$\mathbf{x}_{\text{native}}^{(0)} = 2^K \cdot \mathbf{x}^{(K)} + \sum_{j=0}^{K-1} 2^j \cdot \delta_j$$

Where $\delta_j$ represents local sub-pixel relaxation offsets computed at each octave level.

---

## 4. Spatial Uniformity & The Keypoint Gini Filter

### 4.1 Quad-Tree Spatial Discretization
To prevent geometric estimators from overfitting to clusters of points on a single prominent crater, the image domain $\Omega = [0, W] \times [0, H]$ is partitioned into a uniform $M \times M$ grid of spatial cells (configured as $M = 4$, yielding $K = 16$ spatial bins):

$$B_{p, q} = \left[ (p-1)\frac{W}{M}, \; p\frac{W}{M} \right) \times \left[ (q-1)\frac{H}{M}, \; q\frac{H}{M} \right), \quad p, q \in \{1, \dots, M\}$$

### 4.2 Bin Inlier Capacity Clamping
Let $\mathcal{P}_{p,q} = \{ \mathbf{x}_i \mid \mathbf{x}_i \in B_{p, q} \}$ denote the set of inlier correspondences falling into bin $(p, q)$, with count $c_{p, q} = |\mathcal{P}_{p,q}|$.

To eliminate clumping, each bin is capped at a maximum capacity $C_{\max} = 25$ points, retaining only the highest-confidence matches based on Lowe ratio margin:

$$\mathcal{P}_{p, q}^* = \arg\max_{\mathcal{S} \subset \mathcal{P}_{p, q}, |\mathcal{S}| \le C_{\max}} \sum_{\mathbf{x} \in \mathcal{S}} (1.0 - \text{ratio}(\mathbf{x}))$$

### 4.3 Discrete Spatial Gini Coefficient ($G_k$)
The spatial dispersion of verified correspondences is quantified by the discrete Gini coefficient across all $K = M^2$ bins:

$$G_k = \frac{\sum_{i=1}^K \sum_{j=1}^K |c_i - c_j|}{2 K \sum_{i=1}^K c_i}$$

Properties:
* $G_k \to 0.0$: Perfect uniform distribution across the entire lunar frame (ideal for unconstrained homography stability).
* $G_k \to 1.0$: Severe pathological clumping (all points clustered in a single bin).

### 4.4 Objective Quality Thresholds
$$Q(G_k) = \begin{cases} 
\text{GOOD} & \text{if } G_k < 0.35 \\
\text{ACCEPTABLE} & \text{if } 0.35 \le G_k \le 0.65 \\
\text{POOR (Degenerate Clump)} & \text{if } G_k > 0.65 
\end{cases}$$

---

## 5. Continuous 2D Parabolic Taylor Sub-Pixel Refinement

Integer-grid feature detection introduces discretization truncation error ($\pm 0.5\text{ px}$). To achieve sub-pixel accuracy ($\text{RMSE} < 0.5\text{ px}$), we apply 2D quadratic Taylor surface fitting on local correlation neighborhoods.

### 5.1 Local Correlation Patch
For each verified inlier pair $(\mathbf{x}_{\text{src}}, \mathbf{x}_{\text{ref}})$, a $(2W+1) \times (2W+1)$ patch (with $W = 5$) is extracted from the reference image around integer coordinate $(u_0, v_0)$.

The Normalized Cross-Correlation (NCC) surface $C(u, v)$ over shift neighborhood $(u, v) \in \{-W, \dots, W\}^2$ is:

$$C(u, v) = \frac{\sum_{x, y} \left(I_{\text{src}}(x, y) - \bar{I}_{\text{src}}\right) \left(I_{\text{ref}}(x+u, y+v) - \bar{I}_{\text{ref}}\right)}{\sqrt{\sum_{x, y} \left(I_{\text{src}}(x, y) - \bar{I}_{\text{src}}\right)^2 \sum_{x, y} \left(I_{\text{ref}}(x+u, y+v) - \bar{I}_{\text{ref}}\right)^2}}$$

### 5.2 2D Quadratic Taylor Expansion
The continuous correlation surface around discrete peak $\mathbf{x}_0 = (u_0, v_0)$ is approximated by a second-order Taylor polynomial:

$$C(\mathbf{x}_0 + \delta) \approx C(\mathbf{x}_0) + \mathbf{g}^T \delta + \frac{1}{2} \delta^T \mathbf{H} \delta$$

Where:
* $\delta = [\Delta u, \Delta v]^T$ is the sub-pixel displacement vector.
* $\mathbf{g}$ is the discrete gradient vector:

$$\mathbf{g} = \begin{bmatrix} \frac{\partial C}{\partial u} \\ \frac{\partial C}{\partial v} \end{bmatrix} = \begin{bmatrix} \frac{C(1, 0) - C(-1, 0)}{2} \\ \frac{C(0, 1) - C(0, -1)}{2} \end{bmatrix}$$

* $\mathbf{H}$ is the $2 \times 2$ symmetric Hessian matrix:

$$\mathbf{H} = \begin{bmatrix} \frac{\partial^2 C}{\partial u^2} & \frac{\partial^2 C}{\partial u \partial v} \\ \frac{\partial^2 C}{\partial v \partial u} & \frac{\partial^2 C}{\partial v^2} \end{bmatrix} = \begin{bmatrix} C(1, 0) - 2C(0, 0) + C(-1, 0) & \frac{C(1, 1) - C(1, -1) - C(-1, 1) + C(-1, -1)}{4} \\ \frac{C(1, 1) - C(1, -1) - C(-1, 1) + C(-1, -1)}{4} & C(0, 1) - 2C(0, 0) + C(0, -1) \end{bmatrix}$$

### 5.3 Extremum Derivation
Setting the derivative with respect to $\delta$ to zero:

$$\nabla_\delta C(\mathbf{x}_0 + \delta) = \mathbf{g} + \mathbf{H} \delta = \mathbf{0} \implies \mathbf{H} \delta^* = -\mathbf{g}$$

Solving via matrix inversion:

$$\delta^* = -\mathbf{H}^{-1} \mathbf{g} = -\frac{1}{\det(\mathbf{H})} \begin{bmatrix} H_{22} & -H_{12} \\ -H_{21} & H_{11} \end{bmatrix} \begin{bmatrix} g_1 \\ g_2 \end{bmatrix}$$

### 5.4 Physical Concavity & Stability Verification
The sub-pixel displacement $\delta^*$ represents a valid local maximum **if and only if** the Hessian matrix is strictly negative definite (concave downward surface):

$$\det(\mathbf{H}) = H_{11} H_{22} - H_{12}^2 > 0 \quad \text{and} \quad \text{Tr}(\mathbf{H}) = H_{11} + H_{22} < 0$$

Furthermore, we enforce an excursion bound to reject unstable polynomial divergence:

$$\|\delta^*\|_\infty = \max(|\Delta u^*|, |\Delta v^*|) \le 1.0\text{ px}$$

If concavity or bounds checks fail, $\delta^*$ is clamped to $\mathbf{0}$ (retaining the discrete coordinate). The refined sub-pixel coordinate is:

$$\mathbf{x}_{\text{sub}} = \mathbf{x}_0 + \delta^*$$

---

## 6. Geometric Transformation & Matrix Condition Stability

### 6.1 Transformation Models
Verified correspondence pairs $\mathbf{x}_i = [x_i, y_i, 1]^T \leftrightarrow \mathbf{x}_i' = [x_i', y_i', 1]^T$ are related by a $3 \times 3$ transformation matrix $\mathbf{T}$:

$$\mathbf{x}_i' \sim \mathbf{T} \mathbf{x}_i$$

1. **Projective Homography (8-DOF)**:
   $$\mathbf{H} = \begin{bmatrix} h_{11} & h_{12} & h_{13} \\ h_{21} & h_{22} & h_{23} \\ h_{31} & h_{32} & 1 \end{bmatrix}, \quad x' = \frac{h_{11}x + h_{12}y + h_{13}}{h_{31}x + h_{32}y + 1}, \quad y' = \frac{h_{21}x + h_{22}y + h_{23}}{h_{31}x + h_{32}y + 1}$$

2. **Affine Transformation (6-DOF)**:
   $$\mathbf{A} = \begin{bmatrix} a_{11} & a_{12} & t_x \\ a_{21} & a_{22} & t_y \\ 0 & 0 & 1 \end{bmatrix}, \quad \begin{bmatrix} x' \\ y' \end{bmatrix} = \begin{bmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{bmatrix} \begin{bmatrix} x \\ y \end{bmatrix} + \begin{bmatrix} t_x \\ t_y \end{bmatrix}$$

3. **Similarity Transformation (4-DOF)**:
   $$\mathbf{S} = \begin{bmatrix} s \cos\theta & -s \sin\theta & t_x \\ s \sin\theta & s \cos\theta & t_y \\ 0 & 0 & 1 \end{bmatrix}$$

4. **Translation (2-DOF)**:
   $$\mathbf{T}_{\text{trans}} = \begin{bmatrix} 1 & 0 & t_x \\ 0 & 1 & t_y \\ 0 & 0 & 1 \end{bmatrix}$$

### 6.2 Condition Number Stability Check
To prevent ill-conditioned homographies (which cause extreme perspective stretching or division by zero along image edges), we evaluate the matrix condition number $\kappa(\mathbf{T})$ via Singular Value Decomposition (SVD):

$$\mathbf{T} = \mathbf{U} \mathbf{\Sigma} \mathbf{V}^T, \quad \mathbf{\Sigma} = \text{diag}(\sigma_1, \sigma_2, \sigma_3)$$

$$\kappa(\mathbf{T}) = \frac{\sigma_{\max}(\mathbf{T})}{\sigma_{\min}(\mathbf{T})} = \frac{\sigma_1}{\sigma_3}$$

**Dynamic Model Downgrade Policy**:
* If $\kappa(\mathbf{H}) > 10^8$ or $\det(\mathbf{H}) \le 0$ (orientation reversal), Homography is marked degenerate.
* The system automatically downgrades the model: $\text{Homography} \to \text{Affine} \to \text{Similarity} \to \text{Translation}$.

### 6.3 Backward Warping Resampling
To ensure no holes appear in the warped output, backward mapping with bilinear interpolation is executed:

$$\mathcal{I}_{\text{warped}}(x, y) = \mathcal{I}_{\text{src}}\left(\mathbf{T}^{-1} [x, y, 1]^T\right)$$

For continuous fractional coordinate $(u, v) = \mathbf{T}^{-1}[x, y, 1]^T$, let $u_0 = \lfloor u \rfloor, v_0 = \lfloor v \rfloor$ and $\alpha = u - u_0, \beta = v - v_0$:

$$\mathcal{I}_{\text{warped}}(x, y) = (1-\alpha)(1-\beta) \mathcal{I}(u_0, v_0) + \alpha(1-\beta) \mathcal{I}(u_0+1, v_0) + (1-\alpha)\beta \mathcal{I}(u_0, v_0+1) + \alpha\beta \mathcal{I}(u_0+1, v_0+1)$$

---

## 7. Quantitative Evaluation Metrics Suite

### 7.1 Inlier Ratio ($\text{IR}$)
$$\text{IR} = \frac{N_{\text{inlier}}}{N_{\text{candidate}}} \times 100\%$$

### 7.2 Inlier Reprojection RMSE ($\text{RMSE}_{\text{inliers}}$)
The measured Euclidean error of verified correspondences under estimated model $\mathbf{H}$:

$$\text{RMSE}_{\text{inliers}} = \sqrt{ \frac{1}{N_{\text{inlier}}} \sum_{i=1}^{N_{\text{inlier}}} \left\| \mathbf{x}_i' - \pi\left(\mathbf{H} \mathbf{x}_i\right) \right\|^2 }$$

Where $\pi([u, v, w]^T) = [u/w, v/w]^T$ denotes homogeneous projection.

### 7.3 Ground-Truth RMSE ($\text{RMSE}_{\text{GT}}$)
For synthetic benchmark pairs with known analytical transformation matrix $\mathbf{H}_{\text{GT}}$, the error is evaluated over all four image corners $\mathbf{c}_k \in \{(0, 0), (W, 0), (W, H), (0, H)\}$:

$$\text{RMSE}_{\text{GT}} = \sqrt{ \frac{1}{4} \sum_{k=1}^4 \left\| \pi\left(\mathbf{H}_{\text{GT}} \mathbf{c}_k\right) - \pi\left(\mathbf{H}_{\text{est}} \mathbf{c}_k\right) \right\|^2 }$$

### 7.4 Sub-Pixel Accuracy Rate ($\text{SPA@0.5px}$)
The proportion of verified inliers whose reprojection residual falls strictly below half a pixel:

$$\text{SPA@0.5px} = \frac{1}{N_{\text{inlier}}} \sum_{i=1}^{N_{\text{inlier}}} \mathbb{I}\left( \left\| \mathbf{x}_i' - \pi\left(\mathbf{H} \mathbf{x}_i\right) \right\| < 0.5\text{ px} \right) \times 100\%$$

### 7.5 Normalized Difference Residual Map
For visual registration verification, the absolute difference map after radiometric histogram matching $\mathcal{M}$ is defined as:

$$\Delta\mathcal{I}(x, y) = \left| \mathcal{I}_{\text{ref}}(x, y) - \mathcal{M}\left(\mathcal{I}_{\text{warped}}(x, y)\right) \right|$$

In perfectly registered regions, $\Delta\mathcal{I}(x, y) \to 0$ (pure black).

---

## 8. Summary Formulation Cheatsheet for Viva / Evaluation

| Metric / Method | Mathematical Formula | Purpose in LUNARIS-X |
| :--- | :--- | :--- |
| **Phase Congruency** | $PC(x,y) = \frac{\sum_o \sum_n W_o \lfloor A_{no}\Delta\Phi_{no} - T_o \rfloor}{\sum_o \sum_n A_{no} + \epsilon}$ | Decouples structural crater rims from inverted lighting & shadows. |
| **Scale Octave** | $\mathcal{O}_k = [\mathcal{I}_{\text{OHRC}} \circledast G(2^k\sigma_0)] \downarrow_{2^k}$ | Bridges $1:18\times$ GSD disparity between TMC-2 ($5\text{m}$) and OHRC ($0.28\text{m}$). |
| **Spatial Gini** | $G_k = \frac{\sum_i \sum_j \|c_i - c_j\|}{2 K \sum_i c_i}$ | Quantifies uniform point coverage across 16 quad-tree grid cells ($G_k < 0.35$). |
| **Sub-Pixel Peak** | $\delta^* = -\mathbf{H}_C^{-1} \mathbf{g}_C$ | 2D quadratic Taylor fit achieving sub-pixel precision ($\text{RMSE} < 0.5\text{ px}$). |
| **Condition Check** | $\kappa(\mathbf{T}) = \frac{\sigma_{\max}(\mathbf{T})}{\sigma_{\min}(\mathbf{T})} < 10^8$ | Prevents degenerate perspective stretching and numerical blowup. |
| **Reprojection RMSE** | $\text{RMSE} = \sqrt{\frac{1}{N}\sum \|\mathbf{x}_i' - \mathbf{H}\mathbf{x}_i\|^2}$ | Primary metric proving geometric correspondence precision. |

---
*Authored for Smart India Hackathon (SIH 2026) &bull; Problem Statement SIH26166*  
*Indian Space Research Organisation (ISRO) &bull; Space Applications Centre (SAC)*
