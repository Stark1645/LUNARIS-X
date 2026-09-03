"""
Feature Matching & Filtering Module for SIH26166.
Implements Nearest-Neighbor matching, Lowe's ratio test, mutual consistency check,
and structured match candidate creation.
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class MatchResult:
    """Encapsulates raw and filtered candidate matches."""
    source_points: np.ndarray  # (N, 2) [x, y] in source (moving) image
    reference_points: np.ndarray  # (N, 2) [x, y] in reference (fixed) image
    distances: np.ndarray  # (N,) match distances
    confidence: np.ndarray  # (N,) confidence scores in [0, 1]
    raw_matches_count: int
    filtered_matches_count: int


class FeatureMatcher:
    """Robust feature matcher with ratio test and cross-check filtering."""

    def __init__(
        self,
        ratio_threshold: float = 0.80,
        cross_check: bool = True,
        distance_metric: int = cv2.NORM_L2
    ):
        self.ratio_threshold = ratio_threshold
        self.cross_check = cross_check
        self.distance_metric = distance_metric

    def match(
        self,
        keypoints_src: List[cv2.KeyPoint],
        descriptors_src: np.ndarray,
        keypoints_ref: List[cv2.KeyPoint],
        descriptors_ref: np.ndarray
    ) -> MatchResult:
        """
        Matches source (moving) descriptors against reference (fixed) descriptors.
        Applies Lowe's ratio test and optional mutual cross-check.
        """
        if (
            descriptors_src is None or len(descriptors_src) < 2 or
            descriptors_ref is None or len(descriptors_ref) < 2
        ):
            return MatchResult(
                source_points=np.empty((0, 2), dtype=np.float32),
                reference_points=np.empty((0, 2), dtype=np.float32),
                distances=np.empty((0,), dtype=np.float32),
                confidence=np.empty((0,), dtype=np.float32),
                raw_matches_count=0,
                filtered_matches_count=0
            )

        bf = cv2.BFMatcher(self.distance_metric, crossCheck=False)

        # 1. k-NN matching (k=2) for Lowe's ratio test
        matches_src_to_ref = bf.knnMatch(descriptors_src, descriptors_ref, k=2)

        good_matches = []
        for m_tuple in matches_src_to_ref:
            if len(m_tuple) == 2:
                m, n = m_tuple
                if m.distance < self.ratio_threshold * n.distance:
                    good_matches.append(m)
            elif len(m_tuple) == 1:
                good_matches.append(m_tuple[0])

        raw_count = len(good_matches)

        # 2. Mutual Cross-Check Consistency (if enabled)
        if self.cross_check and len(good_matches) > 0:
            matches_ref_to_src = bf.knnMatch(descriptors_ref, descriptors_src, k=2)
            ref_best_match = {}
            for m_tuple in matches_ref_to_src:
                if len(m_tuple) >= 1:
                    m = m_tuple[0]
                    # m.queryIdx is in ref, m.trainIdx is in src
                    ref_best_match[m.queryIdx] = m.trainIdx

            mutual_matches = []
            for m in good_matches:
                # m.queryIdx is src, m.trainIdx is ref
                if ref_best_match.get(m.trainIdx) == m.queryIdx:
                    mutual_matches.append(m)

            good_matches = mutual_matches

        if not good_matches:
            return MatchResult(
                source_points=np.empty((0, 2), dtype=np.float32),
                reference_points=np.empty((0, 2), dtype=np.float32),
                distances=np.empty((0,), dtype=np.float32),
                confidence=np.empty((0,), dtype=np.float32),
                raw_matches_count=raw_count,
                filtered_matches_count=0
            )

        # Extract (x, y) coordinates
        pts_src = np.array([keypoints_src[m.queryIdx].pt for m in good_matches], dtype=np.float32)
        pts_ref = np.array([keypoints_ref[m.trainIdx].pt for m in good_matches], dtype=np.float32)
        dists = np.array([m.distance for m in good_matches], dtype=np.float32)

        # Confidence: inverted normalized distance
        max_dist = dists.max() if dists.max() > 0 else 1.0
        conf = np.clip(1.0 - (dists / max_dist), 0.0, 1.0)

        return MatchResult(
            source_points=pts_src,
            reference_points=pts_ref,
            distances=dists,
            confidence=conf,
            raw_matches_count=raw_count,
            filtered_matches_count=len(good_matches)
        )
