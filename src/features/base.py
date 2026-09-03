"""
Abstract Base Class for Feature Detection & Description in SIH26166.
Ensures interchangeable algorithms (SIFT baseline, RIFT baseline, and future proposed methods).
"""

from abc import ABC, abstractmethod
from typing import Tuple, List, Dict, Any, Optional
import numpy as np
import cv2


class BaseFeatureDetector(ABC):
    """Abstract base class for all feature detectors and descriptors."""

    def __init__(self, name: str, params: Optional[Dict[str, Any]] = None):
        self.name = name
        self.params = params or {}

    @abstractmethod
    def detect_and_compute(
        self,
        image: np.ndarray,
        mask: Optional[np.ndarray] = None
    ) -> Tuple[List[cv2.KeyPoint], np.ndarray]:
        """
        Detects keypoints and extracts descriptor vectors.
        Returns:
            keypoints: List of cv2.KeyPoint objects (pt=(x, y), size, angle, response, octave).
            descriptors: np.ndarray of shape (N, D) containing feature vectors.
        """
        pass

    @staticmethod
    def keypoints_to_array(keypoints: List[cv2.KeyPoint]) -> np.ndarray:
        """Converts list of cv2.KeyPoint to (N, 2) float32 coordinates [x, y]."""
        if not keypoints:
            return np.empty((0, 2), dtype=np.float32)
        return np.array([kp.pt for kp in keypoints], dtype=np.float32)

    @staticmethod
    def array_to_keypoints(points: np.ndarray, size: float = 10.0) -> List[cv2.KeyPoint]:
        """Converts (N, 2) numpy array of [x, y] to list of cv2.KeyPoint."""
        if points is None or len(points) == 0:
            return []
        return [cv2.KeyPoint(x=float(pt[0]), y=float(pt[1]), size=size) for pt in points]
