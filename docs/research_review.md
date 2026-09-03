# Comprehensive Research Review: Planetary Optical & Multimodal Image Correspondence

## 1. Introduction
Autonomous image registration and correspondence across planetary remote sensing datasets is a foundational prerequisite for high-precision lunar cartography, digital elevation model (DEM) extraction, landing hazard assessment, and spectral mineralogy mapping. In the context of the **ISRO Chandrayaan-2** mission, the challenge is amplified by three distinct sensors: **OHRC** (sub-meter panchromatic), **TMC-2** (stereo triplet panchromatic), and **IIRS** (hyperspectral SWIR).

This review surveys the theoretical physics, classical photogrammetry, frequency-domain representations, and deep-learning methods relevant to solving SIH26166.

---

## 2. Theoretical Foundations: Lunar Photometry & Illumination Physics

### 2.1 The Non-Atmospheric Lunar Environment
Unlike Earth observation imagery, where Rayleigh and aerosol scattering produce diffuse skylight that softly illuminates shadowed areas, the lunar surface operates in a near-perfect vacuum ($P < 10^{-12}\text{ torr}$). Consequently:
1. **Harsh Step-Function Shadows**: Direct solar flux creates binary illumination transitions. Shadowed regions receive only minimal secondary scattered radiance from adjacent illuminated crater walls.
2. **Directional Illumination Inversion**: When the sun moves from East to West across orbits ($\Delta \phi_\odot \approx 180^\circ$), the illuminated rim of a crater switches to the opposite side. Gradient vectors ($\nabla I$) invert their direction completely:
   $$\nabla I_{\text{afternoon}}(\mathbf{x}) \approx - \nabla I_{\text{morning}}(\mathbf{x})$$
   Any algorithm relying on monotonic gradient orientation (e.g., SIFT, SURF, ORB) matches opposing crater rims rather than true physical points, causing severe registration errors.

### 2.2 Non-Lambertian Reflectance Models (Hapke & Lommel-Seeliger)
The lunar regolith exhibits a strong opposition surge and anisotropic backward scattering governed by Hapke's photometric equation:
$$r(i, e, \alpha) = \frac{w}{4\pi} \frac{\mu_0}{\mu_0 + \mu} \left[ (1 + B(\alpha)) P(\alpha) + H(\mu_0) H(\mu) - 1 \right] S(i, e, \alpha, \bar{\theta})$$
Where:
- $i$ = Solar incidence angle
- $e$ = Emission angle
- $\alpha$ = Phase angle
- $B(\alpha)$ = Opposition effect term
- $P(\alpha)$ = Particle phase function
- $S(i, e, \alpha, \bar{\theta})$ = Macroscopic surface roughness correction factor

Because reflectance is a non-linear function of illumination angles, standard radiometric cross-correlation (NCC) fails when $\Delta \alpha > 15^\circ$.

---

## 3. Analysis of Existing Methodological Paradigms

```
+---------------------------------------------------------------------------------------------------+
| PARADIGM               | METHOD EXAMPLES             | STRENGTHS             | LUNAR LIMITATIONS  |
+------------------------+-----------------------------+-----------------------+--------------------+
| 1. Classical Gradient  | SIFT, ASIFT, SURF, AKAZE    | Fast, scale/rotation  | Gradient inversion |
|                        |                             | invariant in 2D       | under shadow flip  |
+------------------------+-----------------------------+-----------------------+--------------------+
| 2. Phase / Frequency   | RIFT, RIFT2, OS-SIFT        | Radiometric & modal   | Breaks at scale    |
|                        |                             | invariance via phase  | ratios > 3.5x      |
+------------------------+-----------------------------+-----------------------+--------------------+
| 3. Deep Transformers   | LoFTR, SuperGlue, RoMa, DKM | Dense matching in low | Pretrained on Earth|
|                        |                             | texture regions       | collapses on regolith |
+------------------------+-----------------------------+-----------------------+--------------------+
| 4. Planetary Pipelines | USGS ISIS3, Ames Stereo     | Geodetically accurate | Relies on manual / |
|                        |                             | with SPICE kernels    | NCC tie-point seeds|
+---------------------------------------------------------------------------------------------------+
```

---

## 4. Gap Analysis & Proposed Direction

Existing literature provides separate solutions for:
- Non-linear contrast (RIFT/RIFT2)
- Dense feature context (LoFTR)
- Geodetic geometry (USGS ISIS3)

However, **no unified pipeline currently addresses the simultaneous combination of**:
1. $20\times$ cross-scale resolution bridging (TMC-2 $\leftrightarrow$ OHRC).
2. Complete $180^\circ$ solar azimuth shadow invariance.
3. Hyperspectral SWIR to panchromatic cross-modal alignment.
4. Uniform geodetic spatial dispersion without crater-rim clumping.

Our research aims to address this multi-dimensional gap through an experimentally validated Proposed Method.
