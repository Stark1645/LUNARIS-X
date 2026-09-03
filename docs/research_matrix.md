# Comprehensive Research Matrix: Lunar & Multimodal Correspondence

| Paper / System | Year | Authors / Institution | Target Sensors / Datasets | Algorithm / Methodology | Key Strengths | Critical Weaknesses & Gaps | Relevance to Our Scope |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RIFT (Radiation-Invariant Feature Transform)** | 2020 | J. Li et al. (IEEE TGRS) | SAR, Optical, Infrared, Map data | Phase Congruency + Maximum Index Map (MIM) + SIFT-like Log-polar grid | Invariant to severe non-linear radiometric differences; robust to illumination direction | Fails at scale changes $>3.5\times$; high computational cost; susceptible to repetitive crater textures | Core baseline for Phase Congruency & multimodal structural representation |
| **RIFT 2 (Fast Radiation-Invariant Feature Transform)** | 2022 | J. Li et al. (IEEE TGRS) | Multi-modal remote sensing | Fast Log-Gabor Phase Congruency + Orientated Gradient Inversion | $4\times$ faster than RIFT; improved repeatability on optical-to-NIR | Still breaks on large scale jumps ($>4\times$); lacks sub-pixel geometric refinement | Foundation for our structural invariant branch |
| **LoFTR (Detector-Free Local Feature Matching with Transformers)** | 2021 | J. Sun et al. (CVPR) | MegaDepth, ScanNet (Terrestrial) | CNN backbone + Self- and Cross-Attention Transformers on dense grids | Dense matching in textureless regions; avoids fragile detector stage | Pretrained on terrestrial textures; degraded by binary lunar shadows; high memory footprint | Candidate deep dense baseline; domain adaptation target |
| **RoMa (Robust Dense Feature Matching)** | 2023 | J. Edstedt et al. (CVPR) | Terrestrial benchmarks | DINOv2 / Foundation Model + Dense Warp Field Estimation | SOTA dense accuracy on terrestrial outdoor scenes | High memory footprint; poor cross-resolution matching across $20\times$ scale gaps | Candidate deep dense baseline |
| **SuperPoint + SuperGlue / LightGlue** | 2018 / 2020 / 2023 | D. DeTone, P. Sarlin, P. Lindenberger (CVPR / ICCV) | MS-COCO, MegaDepth | Self-supervised interest point detector + Graph Neural Network matcher | High inlier ratio on planar/terrestrial scenes; fast inference with LightGlue | Keypoint detector misses features in shadowed lunar crater interiors | Candidate sparse learned baseline |
| **USGS ISIS3 (Integrated Software for Imagers and Spectrometers)** | 2018–2023 | USGS Astrogeology Science Center | LRO (LROC NAC/WAC), Kaguya, Chandrayaan-1 | SPICE geometry + Point-based Normalized Cross Correlation (NCC) + Bundle Adjustment | Geodesically accurate; integrates spacecraft telemetry | NCC fails when solar azimuth changes $>30^\circ$; manual tie-point seeding often required | Provides georeferencing & SPICE projection reference standard |
| **Photometric Normalization / Hapke Lunar SfS** | 2014–2021 | Wohlfarth et al., Grumpe et al. | LROC NAC, Chandrayaan-1 M3 | Hapke Photometric Model Inversion + Shape from Shading (SfS) | Disentangles topography from illumination to create virtual nadir-sun albedo maps | High computational overhead; requires high-accuracy prior DEM to prevent artifact generation | Can be used as an illumination-normalization pre-filter module |
| **Lunar Crater-Centroid Invariants** | 2011–2020 | Troglio et al., Bandeira et al. | Lunar orbital images | Conic fitting on crater rims + Delaunay triangulation graph matching | Invariant to illumination direction changes because crater geometry is physical | Fails in non-cratered maria regions or heavily boulder-strewn terrain; sensitive to crater overlap | Candidate structural anchor module for large scale gaps ($>10\times$) |
| **ASIFT (Affine SIFT)** | 2009 | J.M. Morel & G. Yu (SIIMS) | General Computer Vision | Affine parameter space simulation (tilt and rotation) + SIFT | Invariant to extreme perspective tilt (e.g. TMC-2 Fore/Aft) | $O(N^2)$ simulation explosion; does not solve shadow reversal or cross-modal radiometry | Baseline for extreme perspective / stereo triplet matching |
| **OS-SIFT (Optical-to-SAR SIFT)** | 2018 | Y. Xiang et al. (IEEE GRSL) | Optical and SAR images | Exponential and Ratio Gradient Operators + Multi-scale Sobel | Resilient to multiplicative speckle and intensity inversion | Sensitive to large scale differences; limited repeatability in shadow-dominant lunar scenes | Classical multimodal comparison |
| **SOS-Mask / Deep Shadow Removal for Planetary Regolith** | 2021 | H. Wu et al. | Planetary orbital datasets | Generative Adversarial Networks (GANs) for shadow illumination inpainting | Synthesizes illuminated terrain inside deep shadows | Risk of hallucinating non-existent crater morphology; unsuited for high-precision metrology | Explored and rejected for safety/scientific validity |

---

## Synthesis: Research to Opportunity Bridge

```
+---------------------------------------------------------------------------------------------------+
| RESEARCH FINDINGS          | IDENTIFIED GAPS              | SYSTEM RESEARCH OPPORTUNITY           |
+----------------------------+------------------------------+---------------------------------------+
| 1. Phase congruency works  | Fails at scale jumps > 4x;   | Hierarchical Gaussian-pyramid scale   |
|    for contrast inversion. | high compute on 10k x 10k.   | bridge with coarse tile anchoring.    |
|                            |                              |                                       |
| 2. Deep transformers excel | Pretrained on Earth; fail on | Planetary feature representation      |
|    in textureless areas.   | binary shadows and regolith. | on lunar regolith patches.            |
|                            |                              |                                       |
| 3. SPICE/telemetry gives   | Sub-pixel drift exists;      | SPICE-initialized bounding box search |
|    coarse geographic bounds| tie-points cluster on rims.  | + Quad-tree spatial filtering.        |
+---------------------------------------------------------------------------------------------------+
```
