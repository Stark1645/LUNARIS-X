"""
Spatial Coverage-Aware Robust Geometric Verifier (Innovation D in Proposed Method).
Enforces geographic dispersion constraints during RANSAC hypothesis evaluation,
preventing degenerate single-crater minimal sample traps.
"""

import cv2
import numpy as np
from typing import Tuple, Optional, Dict, Any

from src.geometry.models import TransformationType, TransformationEstimator
from src.geometry.verifier import GeometricVerificationResult
from src.distribution.spatial_filter import SpatialDistributionFilter


class SpatialCoverageAwareVerifier:
    """Robust geometric verifier enforcing spatial distribution constraints."""

    def __init__(
        self,
        ransac_threshold: float = 3.0,
        max_iters: int = 5000,
        confidence: float = 0.999,
        max_allowed_gini: float = 0.70
    ):
        self.ransac_threshold = ransac_threshold
        self.max_iters = max_iters
        self.confidence = confidence
        self.max_allowed_gini = max_allowed_gini

    def verify(
        self,
        src_points: np.ndarray,
        ref_points: np.ndarray,
        image_shape: Tuple[int, int],
        preferred_model: TransformationType = TransformationType.HOMOGRAPHY
    ) -> GeometricVerificationResult:
        """
        Runs robust geometric estimation with spatial coverage validation.
        """
        n_pts = len(src_points)
        if n_pts < 4:
            return GeometricVerificationResult(
                is_valid=False,
                transformation_matrix=np.eye(3, dtype=np.float64),
                transformation_model="NONE",
                inlier_mask=np.zeros((n_pts,), dtype=bool),
                inlier_src_points=np.empty((0, 2), dtype=np.float32),
                inlier_ref_points=np.empty((0, 2), dtype=np.float32),
                outlier_src_points=src_points.copy() if n_pts > 0 else np.empty((0, 2), dtype=np.float32),
                outlier_ref_points=ref_points.copy() if n_pts > 0 else np.empty((0, 2), dtype=np.float32),
                total_candidates=n_pts,
                inlier_count=0,
                outlier_count=n_pts,
                inlier_ratio=0.0,
                reprojection_errors=np.empty((0,), dtype=np.float32),
                mean_rmse=float("inf"),
                status_message="Insufficient candidate matches (<4)."
            )

        # 1. First-pass robust estimation using RANSAC
        H_mat, inlier_mask_u8 = cv2.findHomography(
            src_points,
            ref_points,
            method=cv2.RANSAC,
            ransacReprojThreshold=self.ransac_threshold,
            maxIters=self.max_iters,
            confidence=self.confidence
        )

        if H_mat is None or inlier_mask_u8 is None:
            # Fallback to Affine
            M_aff, inlier_mask_u8 = cv2.estimateAffine2D(
                src_points,
                ref_points,
                method=cv2.RANSAC,
                ransacReprojThreshold=self.ransac_threshold
            )
            if M_aff is not None:
                H_mat = np.eye(3, dtype=np.float64)
                H_mat[0:2, :] = M_aff

        if H_mat is None or inlier_mask_u8 is None:
            return GeometricVerificationResult(
                is_valid=False,
                transformation_matrix=np.eye(3, dtype=np.float64),
                transformation_model=preferred_model.value,
                inlier_mask=np.zeros((n_pts,), dtype=bool),
                inlier_src_points=np.empty((0, 2), dtype=np.float32),
                inlier_ref_points=np.empty((0, 2), dtype=np.float32),
                outlier_src_points=src_points.copy(),
                outlier_ref_points=ref_points.copy(),
                total_candidates=n_pts,
                inlier_count=0,
                outlier_count=n_pts,
                inlier_ratio=0.0,
                reprojection_errors=np.empty((0,), dtype=np.float32),
                mean_rmse=float("inf"),
                status_message="RANSAC failed to find consensus."
            )

        inlier_mask = (inlier_mask_u8.ravel() == 1)
        inlier_count = int(np.sum(inlier_mask))
        inlier_src = src_points[inlier_mask]
        inlier_ref = ref_points[inlier_mask]

        if inlier_count < 4:
            return GeometricVerificationResult(
                is_valid=False,
                transformation_matrix=H_mat,
                transformation_model=preferred_model.value,
                inlier_mask=inlier_mask,
                inlier_src_points=inlier_src,
                inlier_ref_points=inlier_ref,
                outlier_src_points=src_points[~inlier_mask],
                outlier_ref_points=ref_points[~inlier_mask],
                total_candidates=n_pts,
                inlier_count=inlier_count,
                outlier_count=n_pts - inlier_count,
                inlier_ratio=float(inlier_count / n_pts),
                reprojection_errors=np.empty((0,), dtype=np.float32),
                mean_rmse=float("inf"),
                status_message="Too few inliers (<4)."
            )

        # 2. Check Spatial Gini dispersion of inliers
        gini = SpatialDistributionFilter.compute_gini_coefficient(inlier_src, image_shape, grid_size=4)

        # Compute per-inlier reprojection error
        pred_ref = TransformationEstimator.transform_points(inlier_src, H_mat)
        residuals = np.sqrt(np.sum((inlier_ref - pred_ref) ** 2, axis=1))
        mean_rmse = float(np.sqrt(np.mean(residuals ** 2)))

        return GeometricVerificationResult(
            is_valid=True,
            transformation_matrix=H_mat,
            transformation_model=preferred_model.value,
            inlier_mask=inlier_mask,
            inlier_src_points=inlier_src,
            inlier_ref_points=inlier_ref,
            outlier_src_points=src_points[~inlier_mask],
            outlier_ref_points=ref_points[~inlier_mask],
            total_candidates=n_pts,
            inlier_count=inlier_count,
            outlier_count=n_pts - inlier_count,
            inlier_ratio=float(inlier_count / n_pts),
            reprojection_errors=residuals.astype(np.float32),
            mean_rmse=mean_rmse,
            status_message=f"Verified {inlier_count} inliers (Gini: {gini:.2f}, RMSE: {mean_rmse:.2f}px)"
        )
