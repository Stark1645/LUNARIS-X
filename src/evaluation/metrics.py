"""
Scientific Metric Evaluation Module for SIH26166.
Computes RMSE, Inlier Match Count, Inlier Ratio, Sub-Pixel Accuracy,
Spatial Distribution Gini Coefficient, and Processing Latency.
Strictly distinguishes Reprojection Residuals vs Analytical Ground Truth Error.
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class RegistrationMetrics:
    """Scientific registration quality metrics record."""
    status: str  # SUCCESS | FAILED
    algorithm: str  # SIFT_Baseline | RIFT_Baseline | Proposed_Method
    transformation_model: str  # TRANSLATION | SIMILARITY | AFFINE | HOMOGRAPHY
    
    # Core SIH Metrics
    rmse_inliers: float  # RMSE of inlier correspondences [pixels] (reprojection residual)
    rmse_ground_truth: Optional[float]  # RMSE against analytical ground truth (if available) [pixels]
    ground_truth_status: str  # AVAILABLE | NOT_AVAILABLE
    inlier_match_count: int  # Number of verified geometric inliers
    candidate_match_count: int  # Number of raw candidate matches
    inlier_ratio_percent: float  # Inlier Ratio (%)
    
    # Sub-Pixel Precision & Residuals
    mean_subpixel_residual: float  # Mean residual reprojection error [pixels]
    mae_residuals: float  # Mean Absolute Error of residuals [pixels]
    median_residual: float  # Median residual [pixels]
    max_residual: float  # Maximum residual error [pixels]
    subpixel_accuracy_rate_05px: float  # % inliers with error < 0.5 px
    subpixel_accuracy_rate_10px: float  # % inliers with error < 1.0 px
    
    # Spatial Dispersion
    spatial_gini_coefficient: float  # Keypoint Gini G_k in [0, 1]
    spatial_quality_status: str  # GOOD | ACCEPTABLE | POOR
    
    # Execution Performance
    latency_ms: float  # Total processing latency in milliseconds
    
    # Data Provenance Classification
    is_synthetic: bool  # True for synthetic benchmark, False for authentic flight data
    dataset_category: str  # SYNTHETIC_BENCHMARK | AUTHENTIC_CH2_PRADAN

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RegistrationEvaluator:
    """Calculates quantitative scientific metrics for image registration experiments."""

    @staticmethod
    def evaluate(
        src_inliers: np.ndarray,
        ref_inliers: np.ndarray,
        H_estimated: np.ndarray,
        candidate_count: int,
        algorithm_name: str,
        transformation_model: str,
        image_shape: Tuple[int, int],
        H_ground_truth: Optional[np.ndarray] = None,
        latency_ms: float = 0.0,
        is_synthetic: bool = True,
        dataset_category: str = "SYNTHETIC_BENCHMARK",
        spatial_quality_status: str = "POOR"
    ) -> RegistrationMetrics:
        """
        Computes the complete SIH26166 evaluation metric suite.
        """
        n_inliers = len(src_inliers)

        if n_inliers < 4 or H_estimated is None:
            return RegistrationMetrics(
                status="FAILED",
                algorithm=algorithm_name,
                transformation_model=transformation_model,
                rmse_inliers=float("inf"),
                rmse_ground_truth=None,
                ground_truth_status="NOT_AVAILABLE" if H_ground_truth is None else "AVAILABLE",
                inlier_match_count=n_inliers,
                candidate_match_count=candidate_count,
                inlier_ratio_percent=0.0,
                mean_subpixel_residual=float("inf"),
                mae_residuals=float("inf"),
                median_residual=float("inf"),
                max_residual=float("inf"),
                subpixel_accuracy_rate_05px=0.0,
                subpixel_accuracy_rate_10px=0.0,
                spatial_gini_coefficient=1.0,
                spatial_quality_status="POOR",
                latency_ms=latency_ms,
                is_synthetic=is_synthetic,
                dataset_category=dataset_category
            )

        # 1. Transform source inliers to reference space: x_pred = H * x_src
        pts_hom = np.hstack([src_inliers, np.ones((n_inliers, 1), dtype=np.float64)])
        pred_hom = (H_estimated @ pts_hom.T).T
        w = pred_hom[:, 2:3]
        w[np.abs(w) < 1e-10] = 1e-10
        pred_ref = (pred_hom[:, :2] / w).astype(np.float32)

        # 2. Per-point reprojection errors: || x_ref - pred_ref ||
        residuals = np.sqrt(np.sum((ref_inliers - pred_ref) ** 2, axis=1))
        rmse_inliers = float(np.sqrt(np.mean(residuals ** 2)))
        mean_subpixel_residual = float(np.mean(residuals))
        mae_residuals = float(np.mean(np.abs(residuals)))
        median_residual = float(np.median(residuals))
        max_residual = float(np.max(residuals))
        spa_05px = float(np.sum(residuals < 0.5) / n_inliers * 100.0)
        spa_10px = float(np.sum(residuals < 1.0) / n_inliers * 100.0)

        # 3. Inlier Ratio
        inlier_ratio = float(n_inliers / candidate_count * 100.0) if candidate_count > 0 else 0.0

        # 4. Ground Truth RMSE (if analytical ground truth available)
        rmse_gt = None
        gt_status = "NOT_AVAILABLE"
        if H_ground_truth is not None:
            gt_status = "AVAILABLE"
            gt_hom = (H_ground_truth @ pts_hom.T).T
            w_gt = gt_hom[:, 2:3]
            w_gt[np.abs(w_gt) < 1e-10] = 1e-10
            pred_gt = (gt_hom[:, :2] / w_gt).astype(np.float32)
            gt_diff = np.sqrt(np.sum((pred_ref - pred_gt) ** 2, axis=1))
            rmse_gt = float(np.sqrt(np.mean(gt_diff ** 2)))

        # 5. Spatial Gini Coefficient G_k
        from src.distribution.spatial_filter import SpatialDistributionFilter
        gini_k = SpatialDistributionFilter.compute_gini_coefficient(src_inliers, image_shape, grid_size=4)

        return RegistrationMetrics(
            status="SUCCESS",
            algorithm=algorithm_name,
            transformation_model=transformation_model,
            rmse_inliers=round(rmse_inliers, 4),
            rmse_ground_truth=round(rmse_gt, 4) if rmse_gt is not None else None,
            ground_truth_status=gt_status,
            inlier_match_count=n_inliers,
            candidate_match_count=candidate_count,
            inlier_ratio_percent=round(inlier_ratio, 2),
            mean_subpixel_residual=round(mean_subpixel_residual, 4),
            mae_residuals=round(mae_residuals, 4),
            median_residual=round(median_residual, 4),
            max_residual=round(max_residual, 4),
            subpixel_accuracy_rate_05px=round(spa_05px, 2),
            subpixel_accuracy_rate_10px=round(spa_10px, 2),
            spatial_gini_coefficient=round(gini_k, 4),
            spatial_quality_status=spatial_quality_status,
            latency_ms=round(latency_ms, 2),
            is_synthetic=is_synthetic,
            dataset_category=dataset_category
        )
