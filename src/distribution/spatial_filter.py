"""
Spatial Distribution Control & Keypoint Gini Filter for SIH26166.
Enforces uniform spatial coverage of geometrically verified inliers across the image canvas,
preventing match clustering on high-contrast crater rims without manufacturing false correspondences.
"""

import numpy as np
from typing import Tuple, Dict, Any, Optional, List


class SpatialDistributionFilter:
    """Selects reliable inlier correspondences to optimize spatial coverage and dispersion."""

    def __init__(
        self,
        grid_size: int = 4,  # 4x4 spatial binning
        max_points_per_bin: int = 25,
        min_points_per_bin: int = 1
    ):
        self.grid_size = grid_size
        self.max_points_per_bin = max_points_per_bin
        self.min_points_per_bin = min_points_per_bin

    @staticmethod
    def compute_gini_coefficient(points: np.ndarray, image_shape: Tuple[int, int], grid_size: int = 4) -> float:
        r"""
        Computes spatial Gini coefficient $G_k \in [0, 1]$ across an $M \times M$ grid.
        $G_k \to 0$: Uniform point distribution.
        $G_k \to 1$: Severe spatial clumping on a single cluster/crater.
        """
        if len(points) == 0:
            return 1.0

        h, w = image_shape[:2]
        bin_h = max(1, h // grid_size)
        bin_w = max(1, w // grid_size)

        counts = np.zeros((grid_size, grid_size), dtype=np.float64)

        for pt in points:
            bx = min(grid_size - 1, max(0, int(pt[0] // bin_w)))
            by = min(grid_size - 1, max(0, int(pt[1] // bin_h)))
            counts[by, bx] += 1.0

        flat = counts.flatten()
        k = len(flat)
        total_pts = np.sum(flat)

        if total_pts == 0:
            return 1.0

        # Mean absolute differences
        diff_matrix = np.abs(flat[:, None] - flat[None, :])
        gini = np.sum(diff_matrix) / (2.0 * k * total_pts)
        return float(np.clip(gini, 0.0, 1.0))

    def filter_inliers(
        self,
        src_inliers: np.ndarray,
        ref_inliers: np.ndarray,
        image_shape: Tuple[int, int],
        confidences: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Selects verified inliers using spatial grid binning to improve spatial dispersion.
        Never creates artificial matches; only retains the most confident inliers per spatial bin.
        """
        n_inliers = len(src_inliers)
        if n_inliers <= self.max_points_per_bin * (self.grid_size ** 2):
            # Compute initial Gini
            initial_gini = self.compute_gini_coefficient(src_inliers, image_shape, self.grid_size)
            return src_inliers, ref_inliers, {
                "initial_gini": initial_gini,
                "filtered_gini": initial_gini,
                "initial_count": n_inliers,
                "filtered_count": n_inliers,
                "occupied_bins": self._count_occupied_bins(src_inliers, image_shape)
            }

        h, w = image_shape[:2]
        bin_h = max(1, h // self.grid_size)
        bin_w = max(1, w // self.grid_size)

        initial_gini = self.compute_gini_coefficient(src_inliers, image_shape, self.grid_size)

        # Organize points into bins
        bins: Dict[Tuple[int, int], List[int]] = {}
        for idx in range(n_inliers):
            pt = src_inliers[idx]
            bx = min(self.grid_size - 1, max(0, int(pt[0] // bin_w)))
            by = min(self.grid_size - 1, max(0, int(pt[1] // bin_h)))
            key = (by, bx)
            if key not in bins:
                bins[key] = []
            bins[key].append(idx)

        selected_indices = []
        for key, indices in bins.items():
            if len(indices) <= self.max_points_per_bin:
                selected_indices.extend(indices)
            else:
                # Sort by confidence if provided, otherwise uniform subsampling
                if confidences is not None:
                    sorted_idxs = sorted(indices, key=lambda i: confidences[i], reverse=True)
                else:
                    # Deterministic spaced selection
                    step = len(indices) / float(self.max_points_per_bin)
                    sorted_idxs = [indices[int(i * step)] for i in range(self.max_points_per_bin)]
                selected_indices.extend(sorted_idxs[:self.max_points_per_bin])

        selected_indices = sorted(selected_indices)
        filtered_src = src_inliers[selected_indices]
        filtered_ref = ref_inliers[selected_indices]

        filtered_gini = self.compute_gini_coefficient(filtered_src, image_shape, self.grid_size)

        # Compute objective spatial quality status
        bin_ratio = float(len(bins) / (self.grid_size ** 2))
        if bin_ratio >= 0.75 and filtered_gini <= 0.35:
            quality = "GOOD"
        elif bin_ratio >= 0.50 and filtered_gini <= 0.60:
            quality = "ACCEPTABLE"
        else:
            quality = "POOR"

        stats = {
            "initial_gini": initial_gini,
            "filtered_gini": filtered_gini,
            "initial_count": n_inliers,
            "filtered_count": len(filtered_src),
            "occupied_bins": len(bins),
            "total_bins": self.grid_size ** 2,
            "bin_occupancy_ratio": bin_ratio,
            "spatial_quality_status": quality
        }

        return filtered_src, filtered_ref, stats

    def _count_occupied_bins(self, points: np.ndarray, image_shape: Tuple[int, int]) -> int:
        if len(points) == 0:
            return 0
        h, w = image_shape[:2]
        bin_h = max(1, h // self.grid_size)
        bin_w = max(1, w // self.grid_size)
        occupied = set()
        for pt in points:
            bx = min(self.grid_size - 1, max(0, int(pt[0] // bin_w)))
            by = min(self.grid_size - 1, max(0, int(pt[1] // bin_h)))
            occupied.add((by, bx))
        return len(occupied)
