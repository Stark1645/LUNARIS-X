"""
Robust Geometric Verification & Inlier / Outlier Separation for SIH26166.
Uses RANSAC / USAC-based robust estimation (and evaluates MAGSAC++ where supported)
to strictly separate candidate matches into geometrically verified inliers and discarded outliers.
"""

import cv2
import numpy as np
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass
from src.geometry.models import TransformationType, TransformationEstimator


@dataclass
class GeometricVerificationResult:
    """Encapsulates the output of robust geometric verification."""
    is_valid: bool
    transformation_matrix: np.ndarray  # 3x3 matrix mapping Source -> Reference
    transformation_model: str  # HOMOGRAPHY, AFFINE, SIMILARITY, TRANSLATION
    inlier_mask: np.ndarray  # (N,) boolean array (True = Inlier, False = Outlier)
    
    # Inlier correspondences (Proceed to spatial distribution & sub-pixel refinement)
    inlier_src_points: np.ndarray  # (M, 2)
    inlier_ref_points: np.ndarray  # (M, 2)
    
    # Outliers (Discarded)
    outlier_src_points: np.ndarray  # (K, 2)
    outlier_ref_points: np.ndarray  # (K, 2)
    
    # Metrics
    total_candidates: int
    inlier_count: int
    outlier_count: int
    inlier_ratio: float  # inlier_count / total_candidates in [0, 1]
    reprojection_errors: np.ndarray  # (M,) errors for inliers in pixels
    mean_rmse: float  # Mean RMSE on verified inliers
    status_message: str


class RobustGeometricVerifier:
    """Performs robust geometric consistency verification and inlier/outlier separation."""

    def __init__(
        self,
        ransac_threshold: float = 3.0,
        max_iters: int = 5000,
        confidence: float = 0.999,
        method: str = "RANSAC"  # RANSAC | USAC_DEFAULT | USAC_MAGSAC | USAC_FAST
    ):
        self.ransac_threshold = ransac_threshold
        self.max_iters = max_iters
        self.confidence = confidence
        self.method_name = method

    def verify(
        self,
        src_points: np.ndarray,
        ref_points: np.ndarray,
        preferred_model: TransformationType = TransformationType.HOMOGRAPHY
    ) -> GeometricVerificationResult:
        """
        Runs robust geometric estimation and separates inliers from outliers.
        """
        n_pts = len(src_points)
        if n_pts < 4 or len(ref_points) != n_pts:
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
                status_message="Insufficient candidate matches for geometric verification."
            )

        # Select OpenCV RANSAC method flag
        cv_method = cv2.RANSAC
        if self.method_name == "USAC_MAGSAC" and hasattr(cv2, "USAC_MAGSAC"):
            cv_method = cv2.USAC_MAGSAC
        elif self.method_name == "USAC_DEFAULT" and hasattr(cv2, "USAC_DEFAULT"):
            cv_method = cv2.USAC_DEFAULT
        elif self.method_name == "USAC_FAST" and hasattr(cv2, "USAC_FAST"):
            cv_method = cv2.USAC_FAST

        H_mat = None
        inlier_mask_u8 = None

        if preferred_model == TransformationType.HOMOGRAPHY:
            H_mat, inlier_mask_u8 = cv2.findHomography(
                src_points,
                ref_points,
                method=cv_method,
                ransacReprojThreshold=self.ransac_threshold,
                maxIters=self.max_iters,
                confidence=self.confidence
            )
        elif preferred_model == TransformationType.AFFINE:
            M_affine, inlier_mask_u8 = cv2.estimateAffine2D(
                src_points,
                ref_points,
                method=cv_method,
                ransacReprojThreshold=self.ransac_threshold,
                maxIters=self.max_iters,
                confidence=self.confidence
            )
            if M_affine is not None:
                H_mat = np.eye(3, dtype=np.float64)
                H_mat[0:2, :] = M_affine
        elif preferred_model == TransformationType.SIMILARITY:
            M_sim, inlier_mask_u8 = cv2.estimateAffinePartial2D(
                src_points,
                ref_points,
                method=cv_method,
                ransacReprojThreshold=self.ransac_threshold,
                maxIters=self.max_iters,
                confidence=self.confidence
            )
            if M_sim is not None:
                H_mat = np.eye(3, dtype=np.float64)
                H_mat[0:2, :] = M_sim

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
                status_message="Robust model estimation failed to find a valid geometric consensus."
            )

        inlier_mask = (inlier_mask_u8.ravel() == 1)
        inlier_count = int(np.sum(inlier_mask))
        outlier_count = n_pts - inlier_count
        inlier_ratio = float(inlier_count / n_pts) if n_pts > 0 else 0.0

        if inlier_count < 4:
            return GeometricVerificationResult(
                is_valid=False,
                transformation_matrix=H_mat,
                transformation_model=preferred_model.value,
                inlier_mask=inlier_mask,
                inlier_src_points=src_points[inlier_mask],
                inlier_ref_points=ref_points[inlier_mask],
                outlier_src_points=src_points[~inlier_mask],
                outlier_ref_points=ref_points[~inlier_mask],
                total_candidates=n_pts,
                inlier_count=inlier_count,
                outlier_count=outlier_count,
                inlier_ratio=inlier_ratio,
                reprojection_errors=np.empty((0,), dtype=np.float32),
                mean_rmse=float("inf"),
                status_message="Too few geometric inliers (<4) to guarantee physical correspondence."
            )

        # Compute per-inlier reprojection error: || x_ref - H * x_src ||
        inlier_src = src_points[inlier_mask]
        inlier_ref = ref_points[inlier_mask]
        pred_ref = TransformationEstimator.transform_points(inlier_src, H_mat)
        errors = np.sqrt(np.sum((inlier_ref - pred_ref) ** 2, axis=1))
        mean_rmse = float(np.sqrt(np.mean(errors ** 2)))

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
            outlier_count=outlier_count,
            inlier_ratio=inlier_ratio,
            reprojection_errors=errors.astype(np.float32),
            mean_rmse=mean_rmse,
            status_message=f"Verified {inlier_count}/{n_pts} geometric inliers (Ratio: {inlier_ratio*100:.1f}%, RMSE: {mean_rmse:.2f}px)."
        )
