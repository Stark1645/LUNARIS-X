# Core Innovation: Technical Hypotheses & Algorithmic Formulation

## 1. Technical Opportunities & Research Hypotheses

Our proposed approach addresses specific failure modes observed during preliminary photogrammetric analysis on Chandrayaan-2 imagery:

### Research Direction 1: Multi-Scale Phase-Structural Scale Bridge
- **The Challenge**: Standard multi-scale descriptors (e.g. classical SIFT octave pyramids) degrade significantly across extreme resolution jumps ($1:4$ to $1:20+$ between TMC-2 $5\text{ m/px}$ and OHRC $0.25\text{ m/px}$).
- **Proposed Method (Hypothesis)**: A hierarchical Gaussian-scale pyramid bridging scheme combined with coarse geographic bounding box anchoring from PDS4 metadata. The algorithm establishes anchor nodes at intermediate octaves:
  $$\mathcal{O}_k = \mathcal{I}_{\text{OHRC}} \circledast G(2^k \sigma_0) \downarrow_{2^k} \quad \text{for } k \in [0, \log_2(R)]$$
  Correspondence is established hierarchically, constraining candidate search bounds.
- **Evaluation Goal**: Quantify registration success rate and inlier retention across scale ratios $1:4$, $1:16$, and $1:20$ on synthetic benchmarks and authentic orbital pairs.

### Research Direction 2: Phase Congruency Representation (Evaluated Baseline / Structural Method)
- **The Challenge**: Opposing solar azimuths invert gradient signs ($\nabla I \to -\nabla I$), causing standard gradient-based orientation histograms to drift by $180^\circ$.
- **Method Formulation**: Evaluating multi-scale, multi-orientation Log-Gabor Phase Congruency ($PC$) as a structural representation:
  $$PC(x,y) = \frac{\sum_o \sum_n W_o(x,y) \lfloor A_{no}(x,y) \Delta\Phi_{no}(x,y) - T_o \rfloor}{\sum_o \sum_n A_{no}(x,y) + \epsilon}$$
  Constructing a Maximum Index Map of Phase Congruency (MIMPC) to evaluate whether phase alignment preserves structural features under solar azimuth reversals.
- **Evaluation Goal**: Measure whether RIFT / Phase Congruency improves inlier ratios under $90^\circ$ and $180^\circ$ solar azimuth disparities compared to the SIFT baseline.

### Research Direction 3: Spatial Dispersion Optimization (Quad-Tree Gini Filter)
- **The Challenge**: Standard geometric estimation tends to cluster inliers exclusively on localized, high-contrast crater rims, leaving large regions unconstrained and leading to uncontrolled peripheral warping.
- **Proposed Method**: A spatial Quad-Tree partitioning filter applied to verified geometric inliers, selecting top-confidence tie-points per quadrant.
- **Optimization Target**: Drive down the spatial Gini coefficient ($G_k$) to achieve uniform landmark distribution across the overlapping area without injecting synthetic correspondences.

### Research Direction 4: Continuous 2D Parabolic Sub-Pixel Surface Refinement
- **The Challenge**: Discrete pixel grid matching introduces quantization errors ($\pm 0.5\text{ px}$), impacting fine registration precision.
- **Proposed Method**: Continuous quadratic Taylor surface fitting on local correlation neighborhoods around verified inlier tie-points:
  $$\mathbf{\delta}^* = - \mathbf{H}_C^{-1} \nabla C$$
- **Optimization Target**: Measure residual reprojection improvement against analytical ground truth, targeting fractional-pixel accuracy on stable features.

