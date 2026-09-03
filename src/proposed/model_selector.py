"""
Transformation Model Selector (Innovation E in Proposed Method).
Dynamically selects between Translation, Similarity, Affine, and Projective Homography
based on correspondence count, spatial dispersion Gini G_k, and geometric condition number.
"""

import numpy as np
from typing import Tuple, Dict, Any, Optional

from src.geometry.models import TransformationType, TransformationEstimator
from src.distribution.spatial_filter import SpatialDistributionFilter


class DynamicModelSelector:
    """Selects the mathematically appropriate transformation model to prevent minimal sample overfitting."""

    @staticmethod
    def select_and_estimate(
        src_points: np.ndarray,
        ref_points: np.ndarray,
        image_shape: Tuple[int, int],
        force_model: Optional[TransformationType] = None
    ) -> Tuple[np.ndarray, TransformationType, Dict[str, Any]]:
        """
        Selects model based on inlier count and spatial Gini dispersion.
        """
        n_pts = len(src_points)
        if n_pts == 0:
            return np.eye(3, dtype=np.float64), TransformationType.TRANSLATION, {"status": "EMPTY"}

        if force_model is not None:
            H, stats = TransformationEstimator.estimate_model(src_points, ref_points, force_model)
            if H is not None:
                return H, force_model, stats

        # Compute spatial Gini dispersion
        gini = SpatialDistributionFilter.compute_gini_coefficient(src_points, image_shape, grid_size=4)

        # Decision logic based on Phase 3 failure evidence:
        # 1. If points are few (4 <= N < 6) or clustered on a single rim (Gini > 0.65),
        # full 8-DOF Homography will overfit and cause massive distortion (RMSE_GT > 300px).
        # We fall back to 6-DOF Affine or 4-DOF Similarity to maintain planar stability!
        if n_pts < 4:
            selected_model = TransformationType.TRANSLATION
        elif n_pts < 8 or gini > 0.65:
            # Robust Affine model (6 DOF)
            selected_model = TransformationType.AFFINE
        else:
            # Well-distributed inliers -> Full Projective Homography (8 DOF)
            selected_model = TransformationType.HOMOGRAPHY

        H_est, stats = TransformationEstimator.estimate_model(src_points, ref_points, selected_model)
        if H_est is None:
            # Fallback to Affine then Similarity
            selected_model = TransformationType.AFFINE
            H_est, stats = TransformationEstimator.estimate_model(src_points, ref_points, selected_model)
            if H_est is None:
                selected_model = TransformationType.SIMILARITY
                H_est, stats = TransformationEstimator.estimate_model(src_points, ref_points, selected_model)
                if H_est is None:
                    H_est = np.eye(3, dtype=np.float64)
                    selected_model = TransformationType.TRANSLATION

        stats["selected_model"] = selected_model.value
        stats["spatial_gini"] = gini
        stats["inlier_count"] = n_pts

        return H_est, selected_model, stats
