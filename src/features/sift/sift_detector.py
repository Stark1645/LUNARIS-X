"""
Classical SIFT Feature Detector Baseline (SIH26166 Classical Baseline A).
Extracts scale-space extrema from Difference-of-Gaussians (DoG) with 128-dimensional gradient orientation descriptors.
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional, Dict, Any
from src.features.base import BaseFeatureDetector


class SIFTDetector(BaseFeatureDetector):
    """Classical SIFT (Scale-Invariant Feature Transform) baseline implementation."""

    def __init__(
        self,
        nfeatures: int = 2000,
        nOctaveLayers: int = 3,
        contrastThreshold: float = 0.04,
        edgeThreshold: float = 10.0,
        sigma: float = 1.6
    ):
        super().__init__(name="SIFT_Baseline", params={
            "nfeatures": nfeatures,
            "nOctaveLayers": nOctaveLayers,
            "contrastThreshold": contrastThreshold,
            "edgeThreshold": edgeThreshold,
            "sigma": sigma
        })
        self.sift = cv2.SIFT_create(
            nfeatures=nfeatures,
            nOctaveLayers=nOctaveLayers,
            contrastThreshold=contrastThreshold,
            edgeThreshold=edgeThreshold,
            sigma=sigma
        )

    def detect_and_compute(
        self,
        image: np.ndarray,
        mask: Optional[np.ndarray] = None
    ) -> Tuple[List[cv2.KeyPoint], np.ndarray]:
        """
        Detects SIFT keypoints and extracts 128-d L2-normalized gradient descriptors.
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        keypoints, descriptors = self.sift.detectAndCompute(gray, mask)

        if keypoints is None or len(keypoints) == 0:
            return [], np.empty((0, 128), dtype=np.float32)

        if descriptors is None:
            descriptors = np.empty((0, 128), dtype=np.float32)

        return list(keypoints), descriptors.astype(np.float32)
