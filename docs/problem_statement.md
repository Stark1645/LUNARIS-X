# SIH26166: Problem Statement & Scientific Objectives

## 1. Problem Statement Details
- **Project ID**: SIH26166
- **Title**: Multi-modal, Sun angle and scale invariant image correspondence using Chandrayaan-2 optical images (OHRC, TMC and IIRS)
- **Organization**: Indian Space Research Organisation (ISRO), Department of Space
- **Category**: Software
- **Theme**: Space Technology

---

## 2. Scientific Meaning of the Problem
The Chandrayaan-2 lunar orbiter mission hosts a premier optical payload suite capable of mapping the Moon at unprecedented spatial and spectral resolutions. However, integrating, co-registering, and cross-referencing observations across different passes and instruments remains an unsolved challenge due to the physics of the lunar imaging environment:

1. **Illumination & Sun Angle Dynamics**:
   - The Moon has no atmosphere, meaning illumination is direct solar flux without diffuse ambient skylight. Shadows are binary, harsh, and span tens of kilometers at high solar incidence angles.
   - When the solar azimuth ($\phi_\odot$) shifts between orbits (e.g. morning vs afternoon passes, $180^\circ$ difference), crater rim shadows completely flip. Standard computer vision edge detectors (which track intensity gradients) track shadow boundaries rather than physical geomorphology, leading to catastrophic matching errors.

2. **Severe Scale & Resolution Disparities**:
   - **OHRC** achieves $\sim 0.25 - 0.32\text{ m/pixel}$ (detecting boulders and meter-scale craters).
   - **TMC-2** operates at $\sim 5.0\text{ m/pixel}$ (regional geomorphology, stereo DEM).
   - **IIRS** operates at $\sim 80 - 250\text{ m/pixel}$ (mineralogy and chemical absorption maps).
   - The scale factor jump between TMC-2 and OHRC is $\sim 1:16$ to $1:20$, and between IIRS and OHRC is up to $1:800$. Classical scale-invariant feature transform (SIFT) octave pyramids break down past $3\times - 4\times$ scale differences.

3. **Multi-Modal & Spectral Differences**:
   - OHRC and TMC-2 are broad panchromatic optical systems (450–900 nm).
   - IIRS records 256 contiguous spectral bands from 0.8 µm to 5.0 µm (VNIR to SWIR). Absorption features (such as the 1 µm and 2 µm pyroxene absorption bands and 3 µm hydration features) cause local contrast reversals and non-linear radiometric variations that invalidate cross-correlation and standard gradient descriptors.

4. **Viewing Geometry & Stereoscopic Parallax**:
   - TMC-2 captures triplets (Fore $+26^\circ$, Nadir $0^\circ$, Aft $-26^\circ$), creating perspective foreshortening over steep crater walls and central peaks.

---

## 3. High-Level Objectives
1. **Automated End-to-End Image Correspondence**: Establish true physical landmark matches across arbitrary pairs of Chandrayaan-2 images (OHRC-OHRC, TMC2-TMC2, OHRC-TMC2, TMC2-IIRS, OHRC-IIRS).
2. **Illumination Invariance**: Maintain consistent, correct correspondence even under opposing sun azimuths ($\Delta\phi_\odot \approx 180^\circ$) and high incidence angles ($\theta_i > 60^\circ$).
3. **Scale Invariance Across $20\times+$ Disparity**: Successfully link coarse contextual frames with ultra-high resolution target chips without manual seeding.
4. **Outlier Rejection & Geodetic Spatial Coverage**: Eliminate false matches caused by repetitive crater patterns and ensure correspondences are evenly distributed across the entire frame.
5. **Sub-Pixel Accuracy & Geometric Registration**: Produce high-precision transformation models (Homography, Thin-Plate Spline, or Rational Polynomials) with sub-pixel residual errors ($\text{RMSE} < 1.0\text{ px}$).
