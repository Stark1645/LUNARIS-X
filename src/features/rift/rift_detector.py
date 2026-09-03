"""
RIFT (Radiation-Invariant Feature Transform) Feature Detector Baseline (SIH26166 Baseline B).
Extracts phase-congruency structural keypoints and Log-Gabor Maximum Index Map (MIM) descriptors
for illumination-robust correspondence under extreme sun azimuth shifts.
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional, Dict, Any
from src.features.base import BaseFeatureDetector
from src.features.rift.log_gabor import LogGaborFilterBank


class RIFTDetector(BaseFeatureDetector):
    """
    Evaluated Illumination-Robust Baseline using Log-Gabor Phase Congruency and Maximum Index Maps (MIM).
    """

    def __init__(
        self,
        nfeatures: int = 2000,
        patch_size: int = 48,
        n_scales: int = 4,
        n_orientations: int = 6,
        n_spatial_bins: int = 6  # 6x6 spatial sub-regions -> descriptor dimension = 6 * 36 = 216
    ):
        super().__init__(name="RIFT_Baseline", params={
            "nfeatures": nfeatures,
            "patch_size": patch_size,
            "n_scales": n_scales,
            "n_orientations": n_orientations,
            "n_spatial_bins": n_spatial_bins
        })
        self.nfeatures = nfeatures
        self.patch_size = patch_size
        self.n_orientations = n_orientations
        self.n_spatial_bins = n_spatial_bins
        self.filter_bank = LogGaborFilterBank(
            n_scales=n_scales,
            n_orientations=n_orientations
        )

    def detect_and_compute(
        self,
        image: np.ndarray,
        mask: Optional[np.ndarray] = None
    ) -> Tuple[List[cv2.KeyPoint], np.ndarray]:
        """
        Computes Phase Congruency, extracts FAST/Harris keypoints on the PC map,
        and constructs local Maximum Index Map (MIM) orientation histogram descriptors.
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        h, w = gray.shape

        # 1. Compute Phase Congruency and Maximum Index Map (MIM)
        pc_map, mim_map, _ = self.filter_bank.compute_phase_congruency(gray)

        # Scale PC map to 8-bit for OpenCV corner detection
        pc_u8 = (pc_map * 255.0).astype(np.uint8)

        # 2. Keypoint Detection on Phase Congruency map (features reflect true physical morphology)
        # Combine FAST corner detector with Shi-Tomasi GoodFeaturesToTrack on PC
        fast = cv2.FastFeatureDetector_create(threshold=15, nonmaxSuppression=True)
        detected = fast.detect(pc_u8, mask=mask)
        raw_kps = list(detected) if detected is not None else []

        # Fallback if FAST detects too few points in low-contrast scenes
        if len(raw_kps) < self.nfeatures // 4:
            corners = cv2.goodFeaturesToTrack(
                pc_u8,
                maxCorners=self.nfeatures,
                qualityLevel=0.01,
                minDistance=6,
                mask=mask
            )
            if corners is not None:
                gftt_kps = [cv2.KeyPoint(x=float(pt[0][0]), y=float(pt[0][1]), size=16.0) for pt in corners]
                raw_kps.extend(gftt_kps)

        if not raw_kps:
            return [], np.empty((0, self.n_spatial_bins * self.n_spatial_bins * self.n_orientations), dtype=np.float32)

        # Sort by response and keep top nfeatures
        raw_kps.sort(key=lambda kp: kp.response, reverse=True)
        raw_kps = raw_kps[:self.nfeatures]

        # 3. Descriptor Extraction from Maximum Index Map (MIM)
        half_w = self.patch_size // 2
        valid_kps = []
        desc_list = []

        descriptor_dim = self.n_spatial_bins * self.n_spatial_bins * self.n_orientations

        for kp in raw_kps:
            x, y = int(round(kp.pt[0])), int(round(kp.pt[1]))

            # Ensure patch is completely within image bounds
            if x - half_w < 0 or x + half_w >= w or y - half_w < 0 or y + half_w >= h:
                continue

            patch_mim = mim_map[y - half_w:y + half_w, x - half_w:x + half_w]

            # Partition patch into (n_spatial_bins x n_spatial_bins) sub-cells
            cell_size = self.patch_size // self.n_spatial_bins
            desc_vec = np.zeros(descriptor_dim, dtype=np.float32)

            for by in range(self.n_spatial_bins):
                for bx in range(self.n_spatial_bins):
                    cell = patch_mim[by * cell_size:(by + 1) * cell_size, bx * cell_size:(bx + 1) * cell_size]
                    counts = np.bincount(cell.flatten(), minlength=self.n_orientations)[:self.n_orientations]
                    start_idx = (by * self.n_spatial_bins + bx) * self.n_orientations
                    desc_vec[start_idx:start_idx + self.n_orientations] = counts

            # L2 Normalization with clipping (SIFT-like robust normalization)
            norm = np.linalg.norm(desc_vec) + 1e-6
            desc_vec /= norm
            desc_vec = np.clip(desc_vec, 0.0, 0.2)
            desc_vec /= (np.linalg.norm(desc_vec) + 1e-6)

            valid_kps.append(kp)
            desc_list.append(desc_vec)

        if not desc_list:
            return [], np.empty((0, descriptor_dim), dtype=np.float32)

        descriptors = np.array(desc_list, dtype=np.float32)
        return valid_kps, descriptors
