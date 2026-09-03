"""
Sub-Pixel Parabolic Surface Refinement Module for SIH26166.
Performs 2D continuous parabolic / quadratic Taylor expansion on the local correlation surface
to localize tie-points with genuine fractional-pixel displacement precision.
"""

import cv2
import numpy as np
from typing import Tuple, List, Dict, Any, Optional


class SubPixelRefiner:
    """Localizes integer tie-point correspondences to continuous sub-pixel coordinates."""

    def __init__(
        self,
        patch_radius: int = 7,  # (2*7+1) = 15x15 template patch
        search_radius: int = 3,  # Local search window
        max_displacement: float = 1.0
    ):
        self.patch_radius = patch_radius
        self.search_radius = search_radius
        self.max_displacement = max_displacement

    def refine_points(
        self,
        src_image: np.ndarray,
        ref_image: np.ndarray,
        src_points: np.ndarray,
        ref_points: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Refines reference tie-point coordinates to continuous sub-pixel coordinates.
        Returns:
            refined_ref_points: (N, 2) float32 coordinates.
            displacements: (N, 2) sub-pixel delta offsets.
            stats: Summary of sub-pixel adjustments.
        """
        if len(src_image.shape) == 3:
            src_gray = cv2.cvtColor(src_image, cv2.COLOR_BGR2GRAY)
        else:
            src_gray = src_image

        if len(ref_image.shape) == 3:
            ref_gray = cv2.cvtColor(ref_image, cv2.COLOR_BGR2GRAY)
        else:
            ref_gray = ref_image

        h_src, w_src = src_gray.shape
        h_ref, w_ref = ref_gray.shape
        n_pts = len(src_points)

        refined_ref = ref_points.copy()
        displacements = np.zeros((n_pts, 2), dtype=np.float32)
        success_count = 0

        r = self.patch_radius
        s = self.search_radius

        for i in range(n_pts):
            xs, ys = int(round(src_points[i, 0])), int(round(src_points[i, 1]))
            xr, yr = int(round(ref_points[i, 0])), int(round(ref_points[i, 1]))

            # Check boundary margins
            if (xs - r < 0 or xs + r >= w_src or ys - r < 0 or ys + r >= h_src or
                xr - (r + s) < 0 or xr + (r + s) >= w_ref or yr - (r + s) < 0 or yr + (r + s) >= h_ref):
                continue

            # Template from source image
            template = src_gray[ys - r:ys + r + 1, xs - r:xs + r + 1].astype(np.float32)

            # Search window from reference image
            search_window = ref_gray[yr - (r + s):yr + (r + s) + 1, xr - (r + s):xr + (r + s) + 1].astype(np.float32)

            # Compute local Normalized Cross-Correlation (NCC)
            corr_map = cv2.matchTemplate(search_window, template, cv2.TM_CCOEFF_NORMED)

            # Find integer peak in correlation map
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(corr_map)
            pk_x, pk_y = max_loc

            # Check if 3x3 neighborhood around peak exists
            if (1 <= pk_x < corr_map.shape[1] - 1 and 1 <= pk_y < corr_map.shape[0] - 1):
                # 3x3 correlation patch around integer peak
                patch = corr_map[pk_y - 1:pk_y + 2, pk_x - 1:pk_x + 2].astype(np.float64)

                # Analytical gradients and Hessian on 3x3 grid
                # g = [dC/dx, dC/dy]
                gx = (patch[1, 2] - patch[1, 0]) / 2.0
                gy = (patch[2, 1] - patch[0, 1]) / 2.0

                # Hessian H = [[d2C/dx2, d2C/dxdy], [d2C/dxdy, d2C/dy2]]
                hxx = patch[1, 2] - 2.0 * patch[1, 1] + patch[1, 0]
                hyy = patch[2, 1] - 2.0 * patch[1, 1] + patch[0, 1]
                hxy = (patch[2, 2] - patch[2, 0] - patch[0, 2] + patch[0, 0]) / 4.0

                det_h = hxx * hyy - hxy ** 2

                # Valid peak must be concave (negative eigenvalues)
                if abs(det_h) > 1e-6 and hxx < 0 and hyy < 0:
                    # delta = - H^-1 * g
                    dx_sub = - (hyy * gx - hxy * gy) / det_h
                    dy_sub = - (hxx * gy - hxy * gx) / det_h

                    if abs(dx_sub) <= self.max_displacement and abs(dy_sub) <= self.max_displacement:
                        # Offset relative to initial reference coordinate
                        dx_total = (pk_x - s) + dx_sub
                        dy_total = (pk_y - s) + dy_sub

                        refined_ref[i, 0] = xr + dx_total
                        refined_ref[i, 1] = yr + dy_total
                        displacements[i, 0] = float(dx_total)
                        displacements[i, 1] = float(dy_total)
                        success_count += 1

        disp_mags = np.sqrt(np.sum(displacements ** 2, axis=1))
        stats = {
            "total_points": n_pts,
            "refined_points_count": success_count,
            "success_rate": float(success_count / n_pts) if n_pts > 0 else 0.0,
            "mean_subpixel_displacement": float(np.mean(disp_mags)),
            "max_subpixel_displacement": float(np.max(disp_mags)) if n_pts > 0 else 0.0
        }

        return refined_ref.astype(np.float32), displacements, stats
