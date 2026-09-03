# Baseline Implementation & Reproduction Plan

## 1. Selected Baselines for Benchmarking

To rigorously prove that our proposed method outperforms existing algorithms, we implement 5 representative state-of-the-art baselines across classical, frequency, and deep learned paradigms:

| Baseline | Class | Implementation Details | Expected Failure Modes on Chandrayaan-2 |
| :--- | :--- | :--- | :--- |
| **SIFT / ASIFT** | Classical Gradient | OpenCV `cv2.SIFT_create()` + BruteForce Matcher + RANSAC | Fails when solar azimuth changes $>45^\circ$ due to gradient vector inversion; fails on scale jump $>3\times$. |
| **AKAZE** | Non-Linear Scale Space | OpenCV `cv2.AKAZE_create()` (FED non-linear diffusion) | Slightly better edge preservation, but still gradient-driven and susceptible to shadow drift. |
| **RIFT / RIFT2** | Frequency / Phase | Multi-orientation Log-Gabor filters + Maximum Index Map (MIMPC) | Handles contrast inversion, but breaks on scale jumps $>4\times$ and has high computation time on large images. |
| **SuperPoint + SuperGlue** | Learned Sparse | PyTorch GNN Matcher with self/cross attention | Fails to detect interest points inside dark shadowed crater floors; misses features across $20\times$ scale gaps. |
| **LoFTR** | Learned Dense Transformer | CNN + Linear Transformer cross-attention on dense $1/8$ feature grid | Strong in textureless terrain, but degraded by binary lunar shadow boundaries and out-of-distribution regolith textures. |

---

## 2. Standardized Evaluation Harness
All baselines and the proposed method will be executed through a unified benchmarking script:
```bash
python -m src.evaluation.benchmark_runner --dataset data/benchmark --baselines sift,akaze,rift2,loftr,proposed --output results/
```
Output metrics:
- Inlier Count ($N_{\text{inlier}}$)
- Inlier Ratio ($\%$)
- Mean Reprojection Error (pixels)
- Spatial Distribution Gini Coefficient ($G_k$)
- Runtime per Megapixel (seconds)
