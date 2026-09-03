"""
Multi-Scale Representation & Scale Pyramid Bridge for SIH26166.
Handles multi-resolution processing, octave scale pyramids, and scale-aware feature extraction
to bridge resolution disparities between lunar orbital sensors (e.g. TMC-2 5m/px vs OHRC 0.25m/px).
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Any, Optional


class MultiScaleBridge:
    """Constructs Gaussian multi-resolution representations to bridge cross-sensor scale gaps."""

    def __init__(
        self,
        max_octaves: int = 4,
        scale_step: float = 1.5,
        sigma_blur: float = 1.2
    ):
        self.max_octaves = max_octaves
        self.scale_step = scale_step
        self.sigma_blur = sigma_blur

    def build_pyramid(self, image: np.ndarray, target_scale_ratio: float = 1.0) -> List[Tuple[np.ndarray, float]]:
        r"""
        Builds a multi-scale pyramid of the image with downsampling factor $s \in [1.0, \text{target\_scale\_ratio}]$.
        Returns list of (scaled_image, scale_factor) tuples where scale_factor = width_scaled / width_original.
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        h, w = gray.shape
        pyramid = [(gray, 1.0)]

        if target_scale_ratio <= 1.05:
            return pyramid

        current_img = gray
        current_factor = 1.0

        num_steps = int(np.ceil(np.log(target_scale_ratio) / np.log(self.scale_step)))
        num_steps = min(num_steps, self.max_octaves)

        for step in range(1, num_steps + 1):
            factor = min(target_scale_ratio, self.scale_step ** step)
            new_w = max(32, int(w / factor))
            new_h = max(32, int(h / factor))

            # Anti-aliased resizing
            blurred = cv2.GaussianBlur(current_img, (0, 0), self.sigma_blur)
            downsampled = cv2.resize(blurred, (new_w, new_h), interpolation=cv2.INTER_AREA)

            pyramid.append((downsampled, 1.0 / factor))

        return pyramid

    @staticmethod
    def estimate_scale_ratio(gsd_src_m: Optional[float], gsd_ref_m: Optional[float]) -> float:
        """
        Computes resolution ratio $R = \text{GSD}_{\text{coarse}} / \text{GSD}_{\text{fine}}$.
        """
        if gsd_src_m is None or gsd_ref_m is None or gsd_src_m <= 0 or gsd_ref_m <= 0:
            return 1.0
        return max(gsd_src_m / gsd_ref_m, gsd_ref_m / gsd_src_m)
