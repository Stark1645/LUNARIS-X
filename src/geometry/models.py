"""
Geometric Transformation Models for SIH26166.
Supports Translation, Similarity (rigid + scale), Affine, and Projective Homography models.
Selects models based on imaging geometry and experimental validation.
"""

import cv2
import numpy as np
from enum import Enum
from typing import Tuple, Optional, Dict, Any


class TransformationType(str, Enum):
    TRANSLATION = "TRANSLATION"
    SIMILARITY = "SIMILARITY"
    AFFINE = "AFFINE"
    HOMOGRAPHY = "HOMOGRAPHY"


class TransformationEstimator:
    """Estimates and applies 2D geometric transformation models between image coordinate frames."""

    @staticmethod
    def estimate_model(
        src_points: np.ndarray,
        ref_points: np.ndarray,
        model_type: TransformationType = TransformationType.HOMOGRAPHY
    ) -> Tuple[Optional[np.ndarray], Dict[str, Any]]:
        """
        Estimates the requested transformation matrix mapping src_points -> ref_points.
        Returns 3x3 matrix H such that [x_ref, y_ref, 1]^T ~ H * [x_src, y_src, 1]^T.
        """
        if len(src_points) < 4 and model_type == TransformationType.HOMOGRAPHY:
            return None, {"error": "Homography requires at least 4 points"}
        if len(src_points) < 3 and model_type == TransformationType.AFFINE:
            return None, {"error": "Affine requires at least 3 points"}
        if len(src_points) < 2 and model_type == TransformationType.SIMILARITY:
            return None, {"error": "Similarity requires at least 2 points"}
        if len(src_points) < 1:
            return None, {"error": "Translation requires at least 1 point"}

        H = np.eye(3, dtype=np.float64)

        if model_type == TransformationType.TRANSLATION:
            # Mean translation dx = mean(x_ref - x_src)
            dt = np.mean(ref_points - src_points, axis=0)
            H[0, 2] = float(dt[0])
            H[1, 2] = float(dt[1])

        elif model_type == TransformationType.SIMILARITY:
            # Estimate rigid + uniform scale (partial affine, 4 DOF)
            M, _ = cv2.estimateAffinePartial2D(src_points, ref_points)
            if M is None:
                return None, {"error": "Failed to estimate similarity transform"}
            H[0:2, :] = M

        elif model_type == TransformationType.AFFINE:
            # Full affine (6 DOF: translation, rotation, scale, shear)
            M, _ = cv2.estimateAffine2D(src_points, ref_points)
            if M is None:
                return None, {"error": "Failed to estimate affine transform"}
            H[0:2, :] = M

        elif model_type == TransformationType.HOMOGRAPHY:
            # Projective homography (8 DOF)
            H_mat, _ = cv2.findHomography(src_points, ref_points, method=0)
            if H_mat is None:
                return None, {"error": "Failed to estimate homography matrix"}
            H = H_mat.astype(np.float64)

        return H, {"model_type": model_type.value, "status": "SUCCESS"}

    @staticmethod
    def transform_points(points: np.ndarray, H: np.ndarray) -> np.ndarray:
        """
        Transforms (N, 2) points using 3x3 transformation matrix H.
        x' ~ H * x.
        """
        if len(points) == 0:
            return np.empty((0, 2), dtype=np.float32)

        pts_hom = np.hstack([points, np.ones((len(points), 1), dtype=np.float64)])
        transformed_hom = (H @ pts_hom.T).T

        # Perspective division
        w = transformed_hom[:, 2:3]
        w[np.abs(w) < 1e-10] = 1e-10
        pts_trans = transformed_hom[:, :2] / w

        return pts_trans.astype(np.float32)

    @staticmethod
    def warp_source_to_reference(
        source_image: np.ndarray,
        H: np.ndarray,
        reference_shape: Tuple[int, int],
        interpolation: int = cv2.INTER_LINEAR,
        border_mode: int = cv2.BORDER_CONSTANT,
        border_value: int = 0
    ) -> np.ndarray:
        """
        Warps source (moving) image into the coordinate frame of the reference (fixed) image.
        reference_shape: (height, width).
        """
        h_ref, w_ref = reference_shape[:2]
        warped = cv2.warpPerspective(
            source_image,
            H,
            (w_ref, h_ref),
            flags=interpolation,
            borderMode=border_mode,
            borderValue=border_value
        )
        return warped
