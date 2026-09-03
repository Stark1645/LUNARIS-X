"""
Illumination-Robust Structural Feature Detector (Innovation C in Proposed Method).
Combines Multi-Scale Log-Gabor Phase Congruency, Shadow-Boundary Edge Suppression,
and Structural Orientation Histogram Descriptors.
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional, Dict, Any

from src.features.base import BaseFeatureDetector
from src.features.rift.log_gabor import LogGaborFilterBank


class StructuralFeatureDetector(BaseFeatureDetector):
    """
    Enhanced Structural Feature Detector specifically designed for extreme illumination
    and shadow-inversion invariance on lunar terrain.
    """

    def __init__(
        self,
        nfeatures: int = 2500,
        patch_size: int = 48,
        n_scales: int = 4,
        n_orientations: int = 6,
        n_spatial_bins: int = 6,
        suppress_shadow_edges: bool = True
    ):
        super().__init__(name="Proposed_Structural_Detector", params={
            "nfeatures": nfeatures,
            "patch_size": patch_size,
            "n_scales": n_scales,
            "n_orientations": n_orientations,
            "n_spatial_bins": n_spatial_bins,
            "suppress_shadow_edges": suppress_shadow_edges
        })
        self.nfeatures = nfeatures
        self.patch_size = patch_size
        self.n_orientations = n_orientations
        self.n_spatial_bins = n_spatial_bins
        self.suppress_shadow_edges = suppress_shadow_edges
        self.filter_bank = LogGaborFilterBank(n_scales=n_scales, n_orientations=n_orientations)

    def detect_and_compute(
        self,
        image: np.ndarray,
        mask: Optional[np.ndarray] = None
    ) -> Tuple[List[cv2.KeyPoint], np.ndarray]:
        """
        Extracts structural keypoints and illumination-invariant MIM descriptors.
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        h, w = gray.shape

        # 1. Compute Phase Congruency and Maximum Index Map
        pc_map, mim_map, total_energy = self.filter_bank.compute_phase_congruency(gray)

        # 2. Shadow-Boundary Suppression:
        # Extreme cast shadows produce sharp step edges on flat regolith (non-morphological).
        # We compute local variance of phase congruency to suppress non-stationary shadow edges.
        if self.suppress_shadow_edges:
            # Harsh binary shadow detection
            _, dark_mask = cv2.threshold(gray, 25, 255, cv2.THRESH_BINARY_INV)
            dilated_shadow = cv2.dilate(dark_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
            # Attenuate PC along harsh cast shadow borders while preserving crater rim topography
            pc_map[dilated_shadow == 255] *= 0.6

        pc_u8 = (pc_map * 255.0).astype(np.uint8)

        # 3. Keypoint Detection: Multi-scale Shi-Tomasi on Phase Congruency map
        corners = cv2.goodFeaturesToTrack(
            pc_u8,
            maxCorners=self.nfeatures,
            qualityLevel=0.005,
            minDistance=5,
            mask=mask
        )

        raw_kps = []
        if corners is not None:
            raw_kps = [cv2.KeyPoint(x=float(pt[0][0]), y=float(pt[0][1]), size=16.0) for pt in corners]

        # Augment with FAST on high-energy structural regions
        fast = cv2.FastFeatureDetector_create(threshold=12, nonmaxSuppression=True)
        detected_fast = fast.detect(pc_u8, mask=mask)
        if detected_fast is not None:
            raw_kps.extend(list(detected_fast))

        if not raw_kps:
            return [], np.empty((0, self.n_spatial_bins * self.n_spatial_bins * self.n_orientations), dtype=np.float32)

        # Sort and limit
        raw_kps.sort(key=lambda kp: kp.response if kp.response > 0 else 1.0, reverse=True)
        raw_kps = raw_kps[:self.nfeatures]

        # 4. Descriptor Extraction from MIM map
        half_w = self.patch_size // 2
        valid_kps = []
        desc_list = []
        descriptor_dim = self.n_spatial_bins * self.n_spatial_bins * self.n_orientations
        cell_size = self.patch_size // self.n_spatial_bins

        for kp in raw_kps:
            x, y = int(round(kp.pt[0])), int(round(kp.pt[1]))
            if x - half_w < 0 or x + half_w >= w or y - half_w < 0 or y + half_w >= h:
                continue

            patch_mim = mim_map[y - half_w:y + half_w, x - half_w:x + half_w]
            desc_vec = np.zeros(descriptor_dim, dtype=np.float32)

            for by in range(self.n_spatial_bins):
                for bx in range(self.n_spatial_bins):
                    cell = patch_mim[by * cell_size:(by + 1) * cell_size, bx * cell_size:(bx + 1) * cell_size]
                    counts = np.bincount(cell.flatten(), minlength=self.n_orientations)[:self.n_orientations]
                    start_idx = (by * self.n_spatial_bins + bx) * self.n_orientations
                    desc_vec[start_idx:start_idx + self.n_orientations] = counts

            # L2 Normalization with clipping
            norm = np.linalg.norm(desc_vec) + 1e-6
            desc_vec /= norm
            desc_vec = np.clip(desc_vec, 0.0, 0.2)
            desc_vec /= (np.linalg.norm(desc_vec) + 1e-6)

            valid_kps.append(kp)
            desc_list.append(desc_vec)

        if not desc_list:
            return [], np.empty((0, descriptor_dim), dtype=np.float32)

        return valid_kps, np.array(desc_list, dtype=np.float32)
