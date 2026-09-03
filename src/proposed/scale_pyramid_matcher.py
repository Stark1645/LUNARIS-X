"""
Hierarchical Multi-Scale Pyramid Scale Bridge (Innovation B in Proposed Method).
Bridges large orbital resolution disparities (4x, 16x, 20x+ between TMC-2 and OHRC)
via coarse-to-fine Gaussian scale pyramid matching and coordinate propagation.
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional, Dict, Any

from src.features.base import BaseFeatureDetector
from src.matching.matcher import FeatureMatcher, MatchResult


class HierarchicalScalePyramidMatcher:
    """Bridges cross-sensor scale gaps by aligning resolution levels before descriptor matching."""

    def __init__(
        self,
        detector: BaseFeatureDetector,
        ratio_threshold: float = 0.80,
        max_octaves: int = 4
    ):
        self.detector = detector
        self.matcher = FeatureMatcher(ratio_threshold=ratio_threshold, cross_check=True)
        self.max_octaves = max_octaves

    def match_scale_disparate_pair(
        self,
        source_image: np.ndarray,
        reference_image: np.ndarray,
        estimated_scale_ratio: float = 1.0
    ) -> MatchResult:
        """
        Registers image pair across scale gaps.
        If reference is higher resolution than source (e.g., OHRC vs TMC-2),
        downsamples reference to source resolution, matches at matching scale,
        then projects reference coordinates back to native resolution.
        """
        h_s, w_s = source_image.shape[:2]
        h_r, w_r = reference_image.shape[:2]

        # Determine direction of scale disparity
        if w_r > w_s * 1.5:
            # Reference is high-res (e.g. OHRC 1024x1024), Source is low-res (e.g. TMC-2 256x256 or 64x64)
            scale_factor = float(w_r) / float(w_s)
            ref_down = cv2.resize(reference_image, (w_s, h_s), interpolation=cv2.INTER_AREA)

            # Detect & match at common resolution
            kps_src, desc_src = self.detector.detect_and_compute(source_image)
            kps_ref_down, desc_ref_down = self.detector.detect_and_compute(ref_down)

            res_down = self.matcher.match(kps_src, desc_src, kps_ref_down, desc_ref_down)

            if res_down.filtered_matches_count == 0:
                return res_down

            # Project reference coordinates back to full resolution: x_ref_full = x_ref_down * scale_factor
            pts_ref_full = (res_down.reference_points * scale_factor).astype(np.float32)

            return MatchResult(
                source_points=res_down.source_points,
                reference_points=pts_ref_full,
                distances=res_down.distances,
                confidence=res_down.confidence,
                raw_matches_count=res_down.raw_matches_count,
                filtered_matches_count=res_down.filtered_matches_count
            )

        elif w_s > w_r * 1.5:
            # Source is high-res, Reference is low-res
            scale_factor = float(w_s) / float(w_r)
            src_down = cv2.resize(source_image, (w_r, h_r), interpolation=cv2.INTER_AREA)

            kps_src_down, desc_src_down = self.detector.detect_and_compute(src_down)
            kps_ref, desc_ref = self.detector.detect_and_compute(reference_image)

            res_down = self.matcher.match(kps_src_down, desc_src_down, kps_ref, desc_ref)

            if res_down.filtered_matches_count == 0:
                return res_down

            pts_src_full = (res_down.source_points * scale_factor).astype(np.float32)

            return MatchResult(
                source_points=pts_src_full,
                reference_points=res_down.reference_points,
                distances=res_down.distances,
                confidence=res_down.confidence,
                raw_matches_count=res_down.raw_matches_count,
                filtered_matches_count=res_down.filtered_matches_count
            )

        else:
            # Standard 1:1 scale matching
            kps_src, desc_src = self.detector.detect_and_compute(source_image)
            kps_ref, desc_ref = self.detector.detect_and_compute(reference_image)
            return self.matcher.match(kps_src, desc_src, kps_ref, desc_ref)
